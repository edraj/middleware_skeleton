from pydantic import BaseModel,Field
from models.enums import DeliverStatus, Language
from utils import regex
from datetime import datetime ,date
class UpdateDeliveryRequest(BaseModel):
    tracking_id:str =Field()
    planned_delivery_date:str =Field(default=None,examples=[datetime.now()])
    scheduled_delivery:str =Field(default=None,examples=[datetime.now()])
    state:DeliverStatus=Field(default=DeliverStatus.pending,examples=[DeliverStatus.assigned,DeliverStatus.cancelled,DeliverStatus.confirmed,DeliverStatus.failed,DeliverStatus.rejected])
        