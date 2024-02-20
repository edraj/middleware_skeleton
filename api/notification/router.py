from fastapi import APIRouter, Depends
from api.schemas.response import ApiResponse
from models.base.enums import Status
from models.notification import Notification
from models.user import User

from utils.jwt import JWTBearer


router = APIRouter()


@router.get(path="")
async def list(shortname: str = Depends(JWTBearer())):
    user: User = await User.get_or_fail(shortname)

    return ApiResponse(
        status=Status.success,
        message="Notifications retrieved successfully",
        data={"notifications": await user.notifications()},
    )


@router.patch(path="/mark-as-read/{notification_shortname}")
async def mark_as_read(
    notification_shortname: str, _: str = Depends(JWTBearer())
):
    # user: User = await User.get_or_fail(shortname)

    notification: Notification = await Notification.get_or_fail(notification_shortname)
    
    notification.is_read = True
    await notification.sync()
    await notification.refresh()
    
    return ApiResponse(
        status=Status.success,
        message="Notification updated successfully",
        data={"notification": notification},
    )


@router.delete(path="/{notification_shortname}")
async def delete(
    notification_shortname: str, _: str = Depends(JWTBearer())
):
    # user: User = await User.get_or_fail(shortname)

    notification: Notification = await Notification.get_or_fail(notification_shortname)
    
    await notification.delete()
    
    return ApiResponse(
        status=Status.success,
        message="Notification updated successfully",
        data={"notification": notification},
    )