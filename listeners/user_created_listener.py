from typing import Any


class UserCreatedListener:
    def __init__(self, user: Any) -> None:
        self.user = user

    async def handle(self):
        """
        OTP SENDING IS DONE AT THE INITIAL REGISTRATION API
        """
        pass
        # mail_otp = Otp(
        #     user_shortname=self.user.shortname,
        #     otp_for=OTPFor.mail_verification,
        #     otp=f"{random.randint(111111, 999999)}",
        # )
        # await mail_otp.store()

        # await UserVerificationMail.send(self.user.email, mail_otp.otp)

        # mobile_otp = Otp(
        #     user_shortname=self.user.shortname,
        #     otp_for=OTPFor.mobile_verification,
        #     otp=f"{random.randint(111111, 999999)}",
        # )
        # await mobile_otp.store()

        # await SMSSender.send(self.user.mobile, mobile_otp.otp)
