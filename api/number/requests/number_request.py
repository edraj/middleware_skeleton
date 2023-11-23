from pydantic import BaseModel, Field, validator
from utils import regex


class NumberRequest(BaseModel):
    number: str = Field(default=None, examples=[
                        '7803635191'], pattern=regex.MSISDN)


# cuz pattern does not accept int , it accepts only string , i have to create validator
