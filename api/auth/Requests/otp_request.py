from pydantic import BaseModel, Field, model_validator
from utils import regex


class OTPRequest(BaseModel):
    email: str = Field(default=None, pattern=regex.EMAIL, examples=["myname@gmail.com"])
    mobile: str = Field(default=None, pattern=regex.MSISDN, examples=["7999228903"])

    @model_validator(mode="after")
    def require_email_or_mobile(self) -> "OTPRequest":
        if not self.email and not self.mobile:
            raise ValueError("Email or Mobile is required")

        return self
