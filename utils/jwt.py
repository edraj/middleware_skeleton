import jwt
from time import time
from typing import Optional, Any
from fastapi import Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.schemas.response import ApiException, Error
from models.active_session import ActiveSession
from models.inactive_token import InactiveToken

from utils.settings import settings


async def decode_jwt(token: str) -> dict[str, Any]:
    inactive_token = await InactiveToken.find(shortname=token)
    if inactive_token is not None:
        raise ApiException(
            status.HTTP_401_UNAUTHORIZED,
            Error(type="jwtauth", code=12, message="Invalid Token [1]"),
        )

    decoded_token: dict[str, Any]
    try:
        decoded_token = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except Exception:
        raise ApiException(
            status.HTTP_401_UNAUTHORIZED,
            Error(type="jwtauth", code=12, message="Invalid Token [2]"),
        )
    if (
        not decoded_token
        or "data" not in decoded_token
        or "expires" not in decoded_token
    ):
        raise ApiException(
            status.HTTP_401_UNAUTHORIZED,
            Error(type="jwtauth", code=12, message="Invalid Token [3]"),
        )
    if decoded_token["expires"] <= time():
        raise ApiException(
            status.HTTP_401_UNAUTHORIZED,
            Error(type="jwtauth", code=13, message="Expired Token"),
        )

    active_session_token = await ActiveSession.find(
        decoded_token["data"].get("username", "")
    )
    if active_session_token != token:
        raise ApiException(
            status.HTTP_401_UNAUTHORIZED,
            Error(type="jwtauth", code=12, message="Invalid Token [4]"),
        )

    return decoded_token


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:  # type: ignore
        auth_token: str | None = None
        # Try to get the token from the Authorization header
        try:
            credentials: HTTPAuthorizationCredentials | None = await super(
                JWTBearer, self
            ).__call__(request)
            if credentials and credentials.scheme == "Bearer":
                auth_token = credentials.credentials
        except Exception:
            pass

        # Second attempt to get the token from the cookies
        if not auth_token and request.cookies.get("auth_token"):
            auth_token = request.cookies.get("auth_token")

        if not auth_token:
            raise ApiException(
                status.HTTP_401_UNAUTHORIZED,
                Error(type="jwtauth", code=13, message="Not authenticated [1]"),
            )

        decoded: dict[str, Any] = await decode_jwt(auth_token)
        if decoded and "data" in decoded and "username" in decoded["data"] and str(decoded["data"]["username"]):
            return str(decoded["data"]["username"])

        raise ApiException(
            status.HTTP_401_UNAUTHORIZED,
            Error(type="jwtauth", code=13, message="Not authenticated [2]"),
        )

    @classmethod
    async def extract_and_decode(cls, request: Request) -> dict[str, Any]:
        token: str = request.headers.get("Authorization") or request.cookies.get(
            "auth_token", ""
        )
        token = token.split("Bearer ")[-1]
        decoded: dict[str, Any] = await decode_jwt(token)
        decoded["token"] = token
        return decoded


class GetJWTToken(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(GetJWTToken, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:  # type: ignore
        try:
            credentials: Optional[HTTPAuthorizationCredentials] = await super(
                GetJWTToken, self
            ).__call__(request)
            if credentials and credentials.scheme == "Bearer":
                return credentials.credentials
        except Exception:
            return request.cookies.get("auth_token")


def sign_jwt(data: dict[str, Any], expires: int = settings.access_token_expire) -> str:
    payload = {"data": data, "expires": time() + expires}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
