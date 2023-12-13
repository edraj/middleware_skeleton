from api.schemas.response import ApiException, Error
from models.base.enums import CancellationReason, ResourceType, Space
from models.base.json_model import JsonModel, TJsonModel, model_data_mapper
from utils.dmart import dmart
from utils.helpers import snake_case


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

    async def store(self) -> None:
        await JsonModel.store(self, ResourceType.ticket)

    async def sync(self) -> None:
        await JsonModel.sync(self, ResourceType.ticket)

    @classmethod
    async def get(cls: type[TJsonModel], shortname: str) -> TJsonModel | None:
        model_name = snake_case(cls.__name__)
        try:
            data: dict = await dmart.read(
                space_name=Space.acme,
                subpath=model_data_mapper[model_name]["subpath"],
                shortname=shortname,
                resource_type=ResourceType.ticket,
                retrieve_attachments=True,
            )
            return cls.payload_to_model(
                attributes=data,
                shortname=data.get("shortname"),
            )
        except Exception as _:
            return None

    @classmethod
    async def get_or_fail(cls: type[TJsonModel], shortname: str) -> TJsonModel | None:
        model = await cls.get(shortname)
        if not model:
            raise ApiException(
                status_code=404,
                error=Error(type="db", code=12, message="Model not found"),
            )
        return model

    async def delete(self) -> None:
        await JsonModel.delete(self, ResourceType.ticket)
