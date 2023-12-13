from io import BytesIO
import json
import aiohttp
from models.base.enums import CancellationReason, ResourceType, Space
from utils.settings import settings
from enum import Enum
from typing import Any
from fastapi import status
from api.schemas.response import ApiException, Error
from fastapi.logger import logger


class RequestType(str, Enum):
    create = "create"
    read = "read"
    update = "update"
    delete = "delete"


class RequestMethod(str, Enum):
    get = "get"
    post = "post"
    delete = "delete"
    put = "put"
    patch = "patch"


class DMart:
    auth_token = ""

    @property
    def json_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
        }

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.auth_token}",
        }

    async def login(self):
        async with aiohttp.ClientSession() as session:
            json = {
                "shortname": settings.dmart_username,
                "password": settings.dmart_password,
            }
            url = f"{settings.dmart_url}/user/login"
            response = await session.post(
                url,
                headers=self.get_headers(),
                json=json,
            )
            resp_json = await response.json()
            if (
                resp_json["status"] == "failed"
                and resp_json["error"]["type"] == "jwtauth"
            ):
                raise ConnectionError()

            self.auth_token = resp_json["records"][0]["attributes"]["access_token"]

    async def __api(
        self,
        endpoint,
        method: RequestMethod,
        json=None,
        data=None,
    ) -> dict:
        if not self.auth_token:
            await self.login()

        resp_json = {}
        response: aiohttp.ClientResponse | None = None
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.request(
                    method.value,
                    f"{settings.dmart_url}{endpoint}",
                    headers=self.json_headers if json else self.headers,
                    json=json if not data else None,
                    data=data if data else None,
                )
                resp_json = await response.json()

        except ConnectionError as e:
            logger.warn(
                "Failed request to Dmart core",
                {
                    "endpoint": endpoint,
                    "method": method,
                    "json": json,
                    "data": data,
                    "error": e.args,
                },
            )

        if response is None or response.status != 200:
            message = resp_json.get("error", {}).get("message", {})
            raise ApiException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error=Error(
                    type="dmart",
                    code=260,
                    message=f"{message} AT {endpoint}",
                    info=resp_json.get("error", {}).get("info", None),
                ),
            )

        return resp_json

    async def __request(
        self,
        space_name: Space,
        subpath,
        shortname,
        request_type: RequestType,
        attributes: dict[str, Any] = {},
        resource_type: ResourceType = ResourceType.content,
    ) -> dict:
        return await self.__api(
            "/managed/request",
            RequestMethod.post,
            {
                "space_name": space_name,
                "request_type": request_type,
                "records": [
                    {
                        "resource_type": resource_type,
                        "subpath": subpath,
                        "shortname": shortname,
                        "attributes": attributes,
                    }
                ],
            },
        )

    async def create(
        self,
        space_name: Space,
        subpath: str,
        attributes: dict,
        shortname: str = "auto",
        resource_type: ResourceType = ResourceType.content,
    ) -> dict:
        return await self.__request(
            space_name,
            subpath,
            shortname,
            RequestType.create,
            attributes,
            resource_type,
        )

    async def upload_resource_with_payload(
        self,
        space_name: Space,
        record: dict,
        payload: BytesIO,
        payload_file_name: str,
        payload_mime_type: str,
    ):
        record_file = BytesIO(bytes(json.dumps(record), "utf-8"))

        data = aiohttp.FormData()
        data.add_field(
            "request_record",
            record_file,
            filename="record.json",
            content_type="application/json",
        )
        data.add_field(
            "payload_file",
            payload,
            filename=payload_file_name,
            content_type=payload_mime_type,
        )
        data.add_field("space_name", space_name)

        return await self.__api(
            endpoint="/managed/resource_with_payload",
            method=RequestMethod.post,
            data=data,
        )

    async def read(
        self,
        space_name: Space,
        subpath: str,
        shortname: str,
        retrieve_attachments: bool = False,
        resource_type: ResourceType = ResourceType.content,
    ) -> dict:
        return await self.__api(
            (
                f"/managed/entry/{resource_type}/{space_name}/{subpath}/{shortname}"
                f"?retrieve_json_payload=true&retrieve_attachments={retrieve_attachments}"
            ),
            RequestMethod.get,
        )

    async def read_json_payload(self, space_name: Space, subpath, shortname) -> dict:
        return await self.__api(
            f"/managed/payload/content/{space_name}/{subpath}/{shortname}.json",
            RequestMethod.get,
        )

    async def query(
        self,
        space_name: Space,
        subpath: str,
        search: str = "",
        filter_schema_names=[],
        **kwargs,
    ) -> dict:
        return await self.__api(
            "/managed/query",
            RequestMethod.post,
            {
                "type": "search",
                "space_name": space_name,
                "subpath": subpath,
                "retrieve_json_payload": True,
                "filter_schema_names": filter_schema_names,
                "search": search,
                **kwargs,
            },
        )

    async def update(
        self,
        space_name: Space,
        subpath,
        shortname,
        attributes: dict,
        resource_type: ResourceType = ResourceType.content,
    ) -> dict:
        return await self.__request(
            space_name,
            subpath,
            shortname,
            RequestType.update,
            attributes,
            resource_type,
        )

    async def progress_ticket(
        self,
        space_name: Space,
        subpath: str,
        shortname: str,
        action: str,
        cancellation_reasons: CancellationReason | None = None,
    ) -> dict:
        request_body = None
        if cancellation_reasons:
            request_body = {"resolution": cancellation_reasons}
        return await self.__api(
            (f"/managed/progress-ticket/{space_name}/{subpath}/{shortname}/{action}"),
            RequestMethod.put,
            json=request_body,
        )

    async def delete(
        self,
        space_name: Space,
        subpath,
        shortname,
        resource_type: ResourceType = ResourceType.content,
    ) -> dict:
        json = {
            "space_name": space_name,
            "request_type": RequestType.delete,
            "records": [
                {
                    "resource_type": resource_type,
                    "subpath": subpath,
                    "shortname": shortname,
                    "attributes": {},
                }
            ],
        }
        return await self.__api("/managed/request", RequestMethod.post, json)


dmart = DMart()
