from pydantic import BaseModel, Field
from models.base.enums import DeliverStatus, Language
from models.order import DeliverLocation
from utils import regex


class CreateOrderRequest(BaseModel):
    name: str = Field(
        default=None,
        examples=["John"],
    )
    address: str = Field(default=None, examples=["Baghdad"])
    mobile: str = Field(default=None, pattern=regex.MSISDN)
    location: DeliverLocation = Field()
    language: Language = Field(
        default=Language.en, examples=[Language.en, Language.ar, Language.kd]
    )
    state: DeliverStatus = Field(
        default=DeliverStatus.pending,
        examples=[
            DeliverStatus.pending,
            DeliverStatus.assigned,
            DeliverStatus.cancelled,
            DeliverStatus.confirmed,
            DeliverStatus.failed,
            DeliverStatus.rejected,
        ],
    )
