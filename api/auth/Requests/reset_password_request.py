from pydantic import BaseModel, Field, ValidationInfo, field_validator
from utils import regex


class ResetPasswordRequest(BaseModel):
    email: str = Field(default=None, pattern=regex.EMAIL)
    phone: str = Field(default=None, pattern=regex.MSISDN)
    password_confirmation: str = Field(pattern=regex.PASSWORD)
    password: str = Field(pattern=regex.PASSWORD)
    otp: str

    @field_validator("password")
    @classmethod
    def password_confirmed(cls, v: str, info: ValidationInfo) -> str:
        assert v == info.data.get("password_confirmation")
        return v
