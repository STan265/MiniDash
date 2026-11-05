
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
    