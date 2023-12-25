from pydantic import BaseModel, Field
from models.base.enums import DeliverStatus, DeliveryMethod
from datetime import datetime

from models.order import Delivery


class UpdateOrderRequest(BaseModel):
    tracking_id: str = Field(examples=["3440555"])
    planned_delivery_date: str = Field(default=None, examples=[datetime.now()])
    scheduled_delivery: str = Field(default=None, examples=[datetime.now()])
    delivery: Delivery = Field(
        examples=[
            {
                "method": DeliveryMethod.store_pickup,
                "address": {
                    "city": "Cairo",
                    "governorate_shortname": "Heliopolis",
                    "district_shortname": "D3",
                    "street": "Ali Basha",
                    "building": "Tarra",
                    "apartment": "33",
                    "location": {"latitude": "33.3152° N", "longitude": "44.3661° E"},
                },
            }
        ]
    )
    state: DeliverStatus = Field(
        default=DeliverStatus.pending,
        examples=[
            DeliverStatus.assigned,
            DeliverStatus.cancelled,
            DeliverStatus.confirmed,
            DeliverStatus.failed,
            DeliverStatus.rejected,
        ],
    )
