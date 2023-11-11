from pydantic import BaseModel
from typing import Any
from builtins import Exception as PyException
from models.enums import Status


class Error(BaseModel):
    type: str
    code: int
    message: str
    info: list[dict] | None = None


class ApiResponse(BaseModel):
    status: Status
    error: Error | None = None
    message: str | None = None
    data: dict[str, Any] = {}


class ApiException(PyException):
    status_code: int
    error: Error

    def __init__(self, status_code: int, error: Error):
        super().__init__(status_code)
        self.status_code = status_code
        self.error = error
