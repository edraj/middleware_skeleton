from typing import Any
from pydantic import Field
from models.base.enums import OTPFor
from models.base.redis_model import RedisModel
from utils import regex
from utils.helpers import special_to_underscore
from utils.settings import settings


class Otp(RedisModel):
    user_shortname: str = Field(pattern=regex.NAME)
    otp_for: OTPFor
    otp: str

    def get_key(self) -> str:
        return f"otp:{self.user_shortname}:{self.otp}:{self.otp_for}"

    def get_expiry(self) -> int:
        return settings.otp_expire

    @staticmethod
    async def validate_otps(data: dict[str, Any]) -> bool:
        if not data.get("email") and not data.get("mobile"):
            return True

        mail_otp_found = False
        mail_otp_model = None

        if data.get("email"):
            mail_otp_model = Otp(
                user_shortname=special_to_underscore(data.get("email", "")),
                otp=data.get("email_otp", ""),
                otp_for=OTPFor.mail_verification,
            )

            if await mail_otp_model.get() is None:
                return False

            mail_otp_found = True

        if data.get("mobile"):
            otp_model = Otp(
                user_shortname=data.get("mobile", ""),
                otp=data.get("mobile_otp", ""),
                otp_for=OTPFor.mobile_verification,
            )

            if await otp_model.get_and_del() is None:
                return False

        if mail_otp_found and mail_otp_model:
            await mail_otp_model.delete()

        return True
