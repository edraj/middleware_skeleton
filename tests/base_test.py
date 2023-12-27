import json
from typing import Any
from fastapi.testclient import TestClient
from httpx import Response
from main import app
from fastapi import status
from models.base.enums import OTPOperationType
from models.otp import Otp
from utils.helpers import special_to_underscore


client = TestClient(app)


async def get_otp(identifier: str, operation_type: OTPOperationType) -> Any:
    return await Otp.find(
        shortname=special_to_underscore(identifier),
        operation_type=operation_type,
    )


def assert_code_and_status_success(response: Response) -> None:
    json_response = response.json()
    # if (
    #     response.status_code != status.HTTP_200_OK
    #     or json_response.get("status") != "success"
    # ):
    print(
        "\n\n\n\n\n========================= ERROR RESPONSE: =========================n:",
        json.dumps(response.json(), indent=4),
        "\n\n\n\n\n",
    )
    assert response.status_code == status.HTTP_200_OK
    assert json_response.get("status") == "success"
