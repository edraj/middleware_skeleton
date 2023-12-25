from pydantic import BaseModel, Field
from models.base.enums import DeliverStatus, Language
from models.order import Address
from utils import regex


class CreateOrderRequest(BaseModel):
    name: str = Field(default=None, examples=["John"])
    number: str = Field(default=None, examples=["9002213"])
    address: Address = Field(
        default=None,
        examples=[
            {
                "city": "Cairo",
                "governorate_shortname": "Heliopolis",
                "district_shortname": "D3",
                "street": "Ali Basha",
                "building": "Tarra",
                "apartment": "33",
            }
        ],
    )
    store_shortname: str = Field(default=None, examples=["oPhone"])
    plan_shortname: str = Field(default=None, examples=["VIP"])
    mobile: str = Field(default=None, pattern=regex.MSISDN)
    addons: list[str] = []
    high4: bool
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
