from pydantic import BaseModel, Field
from models.base.enums import DeliverStatus, Language


class CreateOrderRequest(BaseModel):
    oodi_mobile: str = Field(default=None, examples=["9002213"])
    user_shortname: str = Field(default=None, examples=["1fd1cc82"])
    plan_shortname: str = Field(default=None, examples=["ecc82efb"])
    addons: list[str] = []
    high5: bool
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
