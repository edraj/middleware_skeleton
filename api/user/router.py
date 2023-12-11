from fastapi import APIRouter, Depends
from api.schemas.response import ApiException, ApiResponse, Error
from api.user.Requests.user_update_request import UserUpdateRequest
from models.base.enums import Status
from models.user import User
from utils.jwt import JWTBearer


router = APIRouter()


@router.get("")
async def profile(shortname=Depends(JWTBearer())):
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
async def update(request: UserUpdateRequest, shortname=Depends(JWTBearer())):
    user: User | None = await User.get(shortname)

    data = request.model_dump(exclude_none=True)

    for key, value in data.items():
        setattr(user, key, value)

    await user.sync(list(data.keys()))

    return ApiResponse(
        status=Status.success,
        message="Account updated successfully",
        data=user.represent(),
    )


@router.delete("", response_model_exclude_none=True)
async def delete(shortname=Depends(JWTBearer())):
    user: User | None = await User.get(shortname)

    await user.delete()

    return ApiResponse(status=Status.success, message="Account delete successfully")
