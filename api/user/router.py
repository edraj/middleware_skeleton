from fastapi import APIRouter, Depends
from api.schemas.response import ApiException, ApiResponse, Error
from api.user.Requests.user_update_request import UserUpdateRequest
from models.base.enums import Status
from models.otp import Otp
from models.user import User
from utils.jwt import JWTBearer


router = APIRouter()


@router.get(path="")
async def profile(shortname: str = Depends(JWTBearer())):
    user: User | None = await User.get(shortname)

    if not user:
        raise ApiException(
            status_code=404,
            error=Error(type="db", code=12, message="User not found"),
        )

    return ApiResponse(
        status=Status.success,
        message="User retrieved successfully",
        data={"user": user.represent()},
    )


@router.put("", response_model_exclude_none=True)
async def update(request: UserUpdateRequest, shortname: str = Depends(JWTBearer())):
    is_valid_otp = await Otp.validate_otps(request.model_dump())

    if not is_valid_otp:
        raise ApiException(
            status_code=404,
            error=Error(type="Invalid request", code=307, message="Invalid OTP"),
        )

    user: User = await User.get_or_fail(shortname)

    data = request.model_dump(exclude_none=True, exclude={"mobile_otp", "email_otp"})

    for key, value in data.items():
        setattr(user, key, value)

    await user.sync(updated=set(data.keys()))

    return ApiResponse(
        status=Status.success,
        message="Account updated successfully",
        data=user.represent(),
    )


@router.delete("", response_model_exclude_none=True)
async def delete(shortname: str = Depends(JWTBearer())):
    user: User = await User.get_or_fail(shortname)

    await user.delete()

    return ApiResponse(status=Status.success, message="Account delete successfully")
