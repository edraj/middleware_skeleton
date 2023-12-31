from typing import Any
from pydantic import BaseModel, Field
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


class Store(BaseModel):
    store_shortname: str


class Order(TicketModel):
    oodi_mobile: str | None = None
    user_shortname: str | None = None
    plan_shortname: str | None = None
    tracking_id: str | None = None
    addons: list[str] | None = None
    high5: bool | None = None
    delivery_location: Address | Store
    requested_date: str | None = None
    scheduled_date: str | None = None
    iccid: str | None = None

    state: DeliverStatus = Field(default=DeliverStatus.pending)
    workflow_shortname: str = "order"
    resolution_reason: str | None = None
    attachments: dict[str, Any] | None = None
    is_open: bool = True

    @classmethod
    def payload_body_attributes(cls) -> set[str]:
        return {
            "oodi_mobile",
            "user_shortname",
            "plan_shortname",
            "tracking_id",
            "addons",
            "high5",
            "delivery_location",
            "requested_date",
            "iccid",
            "scheduled_date",
        }

    @classmethod
    def class_attributes(cls) -> set[str]:
        return {
            "state",
            "workflow_shortname",
            "resolution_reason",
            "attachments",
            "is_open",
        }

    def represent(self) -> dict[str, Any]:
        return self.model_dump(
            exclude={"workflow_shortname"},
            exclude_none=True,
        )
