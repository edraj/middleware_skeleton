from typing import Any
from pydantic import BaseModel, Field, model_validator
from events.user_created import UserCreatedEvent
from events.user_updated import UserUpdatedEvent
from models.base.enums import Gender, Language, ResourceType
from models.base.json_model import JsonModel
from utils import regex
from utils.password_hashing import hash_password


class Contact(BaseModel):
    email: str = Field(default=None, pattern=regex.EMAIL)
    full_email: list[str] = Field(default=None)
    mobile: str = Field(default=None, pattern=regex.MSISDN)

    @model_validator(mode="after")
    def require_email_or_mobile(self) -> Any:
        if not self.email and not self.mobile:
            raise ValueError("Email or Mobile is required")

        return self


class OAuthIDs(BaseModel):
    google_id: str | None = None
    facebook_id: str | None = None
    twitter_id: str | None = None
    github_id: str | None = None
    microsoft_id: str | None = None


class Invitations(BaseModel):
    received: str | None = None
    sent: list[str] | None = None


class User(JsonModel):
    first_name: str = Field(pattern=regex.NAME)
    last_name: str = Field(pattern=regex.NAME)
    contact: Contact
    password: str | None = None
    avatar_url: str = Field(default=None, pattern=regex.URL)
    firebase_token: str | None = None
    language: Language | None = None
    oauth_ids: OAuthIDs | None = None
    oodi_mobile: str = Field(default=None, pattern=regex.MSISDN)
    is_oodi_mobile_active: bool | None = None
    invitations: Invitations | None = None
    gender: Gender | None = None
    date_of_birth: str | None = None

    async def store(
        self,
        resource_type: ResourceType = ResourceType.content,
        trigger_events: bool = True,
    ):
        if self.password:
            self.password = hash_password(self.password)

        if self.contact and self.contact.email:
            self.contact.full_email = [self.contact.email]

        await JsonModel.store(self)

        if trigger_events:
            await UserCreatedEvent(self).trigger()

    async def sync(
        self,
        resource_type: ResourceType = ResourceType.content,
        updated: set[str] = set(),
        trigger_events: bool = True,
    ) -> None:
        if self.password:
            self.password = hash_password(self.password)

        if self.contact and self.contact.email:
            self.contact.full_email = [self.contact.email]

        await JsonModel.sync(self, resource_type)

        if trigger_events:
            await UserUpdatedEvent(self, updated).trigger()

    def represent(self) -> dict[str, Any]:
        user: dict[str, Any] = self.model_dump(
            exclude={
                "password",
                "contact.full_email",
                "firebase_token",
                "oauth_ids",
                "invitations",
            },
            exclude_none=True,
        )
        user.get("contact", {}).pop("full_email", "")
        return user
