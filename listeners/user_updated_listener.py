from services.sms_sender import SMSSender
from mail.user_verification import UserVerification as UserVerificationMail
import random
from models.enums import OTPFor
from models.user_otp import UserOtp


class UserUpdatedListener:
    def __init__(self, user, updated: list) -> None:
        self.user = user
        self.updated = updated

    async def handle(self) -> None:
        is_outdated = False
        if "email" in self.updated:
            self.user.full_email = [self.user.email]
            is_outdated = True

        if "email" in self.updated and self.user.is_email_verified:
            self.user.is_email_verified = False
            mail_otp = UserOtp(
                user_shortname=self.user.shortname,
                otp_for=OTPFor.mail_verification,
                otp=f"{random.randint(111111, 999999)}",
            )
            await mail_otp.store()

            await UserVerificationMail.send(self.user.email, mail_otp.otp)

        if "email" in self.updated and self.user.is_mobile_verified:
            self.user.is_mobile_verified = False
            mobile_otp = UserOtp(
                user_shortname=self.user.shortname,
                otp_for=OTPFor.mobile_verification,
                otp=f"{random.randint(111111, 999999)}",
            )
            await mobile_otp.store()

            await SMSSender.send(self.user.mobile, mobile_otp.otp)
            is_outdated = True

        if is_outdated:
            await self.user.sync()
