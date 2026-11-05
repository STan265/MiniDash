
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


def test_get_restaurants(client):
    response = client.get("/restaurants")

    assert response.status_code == 200

    restaurants = response.json()

    assert len(restaurants) == 5
    assert restaurants[0]["name"] == "Golden Dragon"


def test_get_restaurant_menu(client):
    response = client.get("/restaurants/1/menu")

    assert response.status_code == 200

    menu = response.json()

    assert len(menu) == 3
    assert menu[0]["name"] == "Chicken Fried Rice"
    assert menu[0]["price_cents"] == 1299


def test_get_menu_for_invalid_restaurant(client):
    response = client.get("/restaurants/999/menu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found"

