from typing import Any, Self
from pydantic import BaseModel
from utils.redis_services import RedisServices
from random import randint


class RedisKeyModel(BaseModel):
    shortname: str
    value: str | None = None

    def __init__(self, **data: Any):
        if "value" not in data:
            data["value"] = f"{randint(111111, 999999)}"
        BaseModel.__init__(self, **data)

    @staticmethod
    def key_separator() -> str:
        return ":"

    @staticmethod
    def key_format() -> list[str]:
        # $ meaning: the suffix value should be considered as an object attribute
        return ["$shortname"]

    def get_key(self) -> str:
        key: str = ""
        key_items = self.__class__.key_format()
        for idx, item in enumerate(key_items):
            if item.startswith("$"):
                key += getattr(self, item[1:])
            else:
                key += item
            if idx < len(key_items) - 1:
                key += RedisKeyModel.key_separator()

        return key

    def get_expiry(self) -> int:
        return 300

    def get_value(self) -> str:
        return str(self.value)

    async def store(self) -> None:
        async with RedisServices() as redis:
            await redis.set(
                key=self.get_key(),
                value=self.get_value(),
                ex=self.get_expiry(),
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

    @classmethod
    async def create(cls, shortname: str, **kwargs: Any) -> Self:
        model: Self = cls(shortname=shortname, **kwargs)
        await model.store()
        return model

    @classmethod
    async def find(cls, shortname: str, **kwargs: Any) -> Any:
        model = cls(shortname=shortname, **kwargs)
        res = await model.get()
        return res

    @classmethod
    async def find_and_remove(cls, shortname: str, **kwargs: Any) -> Any:
        model = cls(shortname=shortname, **kwargs)
        return await model.get_and_del()

    @classmethod
    async def remove(cls, shortname: str, **kwargs: Any) -> Any:
        model = cls(shortname=shortname, **kwargs)
        return await model.delete()
