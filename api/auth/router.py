import random
from typing import Annotated
from fastapi import APIRouter, Body, Depends, Query, Request
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
from models.enums import OTPFor, Status
from models.otp import Otp
from utils.helpers import escape_for_redis
from utils.jwt import JWTBearer, sign_jwt
from utils.password_hashing import hash_password, verify_password
from utils.settings import settings
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO
from fastapi_sso.sso.github import GithubSSO
from fastapi_sso.sso.microsoft import MicrosoftSSO

router = APIRouter()


@router.post("/register", response_model_exclude_none=True)
async def register(request: RegisterRequest):
    user_model = User(
        **request.model_dump(exclude=["password_confirmation"], exclude_none=True)
    )

    await user_model.store()

    return ApiResponse(
        status=Status.success,
        message="Account created successfully, please check your mail for the verification code",
        data=user_model.represent(),
    )


@router.post("/verify-email", response_model_exclude_none=True)
async def verify_email(
    email: Annotated[str, Body(examples=["myname@email.com"])],
    otp: Annotated[str, Body(examples=["123456"])],
):
    user: User | None = await User.find(f"@full_email:{{{escape_for_redis(email)}}}")

    if not user:
        raise ApiException(
            status_code=404,
            error=Error(type="db", code=12, message="User not found"),
        )

    if user.is_email_verified:
        raise ApiException(
            status_code=400,
            error=Error(
                type="db",
                code=12,
                message="User's email has already been verified, please go to login",
            ),
        )

    otp_model = Otp(
        user_shortname=user.shortname, otp=otp, otp_for=OTPFor.mail_verification
    )
    otp_exists = await otp_model.get_and_del()

    if not otp_exists:
        return ApiResponse(
            status=Status.failed,
            error=Error(type="Invalid request", code=307, message="Invalid OTP"),
        )

    user.is_email_verified = True
    await user.sync()

    return ApiResponse(status=Status.success, message="Email verified successfully")


@router.post("/verify-mobile", response_model_exclude_none=True)
async def verify_mobile(
    mobile: Annotated[str, Body(examples=["7999228903"])],
    otp: Annotated[str, Body(examples=["123456"])],
):
    user: User | None = await User.find(f"@mobile:{mobile}")

    if not user:
        raise ApiException(
            status_code=404,
            error=Error(type="db", code=12, message="User not found"),
        )

    if user.is_mobile_verified:
        raise ApiException(
            status_code=400,
            error=Error(
                type="db",
                code=12,
                message="User's mobile has already been verified, please go to login",
            ),
        )

    otp_model = Otp(
        user_shortname=user.shortname, otp=otp, otp_for=OTPFor.mobile_verification
    )
    otp_exists = await otp_model.get_and_del()

    if not otp_exists:
        return ApiResponse(
            status=Status.failed,
            error=Error(type="Invalid request", code=307, message="Invalid OTP"),
        )

    user.is_mobile_verified = True
    await user.sync()

    return ApiResponse(status=Status.success, message="mobile verified successfully")


@router.get("/resend-verification-email", response_model_exclude_none=True)
async def resend_verification_email(
    email: Annotated[str, Query(examples=["myname@email.com"])]
):
    user: User | None = await User.find(f"@full_email:{{{escape_for_redis(email)}}}")

    if not user or user.is_email_verified:
        raise ApiException(
            status_code=404,
            error=Error(
                type="db", code=33, message="User not found or already verified"
            ),
        )

    otp = Otp(
        user_shortname=user.shortname,
        otp_for=OTPFor.mail_verification,
        otp=f"{random.randint(111111, 999999)}",
    )
    await otp.store()

    await UserVerification.send(user.email, otp.otp)

    return ApiResponse(status=Status.success, message="Email sent successfully")


@router.get("/resend-verification-sms", response_model_exclude_none=True)
async def resend_verification_sms(
    mobile: Annotated[str, Query(examples=["7999228903"])]
):
    user: User | None = await User.find(f"@mobile:{mobile}")

    if not user or user.is_mobile_verified:
        raise ApiException(
            status_code=404,
            error=Error(
                type="db", code=33, message="User not found or already verified"
            ),
        )

    otp = Otp(
        user_shortname=user.shortname,
        otp_for=OTPFor.mobile_verification,
        otp=f"{random.randint(111111, 999999)}",
    )
    await otp.store()

    await SMSSender.send(user.mobile, otp.otp)

    return ApiResponse(status=Status.success, message="SMS sent successfully")


