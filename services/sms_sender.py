from fastapi.logger import logger
from utils.settings import settings


class SMSSender:
    @staticmethod
    async def send(mobile: str, otp: str) -> bool:
        logger.info(
            "SMSSender",
            extra={"props": {"mobile": mobile, "otp": otp}},
        )

        if settings.mock_sms_provider:
            return True

        # TODO: implement SMS sender
        return True
