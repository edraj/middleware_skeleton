from random import randint
import time
from fastapi.testclient import TestClient
import pytest
from main import app
from utils.redis_services import RedisServices

from fastapi import status

client = TestClient(app)

EMAIL = f"name{time.time()}@gmail.com"
UPDATED_EMAIL = f"name{time.time()}@gmail.com"
MOBILE = f"799922{randint(1111,9999)}"
UPDATED_MOBILE = f"799922{randint(1111,9999)}"
SHORTNAME = None
PASSWORD = "test1234"
UPDATED_PASSWORD = "test123456"
TOKEN = None

RedisServices.is_pytest = True


@pytest.mark.asyncio
async def test_register(mocker):
    global SHORTNAME
    mocker.patch("mail.user_verification.UserVerification.send")
    mocker.patch("services.sms_sender.SMSSender.send")
    response = client.post(
        "/auth/register",
        json={
            "email": EMAIL,
            "first_name": "John",
            "language": "en",
            "last_name": "Doo",
            "mobile": MOBILE,
            "password": PASSWORD,
            "password_confirmation": PASSWORD,
            "profile_pic_url": "https://pics.com/myname.png",
        },
    )

    assert_code_and_status_success(response)
    json_response = response.json()
    SHORTNAME = json_response.get("data", {}).get("shortname")
    otps_stored = await get_otps()
    assert len(otps_stored) == 2


@pytest.mark.asyncio
async def test_resend_email_verification(mocker):
    mocker.patch("mail.user_verification.UserVerification.send")
    response = client.get(f"/auth/resend-verification-email?email={EMAIL}")
    assert_code_and_status_success(response)
    otps_stored = await get_otps()
    assert len(otps_stored) == 3


@pytest.mark.asyncio
async def test_resend_sms_verification(mocker):
    mocker.patch("services.sms_sender.SMSSender.send")
    response = client.get(f"/auth/resend-verification-sms?mobile={MOBILE}")
    assert_code_and_status_success(response)
    otps_stored = await get_otps()
    assert len(otps_stored) == 4


@pytest.mark.asyncio
async def test_verify_email():
    otps_stored = await get_otps()
    email_otps = list(
        filter(lambda otp: otp.endswith("mail_verification"), otps_stored)
    )
    assert len(email_otps)
    response = client.post(
        "/auth/verify-email", json={"email": EMAIL, "otp": email_otps[0].split(":")[1]}
    )
    assert_code_and_status_success(response)
    otps_stored = await get_otps()
    assert len(otps_stored) == 3


def test_login_with_email():
    response = client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert_code_and_status_success(response)


@pytest.mark.asyncio
async def test_verify_mobile():
    otps_stored = await get_otps()
    mobile_otps = list(
        filter(lambda otp: otp.endswith("mobile_verification"), otps_stored)
    )
    assert len(mobile_otps)
    response = client.post(
        "/auth/verify-mobile",
        json={"mobile": MOBILE, "otp": mobile_otps[0].split(":")[1]},
    )
    assert_code_and_status_success(response)
    otps_stored = await get_otps()
    assert len(otps_stored) == 2


def test_login_with_mobile():
    response = client.post("/auth/login", json={"mobile": MOBILE, "password": PASSWORD})
    assert_code_and_status_success(response)


@pytest.mark.asyncio
async def test_forgot_password(mocker):
    mocker.patch("mail.user_reset_password.UserResetPassword.send")
    response = client.get(f"/auth/forgot-password?email={EMAIL}")
    assert_code_and_status_success(response)
    otps_stored = await get_otps()
    assert any(otp.endswith("reset_password") for otp in otps_stored)


@pytest.mark.asyncio
async def test_reset_password():
    otps_stored = await get_otps()
    reset_otps = list(filter(lambda otp: otp.endswith("reset_password"), otps_stored))
    assert len(reset_otps)
    response = client.post(
        "/auth/reset-password",
        json={
            "email": EMAIL,
            "otp": reset_otps[0].split(":")[1],
            "password": UPDATED_PASSWORD,
            "password_confirmation": UPDATED_PASSWORD,
        },
    )
    assert_code_and_status_success(response)