@router.post("/login", response_model_exclude_none=True)
async def login(request: LoginRequest):
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

    if (
        not user
        or (
            (request.email and not user.is_email_verified)
            or (request.mobile and not user.is_mobile_verified)
        )
        or not verify_password(request.password, user.password)
    ):
        raise ApiException(
            status_code=401,
            error=Error(type="auth", code=14, message="Invalid Credentials"),
        )

    access_token = sign_jwt({"username": user.shortname}, settings.jwt_access_expires)

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


@router.get("/google/login")
async def google_login(google_sso: GoogleSSO = Depends(get_google_sso)):
    return await google_sso.get_login_redirect()


@router.get("/google/callback")
async def google_callback(
    request: Request, google_sso: GoogleSSO = Depends(get_google_sso)
):
    user = await google_sso.verify_and_process(request)
    user_model: User | None = await User.find(search=f"@google_id:{user.id}")

    if not user_model:
        user_model = User(
            google_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            is_email_verified=True,
            profile_pic_url=user.picture,
            password="GoogleAuthorized@dmart#2024",
        )

        await user_model.store(trigger_events=False)

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


@router.get("/facebook/login")
async def facebook_login(facebook_sso: FacebookSSO = Depends(get_facebook_sso)):
    return await facebook_sso.get_login_redirect()


@router.get("/facebook/callback")
async def facebook_callback(
    request: Request, facebook_sso: FacebookSSO = Depends(get_facebook_sso)
):
    user = await facebook_sso.verify_and_process(request)
    user_model: User | None = await User.find(search=f"@facebook_id:{user.id}")

    if not user_model:
        user_model = User(
            facebook_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            is_email_verified=True,
            profile_pic_url=user.picture,
            password="FacebookAuthorized@dmart#2024",
        )

        await user_model.store(trigger_events=False)

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
async def github_login(github_sso: GithubSSO = Depends(get_github_sso)):
    return await github_sso.get_login_redirect()


@router.get("/github/callback")
async def github_callback(
    request: Request, github_sso: GithubSSO = Depends(get_github_sso)
):
    user = await github_sso.verify_and_process(request)
    user_model: User | None = await User.find(search=f"@github_id:{user.id}")

    if not user_model:
        user_model = User(
            github_id=user.id,
            first_name=user.display_name,
            last_name="",
            email=user.email,
            is_email_verified=True,
            profile_pic_url=user.picture,
            password="GithubAuthorized@dmart#2024",
        )

        await user_model.store(trigger_events=False)

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
async def microsoft_login(microsoft_sso: MicrosoftSSO = Depends(get_microsoft_sso)):
    return await microsoft_sso.get_login_redirect()


@router.get("/microsoft/callback")
async def microsoft_callback(
    request: Request, microsoft_sso: MicrosoftSSO = Depends(get_microsoft_sso)
):
    user = await microsoft_sso.verify_and_process(request)
    user_model: User | None = await User.find(search=f"@microsoft_id:{user.id}")

    if not user_model:
        user_model = User(
            microsoft_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            is_email_verified=True,
            profile_pic_url=user.picture,
            password="MicrosoftAuthorized@dmart#2024",
        )

        await user_model.store(trigger_events=False)

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


@router.post("/logout")
async def logout(request: Request, shortname=Depends(JWTBearer())):
    user: User | None = await User.get(shortname)

    if not user:
        raise ApiException(
            status_code=404,
            error=Error(type="db", code=12, message="User not found"),
        )

    if user.firebase_token:
        user.firebase_token = None
        user.sync()

    decoded_data = await JWTBearer().extract_and_decode(request)
    inactive_token = InactiveToken(
        token=decoded_data.get("token"), expires=str(decoded_data.get("expires"))
    )
    await inactive_token.store()

    return ApiResponse(status=Status.success, message="Logged out successfully")
