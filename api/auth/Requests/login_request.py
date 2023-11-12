from pydantic import BaseModel, Field
from utils import regex


class LoginRequest(BaseModel):
    email: str = Field(default=None, pattern=regex.EMAIL)
    phone: str = Field(default=None, pattern=regex.MSISDN)
    password: str = Field(pattern=regex.PASSWORD)
