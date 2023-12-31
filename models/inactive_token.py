from typing import Any
from models.base.redis_key_model import RedisKeyModel
from datetime import datetime
from utils.settings import settings


class InactiveToken(RedisKeyModel):
    expires: str | None = None

    def __init__(self, **data: Any):
        data["value"] = "1"
        RedisKeyModel.__init__(self, **data)

    @staticmethod
    def key_format() -> list[str]:
        return ["inactive_token", "$shortname"]

    def get_expiry(self) -> int:
        if self.expires:
            seconds = int(
                (
                    datetime.fromtimestamp(float(self.expires)) - datetime.now()
                ).total_seconds()
            )
        else:
            seconds = settings.access_token_expire

        return seconds
