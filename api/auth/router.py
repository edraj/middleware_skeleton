import random
from typing import Annotated, Any
from venv import logger
import aiohttp
from fastapi import APIRouter, Body, Depends, Request, Response
from api.auth.Requests.otp_request import OTPRequest
from api.auth.Requests.login_request import LoginRequest
from api.auth.Requests.register_request import RegisterRequest
from api.auth.Requests.reset_password_request import ResetPasswordRequest
from api.schemas.response import ApiException, ApiResponse, Error
from models.inactive_token import InactiveToken
from services.facebook_sso import get_facebook_sso
from services.github_sso import get_github_sso
from services.google_sso import get_google_sso
from services.microsoft_sso import get_microsoft_sso
from services.sms_sender import SMSSender
from mail.user_reset_password import UserResetPassword
from mail.user_verification import UserVerification
from models.user import User
from models.base.enums import OTPFor, Status
from models.otp import Otp
from utils.helpers import escape_for_redis, special_to_underscore
from utils.jwt import JWTBearer, sign_jwt
from utils.password_hashing import hash_password, verify_password
from utils.settings import settings
from fastapi_sso.sso.base import OpenID
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO
from fastapi_sso.sso.github import GithubSSO
from fastapi_sso.sso.microsoft import MicrosoftSSO
from fastapi_sso.sso.base import SSOBase

router = APIRouter()


@router.post("/otp-request", response_model_exclude_none=True)
async def otp_request(request: OTPRequest):
    if request.email:
        otp = Otp(
            user_shortname=special_to_underscore(request.email),
            otp_for=OTPFor.mail_verification,
            otp=f"{random.randint(111111, 999999)}",
        )
        await otp.store()

        await UserVerification.send(request.email, otp.otp)

    if request.mobile:
        otp = Otp(
            user_shortname=request.mobile,
            otp_for=OTPFor.mobile_verification,
            otp=f"{random.randint(111111, 999999)}",
        )
        await otp.store()

        await SMSSender.send(request.mobile, otp.otp)

    return ApiResponse(status=Status.success, message="OTP sent successfully")


@router.post("/register", response_model_exclude_none=True)
async def register(request: RegisterRequest):
    is_valid_otp = await Otp.validate_otps(request.model_dump())

    if not is_valid_otp:
        raise ApiException(
            status_code=404,
            error=Error(type="Invalid request", code=307, message="Invalid OTP"),
        )

    user_model = User(
        **request.model_dump(
            exclude={"password_confirmation", "email_otp", "mobile_otp"},
            exclude_none=True,
        ),
    )

    if request.email:
        user_model.is_email_verified = True

    if request.mobile:
        user_model.is_mobile_verified = True

    await user_model.store()

    return ApiResponse(
        status=Status.success,
        message="Account created successfully",
        data=user_model.represent(),
    )


@router.post("/login", response_model_exclude_none=True)
async def login(response: Response, request: LoginRequest):
    user: User | None = await User.find(
        f"@full_email:{{{escape_for_redis(request.email)}}}"
        if request.email
        else f"@mobile:{request.mobile}"
    )

    if (
        not user
        or (
            (request.email and not user.is_email_verified)
            or (request.mobile and not user.is_mobile_verified)
        )
        or (
            request.password
            and user.password
            and not verify_password(request.password, user.password)
        )
    ):
        raise ApiException(
            status_code=401,
            error=Error(type="auth", code=14, message="Invalid Credentials"),
        )

    if not request.password:
        is_valid_otp: bool = await Otp.validate_otps(
            request.model_dump(exclude_none=True)
        )
        if not is_valid_otp:
            raise ApiException(
                status_code=401,
                error=Error(type="auth", code=14, message="Invalid OTP"),
            )

    access_token = sign_jwt({"username": user.shortname}, settings.jwt_access_expires)

    response.set_cookie(
        value=access_token,
        max_age=settings.jwt_access_expires,
        key="auth_token",
        httponly=True,
        secure=True,
        samesite="none",
    )

    return ApiResponse(
        status=Status.success,
        message="Logged in successfully",
        data={
            "user": user.represent(),
            "token": access_token,
        },
    )


@router.get("/forgot-password", response_model_exclude_none=True)
async def forgot_password(email: str | None = None, mobile: str | None = None):
    if not email and not mobile:
        raise ApiException(
            status_code=401,
            error=Error(
                type="auth", code=14, message="Please provide email or mobile number"
            ),
        )

    user: User | None = await User.find(
        f"@full_email:{{{escape_for_redis(email)}}}" if email else f"@mobile:{mobile}"
    )

    if not user:
        raise ApiException(
            status_code=404,
            error=Error(type="db", code=12, message="User not found"),
        )

    otp = Otp(
        user_shortname=user.shortname,
        otp_for=OTPFor.reset_password,
        otp=f"{random.randint(111111, 999999)}",
    )
    await otp.store()

    if email:
        await UserResetPassword.send(user.email, otp.otp)
        message = "Email sent successfully"
    else:
        await SMSSender.send(user.mobile, otp.otp)
        message = "SMS sent successfully"

    return ApiResponse(status=Status.success, message=message)


