from utils.settings import settings


class SMSSender:
    @staticmethod
    async def send(phone: str, otp: str) -> bool:
        if settings.mock_sms_provider:
            return True

        # TODO: implement SMS sender
