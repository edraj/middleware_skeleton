import json
from fastapi.testclient import TestClient
from httpx import Response
from main import app
from fastapi import status
from utils.helpers import special_to_underscore

from utils.redis_services import RedisServices

client = TestClient(app)


async def get_otps(identifier: str) -> list[str]:
    async with RedisServices() as redis:
        escaped: str = special_to_underscore(identifier)
        res = await redis.get_keys(f"{escaped}:*")
        print(f"\n\n {escaped = } \n {res = } \n\n")
        return res


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
