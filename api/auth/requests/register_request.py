from pydantic import BaseModel, Field, ValidationInfo, field_validator
from models.base.enums import Gender, Language
from models.user import Invitations
from utils import regex


class ContactRequest(BaseModel):
    email_otp: str | None = None
    email: str = Field(default=None, pattern=regex.EMAIL)
    mobile_otp: str | None = None
    mobile: str = Field(default=None, pattern=regex.MSISDN)

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


class RegisterRequest(BaseModel):
    first_name: str = Field(pattern=regex.NAME)
    last_name: str = Field(pattern=regex.NAME)
    contact: ContactRequest
    password: str = Field(pattern=regex.PASSWORD)
    avatar_url: str = Field(default=None, pattern=regex.URL)
    firebase_token: str | None = None
    language: Language | None = None
    oodi_mobile: str = Field(default=None, pattern=regex.MSISDN)
    invitations: Invitations | None = None
    gender: Gender | None = None
    date_of_birth: str | None = None

    promo_code: str = Field(default=None)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "first_name": "John",
                    "last_name": "Doo",
                    "contact": {
                        "mobile_otp": "112132",
                        "mobile": "7999228903",
                        "email_otp": "112132",
                        "email": "myname@gmail.com",
                    },
                    "password": "test1234",
                    "avatar_url": "https://pics.com/myname.png",
                    "language": "en",
                    "oodi_mobile": "7950385032",
                    "invitations": {"received": "xff4fdkfisjsk", "sent": []},
                    "gender": Gender.male,
                    "date_of_birth": "1990-12-31",
                    "promo_code": "j42l343kj4",
                }
            ]
        }
    }
