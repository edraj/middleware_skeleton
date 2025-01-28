from pydantic import BaseModel


class Dummy(BaseModel):
    mere_string: str
    mere_int: int
    mere_float: float
    mere_bool: bool
    mere_dict: dict
