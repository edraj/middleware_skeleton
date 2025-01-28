from pydmart.service import ResourceType, DmartException, DmartResponse

from models.dummy import DummyData
from utils.dmart import dmart


async def insert_dummy(data: DummyData) -> DmartResponse:
    try:
        return await dmart.create(
            space_name="dummy_space",
            subpath="dummy_subpath",
            attributes={
                "is_active": True,
                "relationships": [],
                "payload": {
                    "content_type": "json",
                    "schema_shortname": "dummy_schema",
                    "body": data.model_dump()
                }
            },
            resource_type=ResourceType.content
        )
    except DmartException as e:
        raise e

async def get_dummies() -> DmartResponse:
    try:
        response = await dmart.query(
            space_name="dummy_space",
            subpath="dummy_subpath",
        )
        return response
    except DmartException as e:
        raise e


async def get_dummy(shortname: str) -> DmartResponse:
    try:
        response = await dmart.query(
            space_name="dummy_space",
            subpath="dummy_subpath",
            filter_shortnames=[shortname]
        )
        return response
    except DmartException as e:
        raise e

async def update_dummy(shortname: str, data: DummyData) -> DmartResponse:
    try:
        return await dmart.update(
            space_name="dummy_space",
            subpath="dummy_subpath",
            shortname=shortname,
            attributes={
                "is_active": True,
                "relationships": [],
                "payload": {
                    "content_type": "json",
                    "schema_shortname": "dummy_schema",
                    "body": data.model_dump()
                }
            },
            resource_type=ResourceType.content
        )
    except DmartException as e:
        raise e

async def delete_dummy(shortname: str) -> DmartResponse:
    try:
        return await dmart.delete(
            space_name="dummy_space",
            subpath="dummy_subpath",
            shortname=shortname,
        )
    except DmartException as e:
        raise e