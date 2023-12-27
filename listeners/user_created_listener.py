from typing import Any


class UserCreatedListener:
    def __init__(self, user: Any) -> None:
        self.user = user

    async def handle(self):
        """
        OTP SENDING IS DONE AT THE INITIAL REGISTRATION API
        """
        pass
