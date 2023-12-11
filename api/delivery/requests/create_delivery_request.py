from pydantic import BaseModel,Field
from models.base.enums import DeliverStatus, Language, StrEnum
from utils import regex

class DeliverLocation(BaseModel):
     latitude:str=Field(default=None,examples=['33.3152° N'])
     longitude:str=Field(default=None,examples=['44.3661° E'])
class CreateDeliveryRequest(BaseModel):

    name: str = Field(default=None, examples=['kadhum'],)
    address: str = Field(default=None, examples=['baghdad'])
    mobile:str= Field(default=None,pattern=regex.MSISDN)
    location:DeliverLocation=Field()
    language:Language=Field(default=Language.en,examples=[Language.en,Language.ar,Language.kd])
    state:DeliverStatus=Field(default=DeliverStatus.pending,examples=[DeliverStatus.pending,DeliverStatus.assigned,DeliverStatus.cancelled,DeliverStatus.confirmed,DeliverStatus.failed,DeliverStatus.rejected])