from typing import Any
from pydantic import BaseModel, Field, model_validator
from utils import regex


class ResetPasswordRequest(BaseModel):
    email: str = Field(default=None, pattern=regex.EMAIL)
    mobile: str = Field(default=None, pattern=regex.MSISDN)
    password: str = Field(pattern=regex.PASSWORD)
    otp: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "mobile": "7999228903",
                    "email": "myname@gmail.com",
                    "password": "test1234",
                    "otp": "123456",
                }
            ]
        }
    }

    @model_validator(mode="after")
    def require_email_or_mobile(self) -> Any:
        if not self.email and not self.mobile:
            raise ValueError("Email or Mobile is required")

        return self
