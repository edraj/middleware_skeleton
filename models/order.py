from typing import Any
from pydantic import BaseModel, ValidationInfo, field_validator, Field
from models.base.enums import DeliverStatus
from models.base.ticket_model import TicketModel


class Location(BaseModel):
    latitude: float | None = None
    longitude: float | None = None


class Address(BaseModel):
    governorate_shortname: str
    building: str
    apartment: str
    street: str
    location: Location | None = None


class Delivery(BaseModel):
    address: Address | None = None
    store_shortname: str | None = None
    requested_date: str | None = None
    scheduled_date: str | None = None

    @field_validator("method")
    @classmethod
    def email_otp_exists(cls, v: str, info: ValidationInfo) -> str:
        if (not info.data.get("address") and not info.data.get("store_shortname")) or (
            info.data.get("address") and info.data.get("store_shortname")
        ):
            raise ValueError("Either address or store_picketup is required")

        return v


class Order(TicketModel):
    oodi_mobile: str | None = None
    user_shortname: str | None = None
    plan_shortname: str | None = None
    tracking_id: str | None = None
    addons: list[str] | None = None
    high5: bool | None = None
    delivery: Delivery | None = None
    iccid: str = "8858774455555"

    state: DeliverStatus = Field(default=DeliverStatus.pending)
    workflow_shortname: str = "order"
    resolution_reason: str | None = None
    attachments: dict[str, Any] | None = None

    @classmethod
    def payload_body_attributes(cls) -> set[str]:
        return {
            "oodi_mobile",
            "user_shortname",
            "plan_shortname",
            "tracking_id",
            "addons",
            "high5",
            "delivery",
            "iccid",
        }

    @classmethod
    def class_attributes(cls) -> set[str]:
        return {"state", "workflow_shortname", "resolution_reason", "attachments"}

    def represent(self) -> dict[str, Any]:
        return self.model_dump(
            exclude={"workflow_shortname"},
            exclude_none=True,
        )
