from typing import TypeVar
from pydantic import BaseModel, Field

from models.enums import Schema, Space
from utils.dmart import dmart
from utils.helpers import snake_case
from utils import regex


model_data_mapper: dict = {
    "user": {"subpath": "users", "schema": Schema.user},
    "user_otp": {"subpath": "users_otps", "schema": Schema.user_otp},
}


TJsonModel = TypeVar("TJsonModel", bound="JsonModel")


class JsonModel(BaseModel):
    shortname: str = Field(default=None, pattern=regex.NAME)

    def __init__(self, **data):
        BaseModel.__init__(self, **data)

    async def store(self) -> None:
        model_name = snake_case(self.__class__.__name__)
        result = await dmart.create(
            space_name=Space.acme,
            subpath=model_data_mapper[model_name]["subpath"],
            shortname=self.shortname if self.shortname else "auto",
            attributes={
                "is_active": True,
                "payload": {
                    "content_type": "json",
                    "schema_shortname": model_data_mapper[model_name]["schema"],
                    "body": self.model_dump(exclude=["shortname"]),
                },
            },
        )
        self.shortname = result["records"][0]["shortname"]

    async def sync(self) -> None:
        model_name = snake_case(self.__class__.__name__)
        await dmart.update(
            space_name=Space.acme,
            subpath=model_data_mapper[model_name]["subpath"],
            shortname=self.shortname,
            attributes={
                "is_active": True,
                "payload": {
                    "content_type": "json",
                    "schema_shortname": model_data_mapper[model_name]["schema"],
                    "body": self.model_dump(exclude=["shortname"]),
                },
            },
        )

    async def delete(self) -> None:
        model_name = snake_case(self.__class__.__name__)
        await dmart.delete(
            space_name=Space.acme,
            subpath=model_data_mapper[model_name]["subpath"],
            shortname=self.shortname,
        )

    @classmethod
    async def get(cls: type[TJsonModel], shortname: str) -> TJsonModel | None:
        model_name = snake_case(cls.__name__)
        try:
            await dmart.read(
                space_name=Space.acme,
                subpath=model_data_mapper[model_name]["subpath"],
                shortname=shortname,
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

        class_model = cls(**result["records"][0]["attributes"]["payload"]["body"])
        class_model.shortname = result["records"][0]["shortname"]
        return class_model
