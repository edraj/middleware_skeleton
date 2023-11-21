from pydantic import BaseModel, Field, ValidationInfo, field_validator
from utils import regex


class ResetPasswordRequest(BaseModel):
    email: str = Field(default=None, pattern=regex.EMAIL)
    mobile: str = Field(default=None, pattern=regex.MSISDN)
    password_confirmation: str = Field(pattern=regex.PASSWORD)
    password: str = Field(pattern=regex.PASSWORD)
    otp: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "mobile": "7999228903",
                    "email": "myname@gmail.com",
                    "password": "test1234",
                    "password_confirmation": "test1234",
                    "otp": "123456",
                }
            ]
        }
    }

    @field_validator("password")
    @classmethod
    def password_confirmed(cls, v: str, info: ValidationInfo) -> str:
        assert v == info.data.get("password_confirmation")
        return v
