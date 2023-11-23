from enum import Enum
from pydantic import Field, BaseModel


class DeliveryStatus(str, Enum):
    progress = "progress",
    Cancel = "Cancel",
    Delivered = "Delivered",
    Failed = "Failed",


class DeliveryRequest(BaseModel):

    name: str = Field(default=None, examples=['kadhum'],)
    address: str = Field(default=None, examples=['baghdad'])
    # progress,Cancel ,Delivered , Failed (get it from oldApi)
    status: DeliveryStatus = Field(
        examples=[DeliveryStatus.progress, DeliveryStatus.Delivered, DeliveryStatus.Cancel])
