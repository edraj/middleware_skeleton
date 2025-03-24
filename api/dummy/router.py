from fastapi import APIRouter
from pydmart.models import ApiResponse

from api.dummy.services import get_dummies, insert_dummy, update_dummy, delete_dummy, get_dummy
from models.dummy import DummyData

router = APIRouter()

@router.get("/", response_model=ApiResponse, response_model_exclude_none=True)
async def fetch_all() -> ApiResponse:
    return await get_dummies()


@router.post("/", response_model=ApiResponse, response_model_exclude_none=True)
async def create(dummy: DummyData) -> ApiResponse:
    return await insert_dummy(dummy)


@router.put("/{shortname}", response_model=ApiResponse, response_model_exclude_none=True)
async def update(shortname: str, dummy: DummyData) -> ApiResponse:
    return await update_dummy(shortname, dummy)


@router.delete("/{shortname}", response_model=ApiResponse, response_model_exclude_none=True)
async def delete(shortname: str) -> ApiResponse:
    return await delete_dummy(shortname)


@router.get("/{shortname}", response_model=ApiResponse, response_model_exclude_none=True)
async def fetch_by_shortname(shortname: str) -> ApiResponse:
    return await get_dummy(shortname)
