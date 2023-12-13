from pydantic import Field, BaseModel
from models.base.enums import DeliverStatus, Language
from models.base.ticket_model import TicketModel
from utils import regex


class DeliverLocation(BaseModel):
    latitude: str = Field(default=None, examples=["33.3152° N"])
    longitude: str = Field(default=None, examples=["44.3661° E"])


class Order(TicketModel):
    name: str = Field(default=None)
    address: str = Field(default=None)
    mobile: str = Field(default=None, pattern=regex.MSISDN)
    tracking_id: str | None = None
    location: DeliverLocation = Field()
    language: Language = Field(default=Language.en)
    state: DeliverStatus = Field(default=DeliverStatus.pending)
    planned_delivery_date: str | None = None
    scheduled_delivery: str | None = None
    workflow_shortname: str = "order"
    resolution_reason: str | None = None
    iccid: str = "8858774455555"
    attachments: dict | None = None

    @classmethod
    def payload_body_attributes(self) -> list:
        return [
            "name",
            "address",
            "mobile",
            "tracking_id",
            "location",
            "language",
            "planned_delivery_date",
            "scheduled_delivery",
            "iccid",
        ]

    @classmethod
    def class_attributes(self) -> dict:
        return ["state", "workflow_shortname", "attachments"]

    def represent(self) -> dict:
        return self.model_dump(
            exclude=["workflow_shortname"],
            exclude_none=True,
        )
