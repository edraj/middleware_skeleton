import os
from typing import Annotated
from fastapi import Query, Depends, Path as PathParam
from fastapi.routing import APIRouter
from api.delivery.requests.create_delivery_request import CreateDeliveryRequest
from api.delivery.requests.update_delivery import UpdateDeliveryRequest
from api.schemas.response import ApiException, ApiResponse, Error
from models.base.enums import CancellationReason, DeliverStatus, Status
import requests
import json
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import UploadFile
from pathlib import Path
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
    order: Order | None = await Order.get(shortname)

    if not order:
        raise ApiException(
            status_code=404,
            error=Error(type="db", code=12, message="Order not found"),
        )

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
    order: Order | None = await Order.get(shortname)

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
    order: Order | None = await Order.get(shortname)

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
    order: Order | None = await Order.get(shortname)

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


@router.post("/attachments")
async def upload_attachment(
    file: UploadFile,
    shortname: Annotated[
        str, Query(examples=["b775fdbe"], description="order shortname")
    ],
    document_name: Annotated[
        str, Query(examples=["front_citizin_id"], description="document name ")
    ],
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    file.file
    # json file path
    token = credentials.credentials
    uploaded_document = await get_file(file)
    uploadAttachmentJson = await get_upload_attachment_json(document_name, shortname)
    files = [
        (
            "payload_file",
            (
                "App Store Badge US Black.png",
                open(uploaded_document, "rb"),
                "image/png",
            ),
        ),
        (
            "request_record",
            (
                "uploadAttachmentJson.json",
                open(uploadAttachmentJson, "rb"),
                "application/json",
            ),
        ),
    ]

    url = "https://api.oodi.iq/dmart/managed/resource_with_payload"
    payload = {"space_name": "acme"}
    headers = {"Cookie": f"auth_token={token}", "Authorization": f"Bearer {token}"}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    os.remove(uploaded_document)
    os.remove(uploadAttachmentJson)
    return response.json()


async def get_upload_attachment_json(document_name, shortname) -> str:
    upload_dir = Path()
    uploadAttachmentJson_path = "uploadAttachmentJson.json"
    json_data = {
        "attributes": {"is_active": True},
        "resource_type": "media",
        "shortname": document_name,
        "subpath": f"orders/{shortname}",
    }
    temp_uploadAttachmentJson_dir = upload_dir / uploadAttachmentJson_path
    # Serialize the JSON data and write it to the file
    with open(temp_uploadAttachmentJson_dir, "w") as json_file:
        json.dump(json_data, json_file)
    return temp_uploadAttachmentJson_dir


async def get_file(file) -> str:
    upload_dir = Path()
    data = await file.read()
    temp_save = upload_dir / file.filename
    with open(temp_save, "wb") as f:
        f.write(data)
    return temp_save
