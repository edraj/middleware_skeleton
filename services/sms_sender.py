from fastapi.logger import logger
from utils.settings import settings


class SMSSender:
    @staticmethod
    async def send(phone: str, otp: str) -> bool:
        logger.info(
            "SMSSender",
            extra={"props": {"phone": phone, "otp": otp}},
        )

        if settings.mock_sms_provider:
            return True

        # TODO: implement SMS sender
