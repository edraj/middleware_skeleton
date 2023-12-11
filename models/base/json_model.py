from typing import TypeVar
from fastapi.logger import logger
from pydantic import BaseModel, Field

from models.base.enums import ResourceType, Schema, Space
from utils.dmart import dmart
from utils.helpers import snake_case
from utils import regex


model_data_mapper: dict = {
    "user": {"subpath": "users", "schema": Schema.user},
    "otp": {"subpath": "otps", "schema": Schema.otp},
    "inactive_token": {"subpath": "inactive_tokens", "schema": Schema.inactive_token},
    "order": {"subpath": "orders", "schema": Schema.order},
}


TJsonModel = TypeVar("TJsonModel", bound="JsonModel")


class JsonModel(BaseModel):
    shortname: str = Field(default=None, pattern=regex.NAME)

    def __init__(self, **data):
        BaseModel.__init__(self, **data)

    @classmethod
    def payload_body_attributes(cls) -> list:
        cls_fields = list(cls.model_json_schema().get("properties").keys())
        cls_fields.remove("shortname")
        return cls_fields

    @classmethod
    def class_attributes(self) -> list:
        return []

    async def store(self, resource_type: ResourceType = ResourceType.content) -> None:
        model_name = snake_case(self.__class__.__name__)
        result = await dmart.create(
            space_name=Space.acme,
            subpath=model_data_mapper[model_name]["subpath"],
            shortname=self.shortname if self.shortname else "auto",
            attributes={
                **self.model_dump(exclude_none=True, include=self.class_attributes()),
                **{
                    "is_active": True,
                    "payload": {
                        "content_type": "json",
                        "schema_shortname": model_data_mapper[model_name]["schema"],
                        "body": self.model_dump(
                            exclude_none=True, include=self.payload_body_attributes()
                        ),
                    },
                },
            },
            resource_type=resource_type,
        )
        self.shortname = result["records"][0]["shortname"]

    async def sync(self, resource_type: ResourceType = ResourceType.content) -> None:
        model_name = snake_case(self.__class__.__name__)
        await dmart.update(
            space_name=Space.acme,
            subpath=model_data_mapper[model_name]["subpath"],
            shortname=self.shortname,
            attributes={
                **self.model_dump(exclude_none=True, include=self.class_attributes()),
                **{
                    "is_active": True,
                    "payload": {
                        "content_type": "json",
                        "schema_shortname": model_data_mapper[model_name]["schema"],
                        "body": self.model_dump(
                            exclude_none=True, include=self.payload_body_attributes()
                        ),
                    },
                },
            },
            resource_type=resource_type,
        )

    async def delete(self, resource_type: ResourceType = ResourceType.content) -> None:
        model_name = snake_case(self.__class__.__name__)
        await dmart.delete(
            space_name=Space.acme,
            subpath=model_data_mapper[model_name]["subpath"],
            shortname=self.shortname,
            resource_type=resource_type,
        )

    @classmethod
    def payload_to_model(cls, attributes: dict, shortname: str) -> TJsonModel | None:
        try:
            payload_body_attributes = cls.payload_body_attributes()
            class_attributes = cls.class_attributes()
            model_fields = {}
            for key, value in attributes.items():
                if key in class_attributes:
                    model_fields[key] = value
            for key, value in attributes.get("payload", {}).get("body", {}).items():
                if key in payload_body_attributes:
                    model_fields[key] = value

            class_model = cls(**model_fields)
            class_model.shortname = shortname
        except Exception as e:
            logger.warn(
                "Failed payload_to_model", extra={"data": attributes, "error": e}
            )
            return None
        return class_model

    @classmethod
    async def get(cls: type[TJsonModel], shortname: str) -> TJsonModel | None:
        model_name = snake_case(cls.__name__)
        try:
            data: dict = await dmart.read(
                space_name=Space.acme,
                subpath=model_data_mapper[model_name]["subpath"],
                shortname=shortname,
            )
            return cls.payload_to_model(
                attributes=data,
                shortname=data.get("shortname"),
            )
        except Exception as _:
            return None

    @classmethod
    async def find(cls: type[TJsonModel], search: str) -> TJsonModel | None:
        model_name = snake_case(cls.__name__)
        result = await dmart.query(
            space_name=Space.acme,
            subpath=model_data_mapper.get(model_name, {}).get("subpath"),
            search=search,
            filter_schema_names=[model_data_mapper.get(model_name, {}).get("schema")],
        )
        if not result.get("records"):
            return None

        return cls.payload_to_model(
            attributes=result["records"][0]["attributes"],
            shortname=result["records"][0]["shortname"],
        )

    @classmethod
    async def search(
        cls: type[TJsonModel],
        search: str,
        filter_types: list = [],
        retrieve_attachments: bool = False,
    ) -> list[TJsonModel]:
        model_name = snake_case(cls.__name__)
        result = await dmart.query(
            space_name=Space.acme,
            subpath=model_data_mapper.get(model_name, {}).get("subpath"),
            search=search,
            filter_schema_names=[model_data_mapper.get(model_name, {}).get("schema")],
            filter_types=filter_types,
            retrieve_attachments=retrieve_attachments,
        )

        models = []

        for record in result.get("records", []):
            models.append(
                cls.payload_to_model(
                    attributes=record["attributes"],
                    shortname=record["shortname"],
                )
            )

        return models
