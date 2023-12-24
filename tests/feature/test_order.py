import pytest
from models.base.enums import CancellationReason
from tests.base_test import assert_code_and_status_success, client

_order_shortname: str = ""
ORDER_PAYLOAD: dict[str, str | dict[str, str]] = {
    "name": "John",
    "address": "Baghdad",
    "mobile": "2355806229",
    "location": {"latitude": "33.3152° N", "longitude": "44.3661° E"},
    "language": "en",
}


@pytest.mark.run(order=2)
def test_create_order():
    global _order_shortname
    response = client.post(
        "/order/create",
        json=ORDER_PAYLOAD,
    )
    assert_code_and_status_success(response)
    json_response = response.json()
    _order_shortname = json_response.get("data", {}).get("shortname", "")


@pytest.mark.run(order=2)
def test_track_order():
    response = client.get(f"order/{_order_shortname}/track")
    assert_code_and_status_success(response)
    assert response.json().get("data", {}).get("order", {}).get("state") == "pending"


@pytest.mark.run(order=2)
def test_update_order():
    response = client.put(
        f"order/{_order_shortname}/update",
        json={
            "tracking_id": "2390849311212",
            "planned_delivery_date": "2023-12-13T21:06:25.242772",
            "scheduled_delivery": "2023-12-13T21:06:25.242791",
            "state": "assigned",
        },
    )
    assert_code_and_status_success(response)
    assert response.json().get("data", {}).get("state") == "assigned"


@pytest.mark.run(order=2)
def test_attach_to_order():
    with open("tests/data/order_attachment.jpeg", "rb") as attachment_file:
        response = client.post(
            f"/order/{_order_shortname}/attach",
            data={"document_name": "order_sample_attachment"},
            files={
                "file": (
                    attachment_file.name.split("/")[-1],
                    attachment_file,
                    "image/jpeg",
                ),
            },
        )

    assert_code_and_status_success(response)


@pytest.mark.run(order=2)
def test_query_assigned_orders():
    response = client.post("/order/query?order_status=assigned")
    assert_code_and_status_success(response)
    assert response.json().get("data", {}).get("count") > 1


# @pytest.mark.run(order=2)
# def test_assign_order():
#     response: Response = client.post(
#         "/order/create",
#         json=ORDER_PAYLOAD,
#     )
#     assert_code_and_status_success(response)
#     order_shortname: str = response.json().get("data", {}).get("shortname", "")
#     response = client.put(f"order/{order_shortname}/assign")
#     assert_code_and_status_success(response)
#     assert response.json().get("data", {}).get("order", {}).get("state") == "assigned"


@pytest.mark.run(order=2)
def test_cancel_order():
    response = client.post(
        "/order/create",
        json=ORDER_PAYLOAD,
    )
    assert_code_and_status_success(response)
    order_shortname = response.json().get("data", {}).get("shortname")

    response = client.put(
        f"order/{order_shortname}/cancel?cancellation_reason={CancellationReason.ordered_by_mistake}"
    )
    assert_code_and_status_success(response)
    assert response.json().get("data", {}).get("order", {}).get("state") == "cancelled"
    assert (
        response.json().get("data", {}).get("order", {}).get("resolution_reason")
        == CancellationReason.ordered_by_mistake
    )
