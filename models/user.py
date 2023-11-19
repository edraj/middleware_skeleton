from pydantic import Field
from events.user_created import UserCreatedEvent
from models.enums import Language, OperatingSystems
from models.json_model import JsonModel
from utils import regex
from utils.password_hashing import hash_password


class User(JsonModel):
    first_name: str = Field(pattern=regex.NAME)
    last_name: str = Field(pattern=regex.NAME)
    email: str = Field(pattern=regex.EMAIL)
    full_email: list[str] | None = None
    phone: str = Field(default=None, pattern=regex.MSISDN)
    password: str | None = None
    profile_pic_url: str = Field(default=None, pattern=regex.URL)
    firebase_token: str | None = None
    os: OperatingSystems | None = None
    language: Language | None = None
    is_email_verified: bool = False
    is_phone_verified: bool = False
    google_id: str | None = None
    facebook_id: str | None = None
    twitter_id: str | None = None

    async def store(self, trigger_events: True):
        self.password = hash_password(self.password)
        self.full_email = [self.email]

        await JsonModel.store(self)

        if trigger_events:
            await UserCreatedEvent(self).trigger()

    def represent(self) -> dict:
        return self.model_dump(
            exclude=[
                "password",
                "password_confirmation",
                "full_email",
                "google_id",
                "facebook_id",
                "twitter_id",
            ],
            exclude_none=True,
        )
