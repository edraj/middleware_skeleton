from pydantic import BaseModel, Field
from utils import regex


class LoginRequest(BaseModel):
    email: str = Field(default=None, pattern=regex.EMAIL)
    phone: str = Field(default=None, pattern=regex.MSISDN)
    password: str = Field(pattern=regex.PASSWORD)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "phone": "7999228903",
                    "email": "myname@gmail.com",
                    "password": "test1234",
                }
            ]
        }
    }
