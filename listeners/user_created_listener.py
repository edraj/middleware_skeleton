from services.sms_sender import SMSSender
from mail.user_verification import UserVerification as UserVerificationMail
import random
from models.enums import OTPFor
from models.user_otp import UserOtp


class UserCreatedListener:
    def __init__(self, user) -> None:
        self.user = user

    async def handle(self):
        mail_otp = UserOtp(
            user_shortname=self.user.shortname,
            otp_for=OTPFor.mail_verification,
            otp=f"{random.randint(111111, 999999)}",
        )
        await mail_otp.store()

        await UserVerificationMail.send(self.user.email, mail_otp.otp)

        mobile_otp = UserOtp(
            user_shortname=self.user.shortname,
            otp_for=OTPFor.mobile_verification,
            otp=f"{random.randint(111111, 999999)}",
        )
        await mobile_otp.store()

        await SMSSender.send(self.user.mobile, mobile_otp.otp)
