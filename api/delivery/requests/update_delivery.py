from pydantic import BaseModel, Field
from models.base.enums import DeliverStatus
from datetime import datetime


class UpdateDeliveryRequest(BaseModel):
    tracking_id: str = Field()
    planned_delivery_date: str = Field(default=None, examples=[datetime.now()])
    scheduled_delivery: str = Field(default=None, examples=[datetime.now()])
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
