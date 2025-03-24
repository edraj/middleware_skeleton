from fastapi import APIRouter
from pydmart.enums import Status
from pydmart.models import ApiResponse, ActionResponse, ApiResponseRecord

from api.dummy.services import get_dummies, insert_dummy, update_dummy, delete_dummy, get_dummy
from models.dummy import DummyData


router = APIRouter()

@router.get("/", response_model=ApiResponse, response_model_exclude_none=True)
async def fetch_all() -> ApiResponse:
    return await get_dummies()


@router.post("/", response_model=ApiResponse, response_model_exclude_none=True)
async def create(dummy: DummyData) -> ApiResponse:
    action : ActionResponse = await insert_dummy(dummy)
    return ApiResponse(status=Status.success, records=[ApiResponseRecord(shortname=one.shortname, resource_type=one.resource_type, subpath=one.subpath, attributes=one.attributes) for one in action.records])


@router.put("/{shortname}", response_model=ApiResponse, response_model_exclude_none=True)
async def update(shortname: str, dummy: DummyData) -> ApiResponse:
    action : ActionResponse = await update_dummy(shortname, dummy)
    return ApiResponse(status=Status.success, records=[ApiResponseRecord(shortname=one.shortname, resource_type=one.resource_type, subpath=one.subpath, attributes=one.attributes) for one in action.records])


@router.delete("/{shortname}", response_model=ApiResponse, response_model_exclude_none=True)
async def delete(shortname: str) -> ApiResponse:
    action : ActionResponse = await delete_dummy(shortname)
    return ApiResponse(status=Status.success, records=[ApiResponseRecord(shortname=one.shortname, resource_type=one.resource_type, subpath=one.subpath, attributes=one.attributes) for one in action.records])


@router.get("/{shortname}", response_model=ApiResponse, response_model_exclude_none=True)
async def fetch_by_shortname(shortname: str) -> ApiResponse:
    return await get_dummy(shortname)
