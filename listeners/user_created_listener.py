from mail.user_verification import UserVerification
import random
from models.enums import OTPFor
from models.user_otp import UserOtp


class UserCreatedListener:
    def __init__(self, user) -> None:
        self.user = user

    async def handle(self):
        otp_model = UserOtp(
            user_shortname=self.user.shortname,
            otp_for=OTPFor.mail_verification,
            otp=f"{random.randint(111111, 999999)}",
        )
        await otp_model.store()

        await UserVerification.send(self.user.email, otp_model.otp)
