from pydantic import BaseModel
from models.base.enums import DeliveryMethod
from models.order import Delivery


class UpdateOrderRequest(BaseModel):
    delivery: Delivery

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "delivery": {
                        "method": DeliveryMethod.home,
                        "requested_date": "2023-12-26T18:22:13.532433",
                        "address": {
                            "governorate_shortname": "Heliopolis",
                            "street": "Ali Basha",
                            "building": "Tarra",
                            "apartment": "33",
                            "location": {"latitude": 33.3152, "longitude": 44.3661},
                        },
                    },
                },
                {
                    "delivery": {
                        "method": DeliveryMethod.store_pickup,
                        "store_shortname": "8ba3ef81",
                        "requested_date": "2023-12-26T18:22:13.532433",
                    },
                },
            ]
        }
    }
