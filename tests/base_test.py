import json
from fastapi.testclient import TestClient
from main import app
from fastapi import status

from utils.redis_services import RedisServices

client = TestClient(app)


async def get_otps(shortname: str):
    async with RedisServices() as redis:
        return await redis.get_keys(f"{shortname}:*")


def assert_code_and_status_success(response):
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
