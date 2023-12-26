from typing import Any
from pydantic import Field
from events.user_created import UserCreatedEvent
from events.user_updated import UserUpdatedEvent
from models.base.enums import Language, OperatingSystems, ResourceType
from models.base.json_model import JsonModel
from utils import regex
from utils.password_hashing import hash_password


class User(JsonModel):
    first_name: str = Field(pattern=regex.NAME)
    last_name: str = Field(pattern=regex.NAME)
    email: str = Field(pattern=regex.EMAIL)
    full_email: list[str] | None = None
    mobile: str = Field(default=None, pattern=regex.MSISDN)
    password: str | None = None
    profile_pic_url: str = Field(default=None, pattern=regex.URL)
    firebase_token: str | None = None
    os: OperatingSystems | None = None
    language: Language | None = None
    is_email_verified: bool = False
    is_mobile_verified: bool = False
    google_id: str | None = None
    facebook_id: str | None = None
    twitter_id: str | None = None
    github_id: str | None = None
    microsoft_id: str | None = None

    async def store(
        self,
        resource_type: ResourceType = ResourceType.content,
        trigger_events: bool = True,
    ):
        if self.password:
            self.password = hash_password(self.password)
        self.full_email = [self.email]

        await JsonModel.store(self)

        if trigger_events:
            await UserCreatedEvent(self).trigger()

    async def sync(
        self,
        resource_type: ResourceType = ResourceType.content,
        updated: set[str] = set(),
        trigger_events: bool = True,
    ) -> None:
        await JsonModel.sync(self, resource_type)

        if trigger_events:
            await UserUpdatedEvent(self, updated).trigger()

    def represent(self) -> dict[str, Any]:
        return self.model_dump(
            exclude={
                "password",
                "full_email",
                "google_id",
                "facebook_id",
                "twitter_id",
                "github_id",
                "microsoft_id",
            },
            exclude_none=True,
        )
