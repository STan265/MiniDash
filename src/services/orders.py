
from src.repositories import orders as order_repository


def place_order(order_request, clock):
    """Validate, calculate, and save a customer order."""

    # 1. Check that the restaurant exists.
    restaurant = order_repository.get_restaurant(
        order_request.restaurant_id
    )

    if restaurant is None:
        raise ValueError("Restaurant not found")

    # 2. Retrieve the selected menu items.
    menu_item_ids = [
        item.menu_item_id for item in order_request.items
    ]

    menu_items = order_repository.get_menu_items(menu_item_ids)

    menu_by_id = {
        item["id"]: item for item in menu_items
    }

    # 3. Make sure every selected item belongs to this restaurant.
    for menu_item_id in menu_item_ids:
        menu_item = menu_by_id.get(menu_item_id)

        if menu_item is None:
            raise ValueError(
                f"Menu item {menu_item_id} not found"
            )

        if menu_item["restaurant_id"] != order_request.restaurant_id:
            raise ValueError(
                f"Menu item {menu_item_id} does not belong "
                "to this restaurant"
            )

    # 4. Calculate the total using database prices.
    total_cents = 0
    order_items = []

    for item in order_request.items:
        menu_item = menu_by_id[item.menu_item_id]

        total_cents += menu_item["price_cents"] * item.quantity

        order_items.append({
            "menu_item_id": item.menu_item_id,
            "quantity": item.quantity
        })

    # 5. Get the current time from the injected clock.
    created_at = clock().isoformat()

    # 6. Save the order.
    order_id = order_repository.create_order(
        restaurant_id=order_request.restaurant_id,
        total_cents=total_cents,
        address=order_request.address,
        created_at=created_at,
        items=order_items
    )

    return {
        "order_id": order_id,
        "restaurant_id": order_request.restaurant_id,
        "status": "PLACED",
        "total_cents": total_cents,
        "address": order_request.address,
        "created_at": created_at
    }
def retrieve_order(order_id):
    """Retrieve an existing customer order."""

    order = order_repository.get_order(order_id)

    if order is None:
        raise ValueError("Order not found")

    return order


def change_order_status(order_id, status):
    """Validate and update an order's status."""

    allowed_statuses = {
        "PLACED",
        "PREPARING",
        "READY",
        "DELIVERED",
        "CANCELLED"
    }

    status = status.upper()

    if status not in allowed_statuses:
        raise ValueError("Invalid order status")

    updated = order_repository.update_order_status(
        order_id,
        status
    )

    if not updated:
        raise ValueError("Order not found")

    return order_repository.get_order(order_id)
