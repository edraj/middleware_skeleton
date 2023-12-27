from models.base.redis_key_model import RedisKeyModel
from datetime import datetime
from utils.settings import settings


class InactiveToken(RedisKeyModel):
    expires: str | None = None

    @staticmethod
    def key_format() -> list[str]:
        return ["inactive_token:$shortname"]

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
