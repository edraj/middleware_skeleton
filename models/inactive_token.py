from models.json_model import JsonModel
from utils.helpers import escape_for_redis


class InactiveToken(JsonModel):
    token: str
    expires: str

    async def store(self):
        self.token = escape_for_redis(self.token)

        await JsonModel.store(self)
