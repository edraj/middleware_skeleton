# from events.base_event import BaseEvent
from listeners.user_updated_listener import UserUpdatedListener


class UserUpdatedEvent:
    def __init__(self, user, updated: list) -> None:
        self.user = user
        self.updated = updated

    async def trigger(self):
        listener = UserUpdatedListener(self.user, self.updated)
        await listener.handle()
