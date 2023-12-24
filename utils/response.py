import typing
from starlette.types import Receive, Scope, Send
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask
import json
from cryptography.fernet import Fernet
from utils.settings import settings


def clean_dict(dict_with_nones: typing.Any) -> typing.Any:
    if not isinstance(dict_with_nones, dict):
        return dict_with_nones

    result: dict[str, typing.Any] = {}
    for key, value in dict_with_nones.items():  # type: ignore
        if value is not None:
            result[key] = clean_dict(value)  # type: ignore
    return result


def safe_log_body(request_body: dict[str, typing.Any] | None = None):
    """
    safe loging the body by hashing the password
    """

    if request_body and request_body.get("password"):
        key = settings.logger_password_hash_key.encode()
        f = Fernet(key)
        new_body = request_body.copy()
        new_body["password"] = str(f.encrypt(new_body["password"].encode()))
        return new_body
    else:
        return request_body


class MainResponse(JSONResponse):
    def __init__(
        self,
        content: typing.Any,
        status_code: int = 200,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        media_type: str = "application/json",
        background: typing.Optional[BackgroundTask] = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)
        pass

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        await super().__call__(scope, receive, send)
        try:
            extra = scope["state"]["extra"]
            extra["props"]["response"]["body"] = json.loads(self.body)
            logger_request_body = safe_log_body(
                request_body=extra["props"]["request"]["body"]
            )
            extra["props"]["request"]["body"] = logger_request_body
            if extra.get("props", {}).get("exception", False):
                logger.error("Error", extra=extra)
            else:
                logger.info("Processed", extra=extra)
        except Exception as e:
            logger.error("Error", extra={"props": {"message": str(e)}})

    def render(self, content: typing.Any) -> bytes:
        data: dict[str, typing.Any] = {}
        try:
            data = content if isinstance(content, dict) else json.loads(content)
        except ValueError:
            data = {"error": content}

        return json.dumps(clean_dict(data), indent=2).encode("utf-8")
