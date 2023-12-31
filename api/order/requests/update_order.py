from pydantic import BaseModel

from models.order import Address, Store


class UpdateOrderRequest(BaseModel):
    requested_date: str | None = None
    delivery_location: Address | Store | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "requested_date": "2023-12-26T18:22:13.532433",
                    "delivery_location": {
                        "governorate_shortname": "Heliopolis",
                        "street": "Ali Basha",
                        "building": "Tarra",
                        "apartment": "33",
                        "location": {"latitude": 33.3152, "longitude": 44.3661},
                    },
                },
                {
                    "requested_date": "2023-12-26T18:22:13.532433",
                    "delivery_location": {
                        "store_shortname": "8ba3ef81",
                    },
                },
            ]
        }
    }
