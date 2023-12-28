from random import randint
import time
import pytest
from models.base.enums import OTPOperationType
from tests.base_test import assert_code_and_status_success, get_otp, client
from utils.redis_services import RedisServices
from httpx import Response
from fastapi import status


EMAIL = f"name{time.time()}@gmail.com"
UPDATED_EMAIL = f"name{time.time()}@gmail.com"
MOBILE = f"799922{randint(1111,9999)}"
UPDATED_MOBILE = f"799922{randint(1111,9999)}"
_shortname = ""
PASSWORD = "test1234"
UPDATED_PASSWORD = "test123456"
token: str = ""

RedisServices.is_pytest = True


@pytest.mark.run(order=1)
@pytest.mark.asyncio
async def test_request_otp(mocker) -> Response | None:  # type: ignore
    mocker.patch("mail.user_verification.UserVerification.send")  # type: ignore
    mocker.patch("services.sms_sender.SMSSender.send")  # type: ignore

    assert_code_and_status_success(
        response=client.post(
            url="/auth/generate-otp",
            json={
                "email": EMAIL,
                "mobile": MOBILE,
                "operation_type": OTPOperationType.register,
            },
        )
    )


@pytest.mark.run(order=1)
@pytest.mark.asyncio
async def test_register() -> None:
    global _shortname

    email_otp = await get_otp(EMAIL, OTPOperationType.register)
    assert email_otp

    mobile_otp = await get_otp(MOBILE, OTPOperationType.register)
    assert mobile_otp

    response: Response = client.post(
        "/auth/register",
        json={
            "avatar_url": "https://pics.com/myname.png",
            "contact": {
                "email_otp": email_otp,
                "email": EMAIL,
                "mobile_otp": mobile_otp,
                "mobile": MOBILE,
            },
            "date_of_birth": "1990-12-31",
            "first_name": "John",
            "gender": "male",
            "invitations": {"received": "xff4fdkfisjsk", "sent": []},
            "language": "en",
            "last_name": "Doo",
            "oodi_mobile": "7950385032",
            "password": PASSWORD,
            "promo_code": "j42l343kj4",
        },
    )

    assert_code_and_status_success(response)
    json_response = response.json()

    _shortname = json_response.get("data", {}).get("user", {}).get("shortname")

    assert await get_otp(EMAIL, OTPOperationType.register) is None
    assert await get_otp(MOBILE, OTPOperationType.register) is None


@pytest.mark.run(order=1)
def test_login_with_email() -> None:
    response = client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert_code_and_status_success(response)


@pytest.mark.run(order=1)
def test_login_with_mobile() -> None:
    response = client.post("/auth/login", json={"mobile": MOBILE, "password": PASSWORD})
    assert_code_and_status_success(response)


@pytest.mark.run(order=1)
@pytest.mark.asyncio
async def test_login_with_otp(mocker) -> None:  # type: ignore
    mocker.patch("services.sms_sender.SMSSender.send")  # type: ignore
    response = client.post(
        url="/auth/generate-otp",
        json={"mobile": MOBILE, "operation_type": OTPOperationType.login},
    )
    assert_code_and_status_success(response)

    mobile_otp = await get_otp(MOBILE, OTPOperationType.login)
    assert mobile_otp

    response: Response = client.post(
        "/auth/login",
        json={"mobile": MOBILE, "mobile_otp": mobile_otp},
    )

    assert_code_and_status_success(response)


@pytest.mark.asyncio
@pytest.mark.run(order=1)
async def test_reset_password(mocker) -> None:  # type: ignore
    mocker.patch("services.sms_sender.SMSSender.send")  # type: ignore
    client.post(
        url="/auth/generate-otp",
        json={"mobile": MOBILE, "operation_type": OTPOperationType.forgot_password},
    )

    reset_otp = await get_otp(MOBILE, OTPOperationType.forgot_password)
    assert reset_otp

    response = client.post(
        "/auth/reset-password",
        json={
            "mobile": MOBILE,
            "otp": reset_otp,
            "password": UPDATED_PASSWORD,
        },
    )
    assert_code_and_status_success(response)


