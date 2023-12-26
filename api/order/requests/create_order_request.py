from pydantic import BaseModel, Field
from models.base.enums import DeliverStatus, Language


class CreateOrderRequest(BaseModel):
    oodi_mobile: str | None = None
    user_shortname: str | None = None
    plan_shortname: str | None = None
    addons: list[str] = []
    high5: bool
    language: Language = Field(
        default=Language.en, examples=[Language.en, Language.ar, Language.kd]
    )
    state: DeliverStatus = DeliverStatus.pending

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "oodi_mobile": "9002213",
                    "user_shortname": "1fd1cc82",
                    "plan_shortname": "ecc82efb",
                    "addons": ["addon_one", "addon_two"],
                    "high5": True,
                    "language": "en",
                }
            ]
        }
    }
