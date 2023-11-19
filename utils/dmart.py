import aiohttp
from models.enums import Space
from utils.settings import settings
from enum import Enum
from typing import Any
from fastapi import status
from api.schemas.response import ApiException, Error


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

    def get_headers(self):
        return {
            "Content-Type": "application/json",
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

    async def __api(self, endpoint, method: RequestMethod, json=None) -> dict:
        resp_json = {}
        response: aiohttp.ClientResponse | None = None
        for _ in range(3):
            url = f"{settings.dmart_url}{endpoint}"
            try:
                async with aiohttp.ClientSession() as session:
                    response = await getattr(session, method.value)(
                        url, headers=self.get_headers(), json=json
                    )
                    # if json:
                    #     response = await session.post(
                    #         url, headers=self.get_headers(), json=json
                    #     )
                    # else:
                    #     response = await session.get(url, headers=self.get_headers())

                    resp_json = await response.json()

                if (
                    resp_json
                    and resp_json.get("status", None) == "failed"
                    and resp_json.get("error", {}).get("type", None) == "jwtauth"
                ):
                    await self.login()
                    raise ConnectionError()

                break
            except ConnectionError:
                continue

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
    ) -> dict:
        return await self.__api(
            "/managed/request",
            RequestMethod.post,
            {
                "space_name": space_name,
                "request_type": request_type,
                "records": [
                    {
                        "resource_type": "content",
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
    ) -> dict:
        return await self.__request(
            space_name, subpath, shortname, RequestType.create, attributes
        )

    async def read(self, space_name: Space, subpath: str, shortname: str) -> dict:
        return await self.__api(
            f"/managed/entry/content/{space_name}/{subpath}/{shortname}",
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
        self, space_name: Space, subpath, shortname, attributes: dict
    ) -> dict:
        return await self.__request(
            space_name, subpath, shortname, RequestType.update, attributes
        )

    async def delete(self, space_name: Space, subpath, shortname) -> dict:
        json = {
            "space_name": space_name,
            "request_type": RequestType.delete,
            "records": [
                {
                    "resource_type": "content",
                    "subpath": subpath,
                    "shortname": shortname,
                    "attributes": {},
                }
            ],
        }
        return await self.__api("/managed/request", RequestMethod.post, json)


dmart = DMart()
