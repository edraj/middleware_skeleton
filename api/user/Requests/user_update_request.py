from pydantic import BaseModel, Field, ValidationInfo, field_validator
from models.enums import Language, OperatingSystems
from utils import regex


class UserUpdateRequest(BaseModel):
    first_name: str = Field(default=None, pattern=regex.NAME)
    last_name: str = Field(default=None, pattern=regex.NAME)
    email: str = Field(default=None, pattern=regex.EMAIL)
    mobile: str = Field(default=None, pattern=regex.MSISDN)
    profile_pic_url: str = Field(default=None, pattern=regex.URL)
    firebase_token: str | None = None
    os: OperatingSystems | None = None
    language: Language | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "first_name": "John",
                    "last_name": "Doo",
                    "mobile": "7999228903",
                    "email": "myname@gmail.com",
                    "profile_pic_url": "https://pics.com/myname.png",
                    "language": "en",
                    "os": "ios",
                    "firebase_token": "long_string"
                }
            ]
        }
    }
