from api.schemas.response import ApiException, Error
from typing import Any, BinaryIO, Optional, Self, Type, TypeVar
from fastapi.logger import logger
from pydantic import BaseModel, Field

from models.base.enums import ResourceType, Schema, Space
from utils.dmart import dmart
from utils.helpers import snake_case
from utils import regex


model_data_mapper: dict[str, dict[str, str]] = {
    "user": {"subpath": "users", "schema": Schema.user},
    "otp": {"subpath": "otps", "schema": Schema.otp},
    "inactive_token": {"subpath": "inactive_tokens", "schema": Schema.inactive_token},
    "order": {"subpath": "orders", "schema": Schema.order},
}


TJsonModel = TypeVar("TJsonModel", bound="JsonModel")


class JsonModel(BaseModel):
    shortname: str = Field(default=None, pattern=regex.NAME)

    def __init__(self, **data: dict[str, Any]) -> None:
        BaseModel.__init__(self, **data)

    @classmethod
    def payload_body_attributes(cls) -> set[str]:
        cls_fields = set(cls.model_json_schema().get("properties", {}).keys())
        cls_fields.remove("shortname")
        return cls_fields

    @classmethod
    def class_attributes(cls) -> set[str]:
        return set()

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
    def payload_to_model(
        cls, attributes: dict[str, Any], shortname: str
    ) -> Optional[Self]:
        try:
            payload_body_attributes = cls.payload_body_attributes()
            class_attributes = cls.class_attributes()
            model_fields: dict[str, Any] = {}
            for key, value in attributes.items():
                if key in class_attributes:
                    model_fields[key] = value
            for key, value in attributes.get("payload", {}).get("body", {}).items():
                if key in payload_body_attributes:
                    model_fields[key] = value

            class_model: Self = cls(**model_fields)
            class_model.shortname = shortname
            return class_model
        except Exception as e:
            logger.warning(
                "Failed payload_to_model", extra={"data": attributes, "error": e}
            )
            return None

    @classmethod
    async def get(cls: Type[TJsonModel], shortname: str) -> TJsonModel | None:
        model_name = snake_case(cls.__name__)
        try:
            data: dict[str, Any] = await dmart.read(
                space_name=Space.acme,
                subpath=model_data_mapper[model_name]["subpath"],
                shortname=shortname,
                retrieve_attachments=True,
            )
            return cls.payload_to_model(
                attributes=data,
                shortname=data.get("shortname", ""),
            )
        except Exception as _:
            return None

    @classmethod
    async def get_or_fail(cls: type[TJsonModel], shortname: str) -> TJsonModel:
        model: TJsonModel | None = await cls.get(shortname)
        if not model:
            raise ApiException(
                status_code=404,
                error=Error(type="db", code=12, message="Model not found"),
            )
        return model

    async def refresh(self) -> None:
        model_name = snake_case(self.__class__.__name__)
        try:
            data: dict[str, Any] = await dmart.read(
                space_name=Space.acme,
                subpath=model_data_mapper[model_name]["subpath"],
                shortname=self.shortname,
                retrieve_attachments=True,
            )
            updated_model = self.__class__.payload_to_model(
                attributes=data,
                shortname=data.get("shortname", ""),
            )
            if updated_model:
                for key, val in updated_model.model_dump().items():
                    setattr(self, str(key), val)
        except Exception as e:
            logger.warn(f"Failed to refresh the model: {model_name}", {"error": e.args})

    @classmethod
    async def find(cls: type[TJsonModel], search: str) -> TJsonModel | None:
        model_name = snake_case(cls.__name__)
        result: dict[str, Any] = await dmart.query(
            space_name=Space.acme,
            subpath=model_data_mapper.get(model_name, {}).get("subpath", ""),
            search=search,
            filter_schema_names=[
                model_data_mapper.get(model_name, {}).get("schema", "")
            ],
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
        filter_types: list[str] = [],
        retrieve_attachments: bool = False,
    ) -> list[TJsonModel]:
        model_name = snake_case(cls.__name__)
        result = await dmart.query(
            space_name=Space.acme,
            subpath=model_data_mapper.get(model_name, {}).get("subpath", ""),
            search=search,
            filter_schema_names=[
                model_data_mapper.get(model_name, {}).get("schema", "")
            ],
            filter_types=filter_types,
            retrieve_attachments=retrieve_attachments,
        )

        models: list[Any] = []

        for record in result.get("records", []):
            record["attributes"]["attachments"] = record["attachments"]
            models.append(
                cls.payload_to_model(
                    attributes=record["attributes"],
                    shortname=record["shortname"],
                )
            )

        return models

    async def attach(
        self,
        payload: BinaryIO,
        payload_file_name: str,
        payload_mime_type: str,
        entry_shortname: str | None = None,
    ) -> bool:
        model_name = snake_case(self.__class__.__name__)
        record = {
            "resource_type": ResourceType.media,
            "shortname": entry_shortname or "auto",
            "subpath": f"{model_data_mapper[model_name]['subpath']}/{self.shortname}",
            "attributes": {"is_active": True},
        }
        try:
            await dmart.upload_resource_with_payload(
                space_name=Space.acme,
                record=record,
                payload=payload,
                payload_file_name=payload_file_name,
                payload_mime_type=payload_mime_type,
            )
            return True
        except Exception:
            return False
