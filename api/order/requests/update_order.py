from pydantic import BaseModel
from models.base.enums import DeliveryMethod
from models.order import Delivery


class UpdateOrderRequest(BaseModel):
    requested_delivery_date: str | None = None
    delivery: Delivery

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "requested_delivery_date": "2023-12-26T18:22:13.532433",
                    "delivery": {
                        "method": DeliveryMethod.home,
                        "address": {
                            "city": "Cairo",
                            "governorate_shortname": "Heliopolis",
                            "district_shortname": "D3",
                            "street": "Ali Basha",
                            "building": "Tarra",
                            "apartment": "33",
                            "location": {"latitude": 33.3152, "longitude": 44.3661},
                        },
                    },
                },
                {
                    "requested_delivery_date": "2023-12-26T18:22:13.532433",
                    "delivery": {
                        "method": DeliveryMethod.store_pickup,
                        "store_shortname": "8ba3ef81",
                    },
                },
            ]
        }
    }
