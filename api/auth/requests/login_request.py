from pydantic import BaseModel, Field, model_validator
from utils import regex


class LoginRequest(BaseModel):
    email: str = Field(default=None, pattern=regex.EMAIL)
    email_otp: str | None = None
    mobile: str = Field(default=None, pattern=regex.MSISDN)
    mobile_otp: str | None = None
    password: str = Field(default=None, pattern=regex.PASSWORD)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "mobile": "7999228903",
                    "email": "myname@gmail.com",
                    "password": "test1234",
                }
            ]
        }
    }

    @model_validator(mode="after")
    def define_required_fields(self):
        if not self.email and not self.mobile:
            raise ValueError("Email or Mobile is required")

        if self.email and self.mobile:
            raise ValueError("Can't use both Email and Mobile")

        if not self.password and (
            (self.email and not self.email_otp) or (self.mobile and not self.mobile_otp)
        ):
            raise ValueError("Password or OTP is required")

        return self
