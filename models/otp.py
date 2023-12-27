from typing import Any
from models.base.enums import OTPOperationType
from models.base.redis_key_model import RedisKeyModel
from utils.helpers import special_to_underscore
from utils.settings import settings


class Otp(RedisKeyModel):
    operation_type: OTPOperationType | None = None

    @staticmethod
    def key_format() -> list[str]:
        return ["otp:$operation_type:$shortname"]

    def get_expiry(self) -> int:
        return settings.otp_expire

    @staticmethod
    async def validate_otp_from_request(
        data: dict[str, Any], operation_type: OTPOperationType
    ) -> bool:
        if not data.get("email") and not data.get("mobile"):
            return True

        mail_otp_found = False

        if data.get("email"):
            otp_value = await Otp.find(
                shortname=special_to_underscore(data.get("email", "")),
                operation_type=operation_type,
            )

            if otp_value is None or otp_value != data.get("email_otp", None):
                return False

            mail_otp_found = True

        if data.get("mobile"):
            otp_value = await Otp.find_and_remove(
                shortname=data.get("mobile", ""),
                operation_type=operation_type,
            )

            if otp_value is None or otp_value != data.get("mobile_otp", None):
                return False

        if mail_otp_found:
            await Otp.remove(
                shortname=special_to_underscore(data.get("email", "")),
                operation_type=operation_type,
            )

        return True
