from uuid import uuid4
import aiohttp

from models.core import Space, Schema
from utils.settings import settings
from enum import Enum
from typing import Any
from fastapi import status
from models.api import Exception, Error
import json_logging


class RequestType(str, Enum):
    create = "create"
    update = "update"
    delete = "delete"


class DMart:
    auth_token = ""

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "X-Correlation-ID": json_logging.get_correlation_id(),
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

    async def __api(self, endpoint, json=None):
        resp_json = {}
        response: aiohttp.ClientResponse | None = None
        for _ in range(3):
            url = f"{settings.dmart_url}{endpoint}"
            try:
                async with aiohttp.ClientSession() as session:
                    if json:
                        response = await session.post(
                            url, headers=self.get_headers(), json=json
                        )
                    else:
                        response = await session.get(url, headers=self.get_headers())

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
        if response is not None and response.status != 200:
            message = resp_json.get("error", {}).get("message", {})
            raise Exception(
                status_code=status.HTTP_400_BAD_REQUEST,
                error=Error(
                    type="dmart",
                    code=260,
                    message=[
                        {"endbpoint": endpoint},
                        {"response": message},
                    ],
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
    ):
        endpoint = "/managed/request"
        json = {
            "space_name": space_name.value,
            "request_type": request_type,
            "records": [
                {
                    "resource_type": "content",
                    "subpath": subpath,
                    "shortname": shortname,
                    "attributes": attributes,
                }
            ],
        }
        return await self.__api(endpoint, json)

    async def delete(self, space_name: Space, subpath, shortname):
        endpoint = "/managed/request"
        resource_type = "content"
        json = {
            "space_name": space_name,
            "request_type": "delete",
            "records": [
                {
                    "resource_type": resource_type,
                    "subpath": subpath,
                    "shortname": shortname,
                    "attributes": {},
                }
            ],
        }
        return await self.__api(endpoint, json)

    # Used in user and gift
    async def get_payload(self, space_name: Space, subpath, shortname):
        endpoint = f"{settings.dmart_url}/managed/payload/content/{space_name.value}/{subpath}/{shortname}.json"
        for _ in range(3):
            try:
                async with aiohttp.ClientSession(
                    headers=self.get_headers()
                ) as requests:
                    response = await requests.get(endpoint)
                    json = await response.json()

                    if (
                        json.get("status", None) == "failed"
                        and json.get("error", {}).get("type", None) == "jwtauth"
                    ):
                        await self.login()
                        raise ConnectionError()
                    if response.status != 200:
                        return None
                    return json
            except ConnectionError:
                continue

    async def query_user(self, space_name: Space, mssidn):
        endpoint = f"/managed/entry/content/{space_name.value}/users/{mssidn}?retrieve_json_payload=true"
        return await self.__api(endpoint)

    async def search(
        self, space_name: Space, subpath, content, filter_schema_names=[], **kwargs
    ) -> dict:
        endpoint = f"/managed/query"
        json = {
            "type": "search",
            "space_name": space_name.value,
            "subpath": subpath,
            "retrieve_json_payload": True,
            "filter_schema_names": filter_schema_names,
            "search": content,
            **kwargs,
        }
        return await self.__api(endpoint, json)

    async def query(self, space_name: Space, subpath, filter_shortnames=[]):
        endpoint = "/managed/query"
        json = {
            "type": "subpath",
            "space_name": space_name,
            "subpath": subpath,
            "filter_shortnames": filter_shortnames,
            "retrieve_json_payload": True,
        }
        return await self.__api(endpoint, json)

    # User in user
    async def update(
        self,
        space_name: Space,
        subpath,
        shortname,
        schema: Schema,
        payload: dict[str, Any],
        displayname: dict[str, str] | None = None,
    ):
        attributes: dict[str, Any] = {
            "payload": {
                "schema_shortname": schema,
                "content_type": "json",
                "body": payload,
            }
        }
        if displayname is not None and displayname.get("en"):
            attributes["displayname"] = displayname

        return await self.__request(
            space_name, subpath, shortname, RequestType.update, attributes
        )

    # Used in user, gift, offer, voucher and subaccount
    async def create(
        self,
        space_name: Space,
        subpath,
        schema: Schema,
        payload: dict[str, Any],
        shortname=None,
        displayname=None,
    ):
        attributes = {
            "is_active": True,
            "displayname": displayname,
            "payload": {
                "schema_shortname": schema,
                "content_type": "json",
                "body": payload,
            },
        }
        if shortname is None:
            attributes["uuid"] = str(uuid4())
            shortname = attributes["uuid"][:8]

        return await self.__request(
            space_name, subpath, shortname, RequestType.create, attributes
        )


dmart = DMart()
