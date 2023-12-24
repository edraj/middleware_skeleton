# from events.base_event import BaseEvent
from typing import Any
from listeners.user_updated_listener import UserUpdatedListener


class UserUpdatedEvent:
    def __init__(self, user: Any, updated: set[str]) -> None:
        self.user = user
        self.updated: set[str] = updated

    async def trigger(self):
        listener = UserUpdatedListener(self.user, self.updated)
        await listener.handle()
