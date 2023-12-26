# from events.base_event import BaseEvent
from typing import Any
from listeners.user_created_listener import UserCreatedListener


class UserCreatedEvent:
    def __init__(self, user: Any) -> None:
        self.user = user

    async def trigger(self):
        listener = UserCreatedListener(self.user)
        await listener.handle()
