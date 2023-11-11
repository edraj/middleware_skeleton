from pydantic import BaseModel, Field
from utils import regex


class LoginRequest(BaseModel):
    email: str = Field(pattern=regex.EMAIL)
    password: str = Field(pattern=regex.PASSWORD)