def test_login_with_new_password():
    global TOKEN
    response = client.post(
        "/auth/login", json={"mobile": MOBILE, "password": UPDATED_PASSWORD}
    )
    assert_code_and_status_success(response)
    TOKEN = response.json().get("data", {}).get("token")


def test_get_profile():
    response = client.get("/user", headers={"Authorization": f"Bearer {TOKEN}"})
    assert_code_and_status_success(response)


@pytest.mark.asyncio
async def test_update_profile(mocker):
    mocker.patch("mail.user_verification.UserVerification.send")
    mocker.patch("services.sms_sender.SMSSender.send")
    response = client.put(
        "/user",
        json={
            "email": UPDATED_EMAIL,
            "first_name": "John2",
            "language": "ar",
            "last_name": "Doo2",
            "mobile": UPDATED_MOBILE,
            "profile_pic_url": "https://pics.com/myname.png",
        },
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert_code_and_status_success(response)
    otps_stored = await get_otps()
    assert len(otps_stored) == 4


def test_login_with_old_email():
    response = client.post(
        "/auth/login", json={"email": EMAIL, "password": UPDATED_PASSWORD}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_with_new_unverified_email():
    response = client.post(
        "/auth/login", json={"email": UPDATED_EMAIL, "password": UPDATED_PASSWORD}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_with_old_mobile():
    response = client.post(
        "/auth/login", json={"mobile": MOBILE, "password": UPDATED_PASSWORD}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_with_new_unverified_mobile():
    response = client.post(
        "/auth/login", json={"mobile": UPDATED_MOBILE, "password": UPDATED_PASSWORD}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_verify_new_mobile():
    otps_stored = await get_otps()
    mobile_otps = list(
        filter(lambda otp: otp.endswith("mobile_verification"), otps_stored)
    )
    assert len(mobile_otps)
    response = client.post(
        "/auth/verify-mobile",
        json={"mobile": UPDATED_MOBILE, "otp": mobile_otps[0].split(":")[1]},
    )
    assert_code_and_status_success(response)
    otps_stored = await get_otps()
    assert len(otps_stored) == 3


def test_login_with_new_mobile():
    global TOKEN
    response = client.post(
        "/auth/login", json={"mobile": UPDATED_MOBILE, "password": UPDATED_PASSWORD}
    )
    assert_code_and_status_success(response)
    TOKEN = response.json().get("data", {}).get("token")


def test_get_updated_profile():
    response = client.get("/user", headers={"Authorization": f"Bearer {TOKEN}"})
    assert_code_and_status_success(response)
    json_response = response.json()

    assert json_response.get("data", {}).get("user") == {
        "shortname": SHORTNAME,
        "first_name": "John2",
        "last_name": "Doo2",
        "email": UPDATED_EMAIL,
        "mobile": UPDATED_MOBILE,
        "profile_pic_url": "https://pics.com/myname.png",
        "language": "ar",
        "is_email_verified": False,
        "is_mobile_verified": True,
    }


def test_logout():
    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {TOKEN}"})
    assert_code_and_status_success(response)


def test_get_profile_after_logout():
    response = client.get("/user", headers={"Authorization": f"Bearer {TOKEN}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_account():
    global TOKEN
    response = client.post(
        "/auth/login", json={"mobile": UPDATED_MOBILE, "password": UPDATED_PASSWORD}
    )
    assert_code_and_status_success(response)
    TOKEN = response.json().get("data", {}).get("token")
    response = client.delete("/user", headers={"Authorization": f"Bearer {TOKEN}"})
    assert_code_and_status_success(response)


async def get_otps():
    async with RedisServices() as redis:
        return await redis.get_keys(f"{SHORTNAME}:*")


def assert_code_and_status_success(response):
    json_response = response.json()
    if (
        response.status_code != status.HTTP_200_OK
        or json_response.get("status") != "success"
    ):
        print(
            "\n\n\n\n\n========================= ERROR RESPONSE: =========================n:",
            response.json(),
            "\n\n\n\n\n",
        )
    assert response.status_code == status.HTTP_200_OK
    assert json_response.get("status") == "success"
