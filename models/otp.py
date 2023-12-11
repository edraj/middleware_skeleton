from pydantic import Field
from models.base.enums import OTPFor
from models.base.redis_model import RedisModel
from utils import regex
from utils.settings import settings


class Otp(RedisModel):
    user_shortname: str = Field(pattern=regex.NAME)
    otp_for: OTPFor
    otp: str

    def get_key(self) -> str:
        return f"{self.user_shortname}:{self.otp}:{self.otp_for}"

    def get_expiry(self) -> int:
        return settings.otp_expire
