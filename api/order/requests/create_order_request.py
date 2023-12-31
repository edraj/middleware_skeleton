from pydantic import BaseModel

from models.order import Delivery


class CreateOrderRequest(BaseModel):
    oodi_mobile: str | None = None
    plan_shortname: str | None = None
    addons: list[str] = []
    high5: bool
    delivery: Delivery

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "oodi_mobile": "9002213",
                    "plan_shortname": "ecc82efb",
                    "addons": ["addon_one", "addon_two"],
                    "high5": True,
                    "delivery": {
                        "requested_date": "2023-12-26T18:22:13.532433",
                        "address": {
                            "governorate_shortname": "Heliopolis",
                            "street": "Ali Basha",
                            "building": "Tarra",
                            "apartment": "33",
                            "location": {"latitude": 33.3152, "longitude": 44.3661},
                        },
                    },
                }
            ]
        }
    }