@pytest.mark.run(order=1)
def test_login_with_new_password():
    # global TOKEN
    response = client.post(
        "/auth/login", json={"mobile": MOBILE, "password": UPDATED_PASSWORD}
    )
    assert_code_and_status_success(response)
    client.cookies.delete("auth_token")
    client.cookies.set("auth_token", response.cookies["auth_token"])
    # TOKEN = response.json().get("data", {}).get("token")


@pytest.mark.run(order=1)
def test_get_profile() -> None:
    response: Response = client.get("/user")
    assert_code_and_status_success(response)


@pytest.mark.asyncio
@pytest.mark.run(order=1)
async def test_update_profile(mocker) -> None:  # type: ignore
    failed_response: Response = client.put(
        "/user",
        json={"contact": {"email": UPDATED_EMAIL, "mobile": UPDATED_MOBILE}},
    )
    assert failed_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    mocker.patch("mail.user_verification.UserVerification.send")  # type: ignore
    mocker.patch("services.sms_sender.SMSSender.send")  # type: ignore
    client.post(
        url="/auth/generate-otp",
        json={
            "mobile": UPDATED_MOBILE,
            "email": UPDATED_EMAIL,
            "operation_type": OTPOperationType.update_profile,
        },
    )

    email_otp = await get_otp(UPDATED_EMAIL, OTPOperationType.update_profile)
    assert email_otp
    mobile_otp = await get_otp(UPDATED_MOBILE, OTPOperationType.update_profile)
    assert mobile_otp

    response: Response = client.put(
        "/user",
        json={
            "avatar_url": "https://pics.com/myname.png",
            "contact": {
                "email_otp": email_otp,
                "email": UPDATED_EMAIL,
                "mobile_otp": mobile_otp,
                "mobile": UPDATED_MOBILE,
            },
            "date_of_birth": "1990-12-31",
            "first_name": "John2",
            "gender": "male",
            "invitations": {
                "received": "xff4fdkfisjsk",
                "sent": ["first_code", "second_code"],
            },
            "language": "ar",
            "last_name": "Doo2",
            "is_oodi_mobile_active": True,
        },
    )
    assert_code_and_status_success(response)


@pytest.mark.run(order=1)
def test_login_with_old_email():
    response = client.post(
        "/auth/login", json={"email": EMAIL, "password": UPDATED_PASSWORD}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.run(order=1)
def test_login_with_old_mobile():
    response = client.post(
        "/auth/login", json={"mobile": MOBILE, "password": UPDATED_PASSWORD}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.run(order=1)
def test_login_with_new_mobile():
    response = client.post(
        "/auth/login", json={"mobile": UPDATED_MOBILE, "password": UPDATED_PASSWORD}
    )
    assert_code_and_status_success(response)
    client.cookies.set("auth_token", response.cookies["auth_token"])


@pytest.mark.run(order=1)
def test_get_updated_profile():
    response = client.get("/user")
    assert_code_and_status_success(response)
    json_response = response.json()

    assert json_response.get("data", {}).get("user") == {
        "shortname": _shortname,
        "first_name": "John2",
        "last_name": "Doo2",
        "contact": {"email": UPDATED_EMAIL, "mobile": UPDATED_MOBILE},
        "avatar_url": "https://pics.com/myname.png",
        "language": "ar",
        "oodi_mobile": "7950385032",
        "is_oodi_mobile_active": True,
        "gender": "male",
        "date_of_birth": "1990-12-31",
    }


@pytest.mark.run(order=10)
def test_logout():
    response = client.post("/auth/logout")
    assert_code_and_status_success(response)


@pytest.mark.run(order=10)
def test_get_profile_after_logout():
    response = client.get("/user")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.run(order=10)
def test_delete_account():
    global token
    response: Response = client.post(
        "/auth/login", json={"email": UPDATED_EMAIL, "password": UPDATED_PASSWORD}
    )
    assert_code_and_status_success(response)
    token = response.json().get("data", {}).get("token")
    response = client.delete("/user", headers={"Authorization": f"Bearer {token}"})
    assert_code_and_status_success(response)
