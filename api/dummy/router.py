from fastapi import APIRouter
import models.api as api

router = APIRouter()


@router.get("/", response_model=api.Response, response_model_exclude_none=True)
async def fetch_dummies() -> api.Response:
    return api.Response(
        status=api.Status.success,
        records=[],
        attributes={"total": 0, "returned": len([])},
    )


@router.get("/", response_model=api.Response, response_model_exclude_none=True)
async def create_dummy() -> api.Response:
    return api.Response(
        status=api.Status.success,
        records=[],
        attributes={"total": 0, "returned": len([])},
    )


@router.get("/", response_model=api.Response, response_model_exclude_none=True)
async def update_dummy() -> api.Response:
    return api.Response(
        status=api.Status.success,
        records=[],
        attributes={"total": 0, "returned": len([])},
    )


@router.get("/", response_model=api.Response, response_model_exclude_none=True)
async def delete_dummy() -> api.Response:
    return api.Response(
        status=api.Status.success,
        records=[],
        attributes={"total": 0, "returned": len([])},
    )


@router.get("/", response_model=api.Response, response_model_exclude_none=True)
async def fetch_by_id_dummy() -> api.Response:
    return api.Response(
        status=api.Status.success,
        records=[],
        attributes={"total": 0, "returned": len([])},
    )
