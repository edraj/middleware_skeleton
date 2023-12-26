from pydantic import BaseModel, Field, ValidationInfo, field_validator
from models.base.enums import Language, OperatingSystems
from utils import regex


class RegisterRequest(BaseModel):
    first_name: str = Field(pattern=regex.NAME)
    last_name: str = Field(pattern=regex.NAME)
    email_otp: str | None = None
    email: str = Field(default=None, pattern=regex.EMAIL)
    mobile_otp: str | None = None
    mobile: str = Field(default=None, pattern=regex.MSISDN)
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
    invitation_code: str | None = None

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
