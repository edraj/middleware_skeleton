from fastapi import APIRouter, Depends
from api.schemas.response import ApiException, ApiResponse, Error
from api.user.requests.user_update_request import UserUpdateRequest
from models.base.enums import OTPOperationType, Status
from models.otp import Otp
from models.user import User
from utils.jwt import JWTBearer


router = APIRouter()


@router.get(path="")
async def profile(shortname: str = Depends(JWTBearer())):
    user: User = await User.get_or_fail(shortname)

    return ApiResponse(
        status=Status.success,
        message="User retrieved successfully",
        data={"user": user.represent()},
    )


@router.put("", response_model_exclude_none=True)
async def update(request: UserUpdateRequest, shortname: str = Depends(JWTBearer())):
    if request.contact and not await Otp.validate_otp_from_request(
        request.contact.model_dump(), OTPOperationType.update_profile
    ):
        raise ApiException(
            status_code=404,
            error=Error(type="Invalid request", code=307, message="Invalid OTP"),
        )

    user: User = await User.get_or_fail(shortname)

    data = request.model_dump(exclude_none=True)
    data.get("contact", {}).pop("email_otp", None)
    data.get("contact", {}).pop("mobile_otp", None)

    updated_user = User(shortname=user.shortname, **data)
    await updated_user.sync(updated=set(data.keys()))

    return ApiResponse(
        status=Status.success,
        message="Account updated successfully",
        data=updated_user.represent(),
    )


@router.delete("", response_model_exclude_none=True)
async def delete(shortname: str = Depends(JWTBearer())):
    user: User = await User.get_or_fail(shortname)

    await user.delete()

    return ApiResponse(status=Status.success, message="Account delete successfully")