@router.post("/reset-password", response_model_exclude_none=True)
async def reset_password(request: ResetPasswordRequest):
    if not request.email and not request.mobile:
        raise ApiException(
            status_code=401,
            error=Error(
                type="auth", code=14, message="Please provide email or mobile number"
            ),
        )

    user: User | None = await User.find(
        f"@full_email:{{{escape_for_redis(request.email)}}}"
        if request.email
        else f"@mobile:{request.mobile}"
    )

    if not user:
        raise ApiException(
            status_code=404,
            error=Error(type="db", code=12, message="User not found"),
        )

    otp_model = Otp(
        user_shortname=user.shortname, otp=request.otp, otp_for=OTPFor.reset_password
    )
    otp_exists = await otp_model.get_and_del()

    if not otp_exists:
        return ApiResponse(
            status=Status.failed,
            error=Error(type="Invalid request", code=307, message="Invalid OTP"),
        )

    user.password = hash_password(request.password)
    await user.sync()

    return ApiResponse(status=Status.success, message="Password updated successfully")


@router.post("/google/login")
async def google_profile(
    access_token: Annotated[str, Body()],
    google_sso: GoogleSSO = Depends(get_google_sso),
):
    user_model = await social_login(access_token, google_sso, "google")

    access_token = sign_jwt(
        {"username": user_model.shortname}, settings.jwt_access_expires
    )

    return ApiResponse(
        status=Status.success,
        message="Logged in successfully",
        data={
            "user": user_model.represent(),
            "token": access_token,
        },
    )


@router.post("/facebook/login")
async def facebook_login(
    access_token: Annotated[str, Body()],
    facebook_sso: FacebookSSO = Depends(get_facebook_sso),
):
    user_model = await social_login(access_token, facebook_sso, "facebook")

    access_token = sign_jwt(
        {"username": user_model.shortname}, settings.jwt_access_expires
    )

    return ApiResponse(
        status=Status.success,
        message="Logged in successfully",
        data={
            "user": user_model.represent(),
            "token": access_token,
        },
    )


@router.get("/github/login")
async def github_login(
    access_token: Annotated[str, Body()],
    github_sso: GithubSSO = Depends(get_github_sso),
):
    user_model = await social_login(access_token, github_sso, "github")

    access_token = sign_jwt(
        {"username": user_model.shortname}, settings.jwt_access_expires
    )

    return ApiResponse(
        status=Status.success,
        message="Logged in successfully",
        data={
            "user": user_model.represent(),
            "token": access_token,
        },
    )


@router.get("/microsoft/login")
async def microsoft_login(
    access_token: Annotated[str, Body()],
    microsoft_sso: MicrosoftSSO = Depends(get_microsoft_sso),
):
    user_model = await social_login(access_token, microsoft_sso, "microsoft")

    access_token = sign_jwt(
        {"username": user_model.shortname}, settings.jwt_access_expires
    )

    return ApiResponse(
        status=Status.success,
        message="Logged in successfully",
        data={
            "user": user_model.represent(),
            "token": access_token,
        },
    )


async def social_login(access_token: str, sso: SSOBase, provider: str) -> User:
    async with aiohttp.ClientSession() as session:
        user_profile_endpoint: str | None = await sso.userinfo_endpoint
        response = None
        if user_profile_endpoint:
            response = await session.get(
                user_profile_endpoint,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if not response or response.status != 200:
            raise ApiException(
                status_code=400,
                error=Error(type="data", code=12, message="Invalid access token"),
            )

        content: dict[str, Any] = await response.json()
        provider_user: OpenID = await sso.openid_from_response(content)  # type: ignore

    user_model: User | None = await User.find(
        search=f"@{provider}_id:{provider_user.id}"
    )

    if not user_model:
        try:
            user_model = User(
                **provider_user.model_dump(include={"first_name", "last_name", "email"})
            )
            user_model.is_email_verified = True
            setattr(user_model, f"{provider}_id", provider_user.id)

        except Exception as e:
            logger.error(
                "Invalid SSO provider data",
                {
                    "provider": provider,
                    "user_profile_endpoint": user_profile_endpoint,
                    "response": content,
                    "provider_user": provider_user,
                    "error": e.args,
                },
            )
            raise ApiException(
                status_code=400,
                error=Error(type="data", code=12, message="Invalid provider data"),
            )

        await user_model.store(trigger_events=False)

    return user_model


@router.post("/logout")
async def logout(
    response: Response, request: Request, shortname: str = Depends(JWTBearer())
):
    user: User = await User.get_or_fail(shortname)

    if user.firebase_token:
        user.firebase_token = None
        await user.sync()

    decoded_data = await JWTBearer().extract_and_decode(request)
    inactive_token = InactiveToken(
        token=decoded_data.get("token", ""), expires=str(decoded_data.get("expires"))
    )
    await inactive_token.store()

    response.set_cookie(
        value="",
        max_age=0,
        key="auth_token",
        httponly=True,
        secure=True,
        samesite="none",
    )

    return ApiResponse(status=Status.success, message="Logged out successfully")
