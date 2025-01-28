from fastapi import APIRouter
import models.api as api
from models.dummy import Dummy

router = APIRouter()


@router.get("/", response_model=api.Response, response_model_exclude_none=True)
async def fetch_dummies() -> api.Response:
    return api.Response(
        status=api.Status.success,
        records=[],
        attributes={"total": 0, "returned": len([])},
    )


@router.post("/", response_model=api.Response, response_model_exclude_none=True)
async def create_dummy(dummy: Dummy) -> api.Response:
    return api.Response(
        status=api.Status.success,
        records=[],
        attributes={"total": 0, "returned": len([])},
    )


@router.put("/", response_model=api.Response, response_model_exclude_none=True)
async def update_dummy(dummy: Dummy) -> api.Response:
    return api.Response(
        status=api.Status.success,
        records=[],
        attributes={"total": 0, "returned": len([])},
    )


@router.delete("/", response_model=api.Response, response_model_exclude_none=True)
async def delete_dummy() -> api.Response:
    return api.Response(
        status=api.Status.success,
        records=[],
        attributes={"total": 0, "returned": len([])},
    )


@router.get("/{shortname}", response_model=api.Response, response_model_exclude_none=True)
async def fetch_by_shortname_dummy(shortname: str) -> api.Response:
    return api.Response(
        status=api.Status.success,
        records=[],
        attributes={"total": 0, "returned": len([])},
    )
