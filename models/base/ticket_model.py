from typing import Any
from api.schemas.response import ApiException, Error
from models.base.enums import CancellationReason, ResourceType, Space
from models.base.json_model import JsonModel, TJsonModel, model_data_mapper
from utils.dmart import dmart
from utils.helpers import snake_case
from fastapi.logger import logger


class TicketModel(JsonModel):
    async def progress(
        self, action: str, cancellation_reasons: CancellationReason | None = None
    ):
        model_name = snake_case(self.__class__.__name__)

        return await dmart.progress_ticket(
            space_name=Space.acme,
            subpath=model_data_mapper[model_name]["subpath"],
            shortname=self.shortname,
            action=action,
            cancellation_reasons=cancellation_reasons,
        )

    async def store(self, resource_type: ResourceType = ResourceType.ticket) -> None:
        await JsonModel.store(self, resource_type)

    async def sync(self, resource_type: ResourceType = ResourceType.ticket) -> None:
        await JsonModel.sync(self, resource_type)

    @classmethod
    async def get(cls: type[TJsonModel], shortname: str) -> TJsonModel | None:
        model_name = snake_case(cls.__name__)
        try:
            data: dict[str, Any] = await dmart.read(
                space_name=Space.acme,
                subpath=model_data_mapper[model_name]["subpath"],
                shortname=shortname,
                resource_type=ResourceType.ticket,
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
                resource_type=ResourceType.ticket,
                retrieve_attachments=True,
            )
            updated = self.__class__.payload_to_model(
                attributes=data,
                shortname=data.get("shortname", ""),
            )
            if updated:
                for key, val in updated.model_dump().items():
                    setattr(self, str(key), val)
        except Exception as e:
            logger.warn(f"Failed to refresh the model: {model_name}", {"error": e.args})

    async def delete(self, resource_type: ResourceType = ResourceType.ticket) -> None:
        await JsonModel.delete(self, resource_type)
