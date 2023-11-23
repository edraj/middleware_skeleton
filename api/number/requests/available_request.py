from pydantic import BaseModel, Field
from utils import regex


class AvailableNumberRequest(BaseModel):
    available_numbers: str = Field(
        examples=['345656', '442367'], pattern=regex.AVAILABLE_NUMBER_CHECK)
