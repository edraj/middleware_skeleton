from models.json_model import JsonModel


class InactiveToken(JsonModel):
    token: str
    expires: str
