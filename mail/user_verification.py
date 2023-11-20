from fastapi.logger import logger
from fastapi_mail import MessageSchema, MessageType
from utils.mailer import mailer


class UserVerification:
    @staticmethod
    async def send(email: str, otp):
        html = f"""
        <p>Use this code to verify your email {otp}</p> 
        """
        message = MessageSchema(
            subject="Email Verification",
            recipients=[email],
            body=html,
            subtype=MessageType.html,
        )
        try:
            await mailer.send_message(message)
        except Exception as e:
            logger.error(
                "UserVerification",
                extra={"props": {"email": email, "response": e.args}},
            )
