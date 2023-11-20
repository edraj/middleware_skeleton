from fastapi.logger import logger
from fastapi_mail import MessageSchema, MessageType
from utils.mailer import mailer


class UserResetPassword:
    @staticmethod
    async def send(email: str, otp):
        html = f"""
        <p>Use this code to reset your password {otp}</p> 
        """
        message = MessageSchema(
            subject="Reset Password",
            recipients=[email],
            body=html,
            subtype=MessageType.html,
        )

        try:
            await mailer.send_message(message)
        except Exception as e:
            logger.error(
                "UserResetPassword",
                extra={"props": {"email": email, "response": e.args}},
            )
