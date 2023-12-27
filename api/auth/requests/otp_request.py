from typing import Any
from pydantic import BaseModel, Field, model_validator
from utils import regex
from models.base.enums import OTPOperationType

class OTPRequest(BaseModel):
    email: str = Field(default=None, pattern=regex.EMAIL, examples=["myname@gmail.com"])
    mobile: str = Field(default=None, pattern=regex.MSISDN, examples=["7999228903"])
    operation_type: OTPOperationType

    @model_validator(mode="after")
    def require_email_or_mobile(self) -> Any:
        if not self.email and not self.mobile:
            raise ValueError("Email or Mobile is required")

        return self
