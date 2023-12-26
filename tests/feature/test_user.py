from random import randint
import time
import pytest
from tests.base_test import assert_code_and_status_success, get_otps, client
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
            url="/auth/generate-otp", json={"email": EMAIL, "mobile": MOBILE}
        )
    )


@pytest.mark.run(order=1)
@pytest.mark.asyncio
async def test_register() -> None:
    global _shortname

    email_otps: list[str] = get_email_otps(await get_otps(EMAIL), EMAIL)
    assert len(email_otps)

    otps_stored = await get_otps(MOBILE)
    mobile_otps: list[str] = get_mobile_otps(otps_stored, MOBILE)
    assert len(mobile_otps)

    response: Response = client.post(
        "/auth/register",
        json={
            "avatar_url": "https://pics.com/myname.png",
            "contact": {
                "email_otp": email_otps[0].split(":")[2],
                "email": EMAIL,
                "mobile_otp": mobile_otps[0].split(":")[2],
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
    _shortname = json_response.get("data", {}).get("shortname")
    otps_stored = await get_otps(_shortname)
    assert get_email_otps(await get_otps(EMAIL), EMAIL) == []
    assert get_mobile_otps(await get_otps(MOBILE), MOBILE) == []


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
    client.post(url="/auth/generate-otp", json={"mobile": MOBILE})

    mobile_otps: list[str] = get_mobile_otps(await get_otps(MOBILE), MOBILE)
    assert mobile_otps

    response: Response = client.post(
        "/auth/login",
        json={"mobile": MOBILE, "mobile_otp": mobile_otps[0].split(":")[2]},
    )

    assert_code_and_status_success(response)


@pytest.mark.asyncio
@pytest.mark.run(order=1)
async def test_forgot_password(mocker) -> None:  # type: ignore
    mocker.patch("mail.user_reset_password.UserResetPassword.send")  # type: ignore
    response: Response = client.get(f"/auth/forgot-password?email={EMAIL}")
    assert_code_and_status_success(response)
    otps_stored: list[str] = await get_otps(_shortname)
    assert any(otp.endswith("reset_password") for otp in otps_stored)


@pytest.mark.asyncio
@pytest.mark.run(order=1)
async def test_reset_password() -> None:
    otps_stored: list[str] = await get_otps(_shortname)
    reset_otps = list(filter(lambda otp: otp.endswith("reset_password"), otps_stored))
    assert len(reset_otps)
    response = client.post(
        "/auth/reset-password",
        json={
            "email": EMAIL,
            "otp": reset_otps[0].split(":")[2],
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
        json={"mobile": UPDATED_MOBILE, "email": UPDATED_EMAIL},
    )

    mobile_otps: list[str] = get_mobile_otps(
        await get_otps(UPDATED_MOBILE), UPDATED_MOBILE
    )
    assert mobile_otps
    email_otps: list[str] = get_email_otps(await get_otps(UPDATED_EMAIL), UPDATED_EMAIL)
    assert email_otps

    response: Response = client.put(
        "/user",
        json={
            "avatar_url": "https://pics.com/myname.png",
            "contact": {
                "email_otp": email_otps[0].split(":")[2],
                "email": UPDATED_EMAIL,
                "mobile_otp": mobile_otps[0].split(":")[2],
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


def get_email_otps(otps: list[str], email: str) -> list[str]:
    email_otps = list(
        filter(
            lambda otp: otp.endswith("mail_verification"),
            otps,
        )
    )
    return email_otps


def get_mobile_otps(otps: list[str], mobile: str) -> list[str]:
    mobile_otps = list(
        filter(
            lambda otp: otp.endswith("mobile_verification"),
            otps,
        )
    )
    return mobile_otps
