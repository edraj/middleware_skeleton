from pydantic import Field
from models.enums import OTPFor
from models.json_model import JsonModel
from utils import regex
from utils.redis_services import RedisServices
from utils.settings import settings


class Otp(JsonModel):
    user_shortname: str = Field(pattern=regex.NAME)
    otp_for: OTPFor
    otp: str
    
    def generate_redis_key(self) -> str:
        return f"{self.user_shortname}:{self.otp}:{self.otp_for}"
    
    async def store(self) -> None:
        async with RedisServices() as redis:
            await redis.set(key=self.generate_redis_key(), value=1, ex=settings.otp_expire)
            
    async def get_and_del(self) -> str | None:
        async with RedisServices() as redis:
            return await redis.getdel(key=self.generate_redis_key())
    
