from pydantic import BaseModel, Field, ValidationInfo, field_validator
from models.base.enums import Language, OperatingSystems
from utils import regex


class UserUpdateRequest(BaseModel):
    first_name: str = Field(default=None, pattern=regex.NAME)
    last_name: str = Field(default=None, pattern=regex.NAME)
    email_otp: str | None = None
    email: str = Field(default=None, pattern=regex.EMAIL)
    mobile_otp: str | None = None
    mobile: str = Field(default=None, pattern=regex.MSISDN)
    profile_pic_url: str = Field(default=None, pattern=regex.URL)
    firebase_token: str | None = None
    os: OperatingSystems | None = None
    language: Language | None = None

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
                    "profile_pic_url": "https://pics.com/myname.png",
                    "language": "en",
                    "os": "ios",
                    "firebase_token": "long_string",
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
