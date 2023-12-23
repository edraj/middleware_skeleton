import asyncio
from typing import Any
from fastapi.logger import logger
from redis.asyncio import BlockingConnectionPool, Redis
from redis.typing import ExpiryT, KeyT, EncodableT
from utils.settings import settings


class RedisServices(object):
    POOL = BlockingConnectionPool(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        decode_responses=True,
        protocol=3,
        max_connections=20,
    )

    is_pytest = False

    def __await__(self):
        return self.init().__await__()

    async def init(self):
        if not hasattr(self, "client"):
            self.client = await Redis(connection_pool=self.POOL)
            if self.is_pytest:
                try:
                    await self.client.ping()  # type: ignore
                except RuntimeError:
                    pass
        return self

    def __del__(self):
        # Close connection when this object is destroyed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.client.aclose())
            else:
                loop.run_until_complete(self.client.aclose())
        except Exception:
            pass

    async def __aenter__(self):
        if not hasattr(self, "client"):
            self.client = await Redis(connection_pool=self.POOL)
            if self.is_pytest:
                try:
                    await self.client.ping()  # type: ignore
                except RuntimeError:
                    pass
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore
        # exc_type = exc_type
        # exc = exc
        # tb = tb
        await self.client.aclose()

    async def get(self, key: KeyT) -> str | None:
        value: Any = await self.client.get(key)  # type: ignore
        if isinstance(value, str):
            return value
        else:
            return None

    async def getdel(self, key: KeyT) -> str | None:
        value: Any = await self.client.getdel(key)  # type: ignore
        if isinstance(value, str):
            return value
        else:
            return None

    async def delete(self, key: KeyT) -> None:
        await self.client.delete(key)  # type: ignore

    async def set(
        self,
        key: KeyT,
        value: EncodableT,
        ex: ExpiryT | None = None,
        nx: bool = False,
    ) -> None:
        await self.client.set(key, value, ex=ex, nx=nx)  # type: ignore

    async def get_keys(self, pattern: str = "*") -> list[Any]:
        try:
            value: Any = await self.client.keys(pattern)  # type: ignore
            if type(value) is list[Any]:
                return value
        except Exception as e:
            logger.warning(f"Error at redis_services.get_keys: {e}")
        return []
