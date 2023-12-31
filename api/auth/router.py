from typing import Annotated, Any
from venv import logger
import aiohttp
from fastapi import APIRouter, Body, Depends, Request, Response, status
from api.auth.requests.otp_request import OTPRequest
from api.auth.requests.login_request import LoginRequest
from api.auth.requests.register_request import RegisterRequest
from api.auth.requests.reset_password_request import ResetPasswordRequest
from api.schemas.response import ApiException, ApiResponse, Error
from models.inactive_token import InactiveToken
from services.facebook_sso import get_facebook_sso
from services.github_sso import get_github_sso
from services.google_sso import get_google_sso
from services.microsoft_sso import get_microsoft_sso
from services.sms_sender import SMSSender
from mail.user_verification import UserVerification
from models.user import Contact, OAuthIDs, User
from models.base.enums import OTPOperationType, Status
from models.otp import Otp
from utils.helpers import escape_for_redis, special_to_underscore
from utils.jwt import JWTBearer, sign_jwt
from utils.password_hashing import verify_password
from utils.settings import settings
from fastapi_sso.sso.base import OpenID
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO
from fastapi_sso.sso.github import GithubSSO
from fastapi_sso.sso.microsoft import MicrosoftSSO
from fastapi_sso.sso.base import SSOBase

router = APIRouter()


@router.post("/generate-otp", response_model_exclude_none=True)
async def generate_otp(request: OTPRequest):
    user: User | None = await User.find(
        f"@contact_email:{escape_for_redis(request.email)}"
        if request.email
        else f"@contact_mobile:{request.mobile}"
    )
    exception_message: str | None = None
    if (
        request.operation_type
        in [
            OTPOperationType.register,
            OTPOperationType.update_profile,
        ]
        and user
    ):
        exception_message = "User already exist"
    elif (
        request.operation_type
        in [
            OTPOperationType.login,
            OTPOperationType.forgot_password,
        ]
        and not user
    ):
        exception_message = "User doesn't exist"

    if exception_message:
        raise ApiException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error=Error(type="otp", code=307, message=exception_message),
        )

    if request.email:
        email_otp: Otp = await Otp.create(
            shortname=special_to_underscore(request.email),
            operation_type=request.operation_type,
        )
        await UserVerification.send(request.email, email_otp.value)

    if request.mobile:
        mobile_otp: Otp = await Otp.create(
            shortname=request.mobile,
            operation_type=request.operation_type,
        )
        await SMSSender.send(request.mobile, mobile_otp.value)

    return ApiResponse(status=Status.success, message="OTP sent successfully")


@router.post("/register", response_model_exclude_none=True)
async def register(response: Response, request: RegisterRequest):
    is_valid_otp = await Otp.validate_otp_from_request(
        request.contact.model_dump(), OTPOperationType.register
    )

    if not is_valid_otp:
        raise ApiException(
            status_code=404,
            error=Error(type="otp", code=307, message="Invalid OTP"),
        )

    user_model = User(
        **request.model_dump(
            exclude={
                "is_oodi_mobile_active",
            },
            exclude_none=True,
        ),
    )

    await user_model.store()

    access_token = sign_jwt(
        {"username": user_model.shortname}, settings.jwt_access_expires
    )

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
        message="Account created successfully",
        data={
            "user": user_model.represent(),
            "token": access_token,
        },
    )


@router.post("/login", response_model_exclude_none=True)
async def login(response: Response, request: LoginRequest):
    user: User | None = await User.find(
        f"@contact_email:{escape_for_redis(request.email)}"
        if request.email
        else f"@contact_mobile:{request.mobile}"
    )

    if not user or (
        request.password
        and user.password
        and not verify_password(request.password, user.password)
    ):
        raise ApiException(
            status_code=401,
            error=Error(type="auth", code=14, message="Invalid Credentials"),
        )

    if not request.password:
        is_valid_otp: bool = await Otp.validate_otp_from_request(
            request.model_dump(exclude_none=True), OTPOperationType.login
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


@router.post("/reset-password", response_model_exclude_none=True)
async def reset_password(request: ResetPasswordRequest):
    user: User | None = await User.find(
        f"@contact_email:{escape_for_redis(request.email)}"
        if request.email
        else f"@contact_mobile:{request.mobile}"
    )
    if not user:
        raise ApiException(
            status_code=404,
            error=Error(type="db", code=12, message="User not found"),
        )

    otp_value = await Otp.find_and_remove(
        shortname=special_to_underscore(request.email)
        if request.email
        else request.mobile,
        operation_type=OTPOperationType.forgot_password,
    )

    if otp_value is None or otp_value != request.otp:
        return ApiResponse(
            status=Status.failed,
            error=Error(type="otp", code=307, message="invalid_otp"),
        )

    user.password = request.password
    await user.sync(updated={"password"})

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


@router.post("/github/login")
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


@router.post("/microsoft/login")
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
        if not provider_user.email:
            raise ApiException(
                status_code=400,
                error=Error(
                    type="data",
                    code=12,
                    message="User email is not retrieved from the provider",
                ),
            )
    user_model: User | None = await User.find(
        search=f"@oauth_ids_{provider}_id:{provider_user.id}"
    )

    if not user_model:
        try:
            oauth_ids = OAuthIDs()
            setattr(oauth_ids, f"{provider}_id", provider_user.id)
            user_model = User(
                first_name=provider_user.first_name or "",
                last_name=provider_user.last_name or "",
                contact=Contact(email=provider_user.email),
                oauth_ids=oauth_ids,
            )

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
    await InactiveToken.create(
        shortname=decoded_data.get("token", ""),
        expires=str(decoded_data.get("expires")),
    )

    response.set_cookie(
        value="",
        max_age=0,
        key="auth_token",
        httponly=True,
        secure=True,
        samesite="none",
    )

    return ApiResponse(status=Status.success, message="Logged out successfully")
