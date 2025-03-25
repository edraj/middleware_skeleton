from pydmart.enums import ResourceType, RequestType, QueryType
from pydmart.models import ApiResponse, ActionResponse, QueryRequest, ActionRequest, ActionRequestRecord
from models.dummy import DummyData
from utils.dmart import dmart


async def insert_dummy(data: DummyData) -> ActionResponse:
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

async def get_dummies() -> ApiResponse:
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


async def get_dummy(shortname: str) -> ApiResponse:
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

async def update_dummy(shortname: str, data: DummyData) -> ActionResponse:
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

async def delete_dummy(shortname: str) -> ActionResponse:
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
