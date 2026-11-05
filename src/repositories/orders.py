
from src.database import get_connection


def get_restaurant(restaurant_id):
    """Find a restaurant by its ID."""
    connection = get_connection()

    try:
        return connection.execute(
            "SELECT * FROM restaurants WHERE id = ?",
            (restaurant_id,)
        ).fetchone()
    finally:
        connection.close()


def get_menu_items(menu_item_ids):
    """Retrieve menu items by their IDs."""
    if not menu_item_ids:
        return []

    placeholders = ",".join("?" for _ in menu_item_ids)

    connection = get_connection()

    try:
        return connection.execute(
            f"SELECT * FROM menu_items WHERE id IN ({placeholders})",
            menu_item_ids
        ).fetchall()
    finally:
        connection.close()


def create_order(restaurant_id, total_cents, address, created_at, items):
    """Save an order and its items in the database."""
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO orders
            (restaurant_id, status, total_cents, address, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (restaurant_id, "PLACED", total_cents, address, created_at)
        )

        order_id = cursor.lastrowid

        for item in items:
            connection.execute(
                """
                INSERT INTO order_items
                (order_id, menu_item_id, quantity)
                VALUES (?, ?, ?)
                """,
                (order_id, item["menu_item_id"], item["quantity"])
            )

        connection.commit()
        return order_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()



def get_order(order_id):
    """Retrieve an order and its menu items."""
    connection = get_connection()

    try:
        order = connection.execute(
            "SELECT * FROM orders WHERE id = ?",
            (order_id,)
        ).fetchone()

        if order is None:
            return None

        items = connection.execute(
            """
            SELECT
                order_items.menu_item_id,
                menu_items.name,
                menu_items.price_cents,
                order_items.quantity
            FROM order_items
            JOIN menu_items
                ON order_items.menu_item_id = menu_items.id
            WHERE order_items.order_id = ?
            """,
            (order_id,)
        ).fetchall()

        result = dict(order)
        result["items"] = [dict(item) for item in items]

        return result

    finally:
        connection.close()


def update_order_status(order_id, status):
    """Update the status of an existing order."""
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE orders
            SET status = ?
            WHERE id = ?
            """,
            (status, order_id)
        )

        if cursor.rowcount == 0:
            return False

        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
