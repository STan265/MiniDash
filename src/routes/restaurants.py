
from fastapi import APIRouter, HTTPException

from src.database import get_connection

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get("")
def get_restaurants():
    """Return all restaurants."""
    connection = get_connection()

    try:
        restaurants = connection.execute(
            "SELECT * FROM restaurants ORDER BY id"
        ).fetchall()

        return [dict(restaurant) for restaurant in restaurants]
    finally:
        connection.close()


@router.get("/{restaurant_id}/menu")
def get_restaurant_menu(restaurant_id: int):
    """Return the menu for a specific restaurant."""
    connection = get_connection()

    try:
        restaurant = connection.execute(
            "SELECT id FROM restaurants WHERE id = ?",
            (restaurant_id,)
        ).fetchone()

        if restaurant is None:
            raise HTTPException(
                status_code=404,
                detail="Restaurant not found"
            )

        menu_items = connection.execute(
            "SELECT * FROM menu_items WHERE restaurant_id = ?",
            (restaurant_id,)
        ).fetchall()

        return [dict(item) for item in menu_items]
    finally:
        connection.close()
