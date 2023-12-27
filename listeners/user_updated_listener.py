from typing import Any


class UserUpdatedListener:
    def __init__(self, user: Any, updated: set[str]) -> None:
        self.user = user
        self.updated: set[str] = updated

    async def handle(self) -> None:
        is_outdated = False

        """
        OTP SENDING IS DONE BEFORE THE UPDATE
        """

        if is_outdated:
            await self.user.sync()  # type: ignore
