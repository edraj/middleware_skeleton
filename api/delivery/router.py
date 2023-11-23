from typing import Annotated
from fastapi import Query
from fastapi.routing import APIRouter
from api.delivery.requests.deliveryRequest import DeliveryRequest, DeliveryStatus
from api.schemas.response import ApiResponse
from models.enums import Status



deliveryRouter = APIRouter()


@deliveryRouter.post('/create')
async def create_delivery(delivery_request: DeliveryRequest):

    return ApiResponse(status=Status.success,data={"deliveryData":delivery_request})


@deliveryRouter.get('/track')
async def track_delivery(id: Annotated[str, Query(example="87",description='delivery id')], ):
    return ApiResponse(message=f'your delivery with id {id} status',status=Status.success,data={"deliveryTrack": DeliveryStatus.progress})


@deliveryRouter.put('/update')
async def update_delivery(delivery_request: DeliveryRequest, id: Annotated[str, Query(example="87",description='delivery id')]):

    return ApiResponse(message=f'delivery with id {id} updated ',status=Status.success,data={"deliveryData":delivery_request})
