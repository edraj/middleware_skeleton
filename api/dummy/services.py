from typing import Union

from pydmart.enums import ResourceType, RequestType, QueryType
from pydmart.models import ApiResponse, DmartException, QueryRequest, ActionRequest, ActionRequestRecord

from models.dummy import DummyData

from utils.dmart import dmart


async def insert_dummy(data: DummyData) -> Union[ApiResponse|DmartException]:
    try:
        return await dmart.request(
            ActionRequest(
                space_name="dummy_space",
                request_type=RequestType.create,
                records=[
                    ActionRequestRecord(
                        shortname='auto',
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
                ]
            )

        )
    except DmartException as e:
        return e

async def get_dummies() -> Union[ApiResponse|DmartException]:
    try:
        response = await dmart.query(
            QueryRequest(
                type=QueryType.search,
                space_name="dummy_space",
                subpath="dummy_subpath",
                search='',
                retrieve_json_payload=True,
                retrieve_attachments=True,
            )
        )
        print("response", response)
        return response
    except DmartException as e:
        return e


async def get_dummy(shortname: str) -> Union[ApiResponse|DmartException]:
    try:
        response = await dmart.query(
            QueryRequest(
                type=QueryType.search,
                space_name="dummy_space",
                subpath="dummy_subpath",
                filter_shortnames=[shortname],
                search='',
                retrieve_json_payload = True,
                retrieve_attachments = True,
            )
        )
        return response
    except DmartException as e:
        return e

async def update_dummy(shortname: str, data: DummyData) -> Union[ApiResponse|DmartException]:
    try:
        return await dmart.request(
            ActionRequest(
                space_name="dummy_space",
                request_type=RequestType.update,
                records=[
                    ActionRequestRecord(
                        shortname=shortname,
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
                ]
            )
        )
    except DmartException as e:
        return e

async def delete_dummy(shortname: str) -> Union[ApiResponse|DmartException]:
    try:
        return await dmart.request(
            ActionRequest(
                space_name="dummy_space",
                request_type=RequestType.delete,
                records=[
                    ActionRequestRecord(
                        subpath="dummy_subpath",
                        shortname=shortname,
                        attributes={},
                        resource_type=ResourceType.content
                    )
                ]
            )
        )
    except DmartException as e:
        return e
