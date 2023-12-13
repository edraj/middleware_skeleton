from typing import Annotated
from fastapi import Form, Depends, Path as PathParam
from fastapi.routing import APIRouter
from api.delivery.requests.create_delivery_request import CreateDeliveryRequest
from api.delivery.requests.update_delivery import UpdateDeliveryRequest
from api.schemas.response import ApiResponse
from models.base.enums import CancellationReason, DeliverStatus, Status
from fastapi.security import HTTPBearer
from fastapi import UploadFile
from models.order import Order

from utils.jwt import JWTBearer


router = APIRouter()


security = HTTPBearer()


@router.post("/create")
async def create_delivery(request: CreateDeliveryRequest, _=Depends(JWTBearer())):
    order_model = Order(
        **request.model_dump(exclude=["password_confirmation"], exclude_none=True)
    )

    await order_model.store()

    return ApiResponse(
        status=Status.success,
        message="Order created successfully",
        data=order_model.represent(),
    )


@router.get("/track/{shortname}")
async def track_delivery(
    shortname: Annotated[
        str, PathParam(examples=["b775fdbe"], description="Order shortname")
    ],
    _=Depends(JWTBearer()),
):
    order: Order = await Order.get_or_fail(shortname)

    return ApiResponse(
        status=Status.success,
        message="Order retrieved successfully",
        data={"order": order.represent()},
    )


@router.put("/cancel/{shortname}")
async def cancel_order(
    shortname: Annotated[
        str, PathParam(examples=["b775fdbe"], description="Order shortname")
    ],
    cancellation_reason: CancellationReason,
    _=Depends(JWTBearer()),
):
    order: Order = await Order.get_or_fail(shortname)

    await order.progress("cancel", cancellation_reason)

    order.resolution_reason = cancellation_reason

    await order.sync()

    return ApiResponse(
        status=Status.success,
        message="Order retrieved successfully",
        data={"order": order.represent()},
    )


@router.put("/assign/{shortname}")
async def assign_order(
    shortname: Annotated[
        str, PathParam(examples=["b775fdbe"], description="Order shortname")
    ],
    _=Depends(JWTBearer()),
):
    order: Order = await Order.get_or_fail(shortname)

    await order.progress("assign")

    return ApiResponse(
        status=Status.success,
        message="Order retrieved successfully",
        data={"order": order.represent()},
    )


@router.put("/update/{shortname}")
async def update_delivery(
    request: UpdateDeliveryRequest,
    shortname: Annotated[
        str, PathParam(examples=["f7bcb9fe"], description="Order shortname")
    ],
    _=Depends(JWTBearer()),
):
    order: Order = await Order.get_or_fail(shortname)

    data = request.model_dump(exclude_none=True)

    for key, value in data.items():
        setattr(order, key, value)

    await order.sync()

    return ApiResponse(
        status=Status.success,
        message="Order updated successfully",
        data=order.represent(),
    )


@router.post("/query")
async def order_query(delivery_status: DeliverStatus, _=Depends(JWTBearer())):
    orders: list[Order] = await Order.search(
        search=f"@state:{delivery_status}",
        filter_types=["ticket", "media"],
        retrieve_attachments=True,
    )

    return ApiResponse(
        status=Status.success,
        message="Orders retrieved successfully",
        data={"count": len(orders), "orders": orders},
    )


@router.post("/{shortname}/attach")
async def upload_attachment(
    file: UploadFile,
    shortname: Annotated[
        str, PathParam(examples=["b775fdbe"], description="order shortname")
    ],
    document_name: Annotated[
        str, Form(examples=["front_citizen_id"], description="document name")
    ],
    _=Depends(JWTBearer()),
):
    order: Order = await Order.get_or_fail(shortname)

    attached = await order.attach(
        payload=file.file,
        payload_file_name=file.filename,
        payload_mime_type=file.content_type,
        entry_shortname=document_name,
    )

    if attached:
        return ApiResponse(status=Status.success, message="Media attached successfully")
    else:
        return ApiResponse(
            status=Status.failed,
            message="Failed to upload the attachment, please try again",
        )
