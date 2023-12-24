from typing import Any
from pydantic import BaseModel, Field
from utils import regex
from utils.redis_services import RedisServices


class RedisModel(BaseModel):
    shortname: str = Field(default=None, pattern=regex.NAME)

    def __init__(self, **data: Any):
        BaseModel.__init__(self, **data)

    def get_value(self) -> int:
        return 1

    def get_key(self) -> str:
        return self.shortname

    def get_expiry(self) -> int:
        return 300

    async def store(self) -> None:
        async with RedisServices() as redis:
            await redis.set(
                key=self.get_key(), value=self.get_value(), ex=self.get_expiry()
            )

    async def get_and_del(self) -> Any:
        async with RedisServices() as redis:
            return await redis.getdel(key=self.get_key())

    async def get(self) -> Any:
        async with RedisServices() as redis:
            return await redis.get(key=self.get_key())

    async def delete(self) -> None:
        async with RedisServices() as redis:
            await redis.delete(key=self.get_key())
