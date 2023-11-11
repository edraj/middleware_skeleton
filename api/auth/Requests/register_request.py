from pydantic import BaseModel, Field, ValidationInfo, field_validator
from models.enums import Language, OperatingSystems
from utils import regex


class RegisterRequest(BaseModel):
    first_name: str = Field(pattern=regex.NAME)
    last_name: str = Field(pattern=regex.NAME)
    email: str = Field(pattern=regex.EMAIL)
    phone: str = Field(pattern=regex.MSISDN)
    password_confirmation: str = Field(pattern=regex.PASSWORD)
    password: str = Field(pattern=regex.PASSWORD)
    profile_pic_url: str = Field(default=None, pattern=regex.URL)
    firebase_token: str | None = None
    os: OperatingSystems | None = None
    language: Language | None = None

    @field_validator("password")
    @classmethod
    def password_confirmed(cls, v: str, info: ValidationInfo) -> str:
        assert v == info.data.get("password_confirmation")
        return v
