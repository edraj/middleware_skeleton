import asyncio
from fastapi.logger import logger
from redis.asyncio import BlockingConnectionPool, Redis
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
                    await self.client.ping()
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
                    await self.client.ping()
                except RuntimeError:
                    pass
        return self

    async def __aexit__(self, exc_type, exc, tb):
        exc_type = exc_type
        exc = exc
        tb = tb
        await self.client.aclose()

    async def get(self, key) -> str | None:
        value = await self.client.get(key)
        if isinstance(value, str):
            return value
        else:
            return None

    async def getdel(self, key) -> str | None:
        value = await self.client.getdel(key)
        if isinstance(value, str):
            return value
        else:
            return None

    async def set(self, key, value, ex=None, nx: bool = False):
        return await self.client.set(key, value, ex=ex, nx=nx)

    async def get_keys(self, pattern: str = "*") -> list:
        try:
            value = await self.client.keys(pattern)
            if isinstance(value, list):
                return value
        except Exception as e:
            logger.warning(f"Error at redis_services.get_keys: {e}")
        return []
