from typing import Any
from pydantic import Field, BaseModel
from models.base.enums import DeliverStatus, DeliveryMethod, Language
from models.base.ticket_model import TicketModel
from utils import regex


class Location(BaseModel):
    latitude: str | None = None
    longitude: str | None = None


class Address(BaseModel):
    city: str
    governorate_shortname: str
    district_shortname: str
    building: str
    apartment: str
    street: str
    location: Location | None = None


class Delivery(BaseModel):
    method: DeliveryMethod
    address: Address


class Order(TicketModel):
    name: str | None = None
    number: str | None = None
    address: Address | None = None
    store_shortname: str | None = None
    plan_shortname: str | None = None
    mobile: str = Field(default=None, pattern=regex.MSISDN)
    tracking_id: str | None = None
    addons: list[str] | None = None
    high4: bool | None = None
    language: Language = Field(default=Language.en)
    planned_delivery_date: str | None = None
    scheduled_delivery: str | None = None
    delivery: Delivery | None = None
    iccid: str = "8858774455555"
    state: DeliverStatus = Field(default=DeliverStatus.pending)
    workflow_shortname: str = "order"
    resolution_reason: str | None = None
    attachments: dict[str, Any] | None = None

    @classmethod
    def payload_body_attributes(cls) -> set[str]:
        return {
            "name",
            "number",
            "address",
            "store_shortname",
            "plan_shortname",
            "mobile",
            "tracking_id",
            "addons",
            "high4",
            "language",
            "planned_delivery_date",
            "scheduled_delivery",
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
