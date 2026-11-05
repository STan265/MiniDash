
from src.services.orders import (
    release_scheduled_orders,
    change_order_status
)
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from src import database
from src.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Use a separate temporary database for each test.
    test_database = tmp_path / "test_minidash.db"
    monkeypatch.setattr(database, "DATABASE_PATH", test_database)

    with TestClient(app) as test_client:
        yield test_client


def test_create_order(client):
    response = client.post(
        "/orders",
        json={
            "restaurant_id": 1,
            "address": "123 Main Street, New York, NY",
            "items": [
                {"menu_item_id": 1, "quantity": 2},
                {"menu_item_id": 3, "quantity": 1}
            ]
        }
    )

    assert response.status_code == 201

    order = response.json()

    assert order["restaurant_id"] == 1
    assert order["status"] == "PLACED"
    assert order["total_cents"] == 3197
    assert order["address"] == "123 Main Street, New York, NY"


def test_create_order_for_invalid_restaurant(client):
    response = client.post(
        "/orders",
        json={
            "restaurant_id": 999,
            "address": "123 Main Street, New York, NY",
            "items": [
                {"menu_item_id": 1, "quantity": 1}
            ]
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Restaurant not found"


def test_create_order_with_item_from_another_restaurant(client):
    response = client.post(
        "/orders",
        json={
            "restaurant_id": 1,
            "address": "123 Main Street, New York, NY",
            "items": [
                {"menu_item_id": 4, "quantity": 1}
            ]
        }
    )

    assert response.status_code == 400
    assert "does not belong to this restaurant" in response.json()["detail"]

def test_update_order_status(client):
    # First, create an order.
    create_response = client.post(
        "/orders",
        json={
            "restaurant_id": 1,
            "address": "123 Main Street, New York, NY",
            "items": [
                {"menu_item_id": 1, "quantity": 1}
            ]
        }
    )

    order_id = create_response.json()["order_id"]

    # Then, update its status.
    response = client.patch(
        f"/orders/{order_id}/status",
        json={"status": "PREPARING"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "PREPARING"

def test_update_order_with_invalid_status(client):
    # First, create an order.
    create_response = client.post(
        "/orders",
        json={
            "restaurant_id": 1,
            "address": "123 Main Street, New York, NY",
            "items": [
                {"menu_item_id": 1, "quantity": 1}
            ]
        }
    )

    order_id = create_response.json()["order_id"]

    # Try to update the order with an invalid status.
    response = client.patch(
        f"/orders/{order_id}/status",
        json={"status": "FLYING"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid order status"

def test_update_nonexistent_order_status(client):
    response = client.patch(
        "/orders/999/status",
        json={"status": "PREPARING"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Order not found"

def test_scheduled_order_without_timezone_is_rejected(client):
    scheduled_time = (
        datetime.now() + timedelta(days=3)
    ).isoformat()

    response = client.post(
        "/orders",
        json={
            "restaurant_id": 1,
            "address": "123 Main Street, New York, NY",
            "items": [{"menu_item_id": 1, "quantity": 1}],
            "scheduled_for": scheduled_time
        }
    )

    assert response.status_code == 400
    assert "must include a timezone" in response.json()["detail"]


def test_scheduled_order_less_than_45_minutes_is_rejected(client):
    scheduled_time = (
        datetime.now(timezone.utc) + timedelta(minutes=20)
    ).isoformat()

    response = client.post(
        "/orders",
        json={
            "restaurant_id": 1,
            "address": "123 Main Street, New York, NY",
            "items": [{"menu_item_id": 1, "quantity": 1}],
            "scheduled_for": scheduled_time
        }
    )

    assert response.status_code == 400
    assert "45 minutes" in response.json()["detail"]


def test_scheduled_order_more_than_7_days_is_rejected(client):
    scheduled_time = (
        datetime.now(timezone.utc) + timedelta(days=8)
    ).isoformat()

    response = client.post(
        "/orders",
        json={
            "restaurant_id": 1,
            "address": "123 Main Street, New York, NY",
            "items": [{"menu_item_id": 1, "quantity": 1}],
            "scheduled_for": scheduled_time
        }
    )

    assert response.status_code == 400
    assert "7 days" in response.json()["detail"]


def test_scheduled_order_when_restaurant_is_closed_is_rejected(client):
    scheduled_time = (
        datetime.now(ZoneInfo("America/New_York")) + timedelta(days=3)
    ).replace(hour=8, minute=0, second=0, microsecond=0).isoformat()

    response = client.post(
        "/orders",
        json={
            "restaurant_id": 1,
            "address": "123 Main Street, New York, NY",
            "items": [{"menu_item_id": 1, "quantity": 1}],
            "scheduled_for": scheduled_time
        }
    )

    assert response.status_code == 400
    assert "Restaurant is closed" in response.json()["detail"]


def test_create_valid_scheduled_order(client):
    scheduled_time = (
        datetime.now(ZoneInfo("America/New_York")) + timedelta(days=3)
    ).replace(hour=12, minute=0, second=0, microsecond=0).isoformat()

    response = client.post(
        "/orders",
        json={
            "restaurant_id": 1,
            "address": "123 Main Street, New York, NY",
            "items": [{"menu_item_id": 1, "quantity": 1}],
            "scheduled_for": scheduled_time
        }
    )

    assert response.status_code == 201
    assert response.json()["status"] == "SCHEDULED"

    order_id = response.json()["order_id"]

    order_response = client.get(f"/orders/{order_id}")

    assert order_response.status_code == 200
    assert order_response.json()["scheduled_for"] is not None

def test_release_scheduled_order_at_30_minute_boundary(client):
    scheduled_time = (
        datetime.now(timezone.utc) + timedelta(hours=1)
    )

    response = client.post(
        "/orders",
        json={
            "restaurant_id": 1,
            "address": "123 Main Street, New York, NY",
            "items": [{"menu_item_id": 1, "quantity": 1}],
            "scheduled_for": scheduled_time.isoformat()
        }
    )

    assert response.status_code == 201

    fixed_clock = scheduled_time - timedelta(minutes=30)

    released_count = release_scheduled_orders(
        clock=lambda: fixed_clock
    )

    assert released_count == 1

    order_id = response.json()["order_id"]
    order = client.get(f"/orders/{order_id}").json()

    assert order["status"] == "PLACED"

    # Calling the release function again must not release it twice.
    second_release_count = release_scheduled_orders(
        clock=lambda: fixed_clock
    )

    assert second_release_count == 0


def test_scheduled_order_is_not_released_too_early(client):
    scheduled_time = (
        datetime.now(timezone.utc) + timedelta(hours=1)
    )

    response = client.post(
        "/orders",
        json={
            "restaurant_id": 1,
            "address": "123 Main Street, New York, NY",
            "items": [{"menu_item_id": 1, "quantity": 1}],
            "scheduled_for": scheduled_time.isoformat()
        }
    )

    assert response.status_code == 201

    fixed_clock = scheduled_time - timedelta(minutes=31)

    released_count = release_scheduled_orders(
        clock=lambda: fixed_clock
    )

    assert released_count == 0

    order_id = response.json()["order_id"]
    order = client.get(f"/orders/{order_id}").json()

    assert order["status"] == "SCHEDULED"

def test_cancel_scheduled_order_before_release(client):
    fixed_now = datetime.now(ZoneInfo("America/New_York"))
    scheduled_time = (
        fixed_now + timedelta(days=1)
    ).replace(hour=12, minute=0, second=0, microsecond=0)

    response = client.post(
        "/orders",
        json={
            "restaurant_id": 1,
            "address": "123 Main Street, New York, NY",
            "items": [{"menu_item_id": 1, "quantity": 1}],
            "scheduled_for": scheduled_time.isoformat()
        }
    )

    assert response.status_code == 201

    order_id = response.json()["order_id"]

    cancelled_order = change_order_status(
        order_id,
        "CANCELLED",
        clock=lambda: fixed_now
    )

    assert cancelled_order["status"] == "CANCELLED"


def test_cannot_cancel_scheduled_order_at_release_boundary(client):
    scheduled_time = (
    datetime.now(ZoneInfo("America/New_York")) + timedelta(days=1)
    ).replace(hour=12, minute=0, second=0, microsecond=0)
    fixed_now = scheduled_time - timedelta(minutes=30)

    response = client.post(
        "/orders",
        json={
            "restaurant_id": 1,
            "address": "123 Main Street, New York, NY",
            "items": [{"menu_item_id": 1, "quantity": 1}],
            "scheduled_for": scheduled_time.isoformat()
        }
    )

    assert response.status_code == 201

    order_id = response.json()["order_id"]

    with pytest.raises(ValueError, match="Only scheduled orders"):
        change_order_status(
            order_id,
            "CANCELLED",
            clock=lambda: fixed_now
        )

    order = client.get(f"/orders/{order_id}").json()
    assert order["status"] == "SCHEDULED"