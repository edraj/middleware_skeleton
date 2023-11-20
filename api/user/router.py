from fastapi import APIRouter, Depends
from api.schemas.response import ApiException, ApiResponse, Error
from models.enums import Status
from models.user import User
from utils.jwt import JWTBearer


router = APIRouter()


@router.get("/profile")
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
