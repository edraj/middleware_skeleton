from pydantic import BaseModel, Field
from api.auth.requests.register_request import ContactRequest
from models.base.enums import Gender, Language
from models.user import Invitations
from utils import regex


class UserUpdateRequest(BaseModel):
    first_name: str = Field(default=None, pattern=regex.NAME)
    last_name: str = Field(default=None, pattern=regex.NAME)
    contact: ContactRequest | None = None
    password: str = Field(default=None, pattern=regex.PASSWORD)
    avatar_url: str = Field(default=None, pattern=regex.URL)
    firebase_token: str | None = None
    language: Language | None = None
    oodi_mobile: str = Field(default=None, pattern=regex.MSISDN)
    is_oodi_mobile_active: bool | None = None
    invitations: Invitations | None = None
    gender: Gender | None = None
    date_of_birth: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "first_name": "John",
                    "last_name": "Doo",
                    "contact": {
                        "mobile": "7999228903",
                        "mobile_otp": "112132",
                        "email": "myname@gmail.com",
                        "email_otp": "112132",
                    },
                    "password": "test1234",
                    "avatar_url": "https://pics.com/myname.png",
                    "language": "en",
                    "oodi_mobile": "7950385032",
                    "is_oodi_mobile_active": True,
                    "invitations": {"received": "xff4fdkfisjsk", "sent": []},
                    "gender": Gender.male,
                    "date_of_birth": "1990-12-31",
                    "promo_code": "j42l343kj4",
                }
            ]
        }
    }
