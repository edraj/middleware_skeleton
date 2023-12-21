from pydantic import BaseModel, Field, ValidationInfo, field_validator
from api.schemas.response import ApiException, Error
from models.base.enums import Language, OTPFor, OperatingSystems
from models.otp import Otp
from utils import regex
from utils.helpers import special_to_underscore


class RegisterRequest(BaseModel):
    first_name: str = Field(pattern=regex.NAME)
    last_name: str = Field(pattern=regex.NAME)
    email_otp: str | None = None
    email: str = Field(pattern=regex.EMAIL)
    mobile_otp: str | None = None
    mobile: str = Field(pattern=regex.MSISDN)
    password_confirmation: str = Field(pattern=regex.PASSWORD)
    password: str = Field(pattern=regex.PASSWORD)
    profile_pic_url: str = Field(default=None, pattern=regex.URL)
    promo_code: str = Field(default=None)
    friend_invitation: str = Field(default=None)
    firebase_token: str | None = None
    os: OperatingSystems | None = None
    language: Language | None = None
    is_email_verified: bool = False
    is_mobile_verified: bool = False

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "first_name": "John",
                    "last_name": "Doo",
                    "mobile": "7999228903",
                    "mobile_otp": "112132",
                    "email": "myname@gmail.com",
                    "email_otp": "112132",
                    "password": "test1234",
                    "password_confirmation": "test1234",
                    "profile_pic_url": "https://pics.com/myname.png",
                    "friend_invitation": "xff4fdkfisjsk",
                    "promo_code": "j42l343kj4",
                    "language": "en",
                }
            ]
        }
    }

    @field_validator("email")
    @classmethod
    def email_otp_exists(cls, v: str, info: ValidationInfo) -> str:
        if not info.data.get("email_otp"):
            raise ValueError("email_otp is required with email")
        return v

    @field_validator("mobile")
    @classmethod
    def mobile_otp_exists(cls, v: str, info: ValidationInfo) -> str:
        if not info.data.get("mobile_otp"):
            raise ValueError("mobile_otp is required with mobile")

        return v

    @field_validator("password")
    @classmethod
    def password_confirmed(cls, v: str, info: ValidationInfo) -> str:
        assert v == info.data.get("password_confirmation")
        return v

    async def validate_otps(self) -> None:
        mail_otp_found = False

        if self.email:
            mail_otp_model = Otp(
                user_shortname=special_to_underscore(self.email),
                otp=self.email_otp,
                otp_for=OTPFor.mail_verification,
            )

            print(mail_otp_model.get_key())
            print(await mail_otp_model.get())
            if await mail_otp_model.get() is None:
                self.is_email_verified = False
                raise ApiException(
                    status_code=404,
                    error=Error(
                        type="Invalid request", code=307, message="Invalid Email OTP"
                    ),
                )
            mail_otp_found = True
            self.is_email_verified = True

        if self.mobile:
            otp_model = Otp(
                user_shortname=self.mobile,
                otp=self.mobile_otp,
                otp_for=OTPFor.mobile_verification,
            )

            if await otp_model.get_and_del() is None:
                self.is_mobile_verified = False
                raise ApiException(
                    status_code=404,
                    error=Error(
                        type="Invalid request", code=307, message="Invalid Mobile OTP"
                    ),
                )

            self.is_mobile_verified = True

        if mail_otp_found:
            await mail_otp_model.delete()
