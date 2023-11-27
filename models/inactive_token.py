from models.redis_model import RedisModel
from datetime import datetime
from utils.settings import settings


class InactiveToken(RedisModel):
    token: str
    expires: str | None = None

    def get_key(self) -> str:
        return self.token

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
