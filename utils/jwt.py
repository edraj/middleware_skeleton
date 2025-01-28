import jwt
from time import time
from typing import Optional, Any
from fastapi import Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydmart.service import DmartException, Error as DmartError

from utils.settings import settings


async def decode_jwt(token: str) -> dict[str, Any]:
    decoded_token: dict[str, Any] = {}
    try:
        decoded_token = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except (jwt.exceptions.PyJWTError, jwt.exceptions.InvalidTokenError, Exception) as e:
        raise DmartException(
            status.HTTP_401_UNAUTHORIZED,
            DmartError(type="jwtauth", code=12, message=f"Invalid Token [2] {type(e)}"),
        )
    if (
        not decoded_token
        or "data" not in decoded_token
        or "expires" not in decoded_token
    ):
        raise DmartException(
            status.HTTP_401_UNAUTHORIZED,
            DmartError(type="jwtauth", code=12, message="Invalid Token [3]"),
        )
    if decoded_token["expires"] <= time():
        raise DmartException(
            status.HTTP_401_UNAUTHORIZED,
            DmartError(type="jwtauth", code=13, message="Expired Token"),
        )

    return decoded_token


class JWTBearer:
    is_required: bool = True
    http_bearer: HTTPBearer

    def __init__(self, auto_error: bool = True, is_required: bool = True):
        self.http_bearer = HTTPBearer(auto_error=auto_error)
        self.is_required = is_required

    async def __call__(self, request: Request) -> tuple[str, str]:  # Changed return type
        auth_token: str | None = None
        try:
            credentials: Optional[HTTPAuthorizationCredentials] = await self.http_bearer.__call__(request)
            if credentials and credentials.scheme == "Bearer":
                auth_token = credentials.credentials
        except Exception:
            auth_token = request.cookies.get("auth_token")

        if not auth_token:
            raise DmartException(
                status.HTTP_401_UNAUTHORIZED,
                DmartError(type="jwtauth", code=13, message="Not authenticated [1]"),
            )

        decoded: dict[str, Any] = await decode_jwt(auth_token)
        if isinstance(decoded, dict) and decoded and "data" in decoded and "shortname" in decoded["data"] and str(decoded["data"]["shortname"]) and "type" in decoded["data"]:
            return str(decoded["data"]["shortname"]), auth_token
        raise DmartException(
            status.HTTP_401_UNAUTHORIZED,
            DmartError(type="jwtauth", code=13, message="Not authenticated [2]"),
        )

def generate_jwt(data: dict, expires: int = 86400) -> str:
    payload = {"data": data, "expires": time() + expires}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
