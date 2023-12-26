from pydantic import BaseModel
from models.base.enums import DeliverStatus, DeliveryMethod

from models.order import Delivery


class UpdateOrderRequest(BaseModel):
    tracking_id: str
    planned_delivery_date: str | None = None
    scheduled_delivery: str | None = None
    delivery: Delivery
    state: DeliverStatus = DeliverStatus.pending

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tracking_id": "3440555",
                    "planned_delivery_date": "2023-12-26T18:22:13.532433",
                    "scheduled_delivery": "2023-12-26T18:22:13.532461",
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
                    "tracking_id": "3440555",
                    "planned_delivery_date": "2023-12-26T18:22:13.532433",
                    "scheduled_delivery": "2023-12-26T18:22:13.532461",
                    "delivery": {
                        "method": DeliveryMethod.store_pickup,
                        "store_shortname": "8ba3ef81",
                    },
                },
            ]
        }
    }
