from pydantic import BaseModel


class DummyData(BaseModel):
    mere_string: str
    mere_int: int
    mere_float: float
    mere_bool: bool
    mere_dict: dict
