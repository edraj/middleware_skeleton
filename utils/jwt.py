import jwt
from time import time
from typing import Optional, Any
from fastapi import Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.schemas.response import ApiException, Error
from models.inactive_token import InactiveToken

from utils.settings import settings


async def decode_jwt(token: str) -> dict[str, Any]:
    inactive = InactiveToken(token=token)
    inactive_exists = await inactive.get()
    if inactive_exists:
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

    return decoded_token


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:  # type: ignore
        user_shortname: str | None = None
        try:
            # Handle token received in Auth header
            credentials: Optional[HTTPAuthorizationCredentials] = await super(
                JWTBearer, self
            ).__call__(request)
            if credentials and credentials.scheme == "Bearer":
                decoded = await decode_jwt(credentials.credentials)
                if decoded and decoded.get("data", {}).get("username"):
                    user_shortname = decoded["data"]["username"]
        except Exception:
            # Handle token received in the cookie
            auth_token = request.cookies.get("auth_token")
            if auth_token:
                decoded = await decode_jwt(auth_token)
                if decoded and decoded.get("data", {}).get("username"):
                    user_shortname = decoded["data"]["username"]
        finally:
            if not user_shortname:
                raise ApiException(
                    status.HTTP_401_UNAUTHORIZED,
                    Error(type="jwtauth", code=13, message="Not authenticated [1]"),
                )

        return user_shortname

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
