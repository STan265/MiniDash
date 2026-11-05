
from datetime import timedelta, timezone

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
    now = clock()

    # 6. Validate the requested scheduled delivery time.
    scheduled_for = order_request.scheduled_for

    if scheduled_for is not None:

        # A timezone is required for scheduled deliveries.
        if (
            scheduled_for.tzinfo is None
            or scheduled_for.utcoffset() is None
        ):
            raise ValueError(
                "Scheduled delivery must include a timezone"
            )

        # Convert both times to UTC for accurate comparison.
        scheduled_utc = scheduled_for.astimezone(timezone.utc)
        now_utc = now.astimezone(timezone.utc)

        # Delivery must be at least 45 minutes away.
        if scheduled_utc < now_utc + timedelta(minutes=45):
            raise ValueError(
                "Scheduled delivery must be at least 45 minutes ahead"
            )

        # Delivery cannot be more than 7 days away.
        if scheduled_utc > now_utc + timedelta(days=7):
            raise ValueError(
                "Scheduled delivery cannot be more than 7 days ahead"
            )
                    # Check whether the restaurant is open at the requested time.
        delivery_time = scheduled_for.strftime("%H:%M")

        opens_at = restaurant["opens_at"]
        closes_at = restaurant["closes_at"]

        if not (opens_at <= delivery_time < closes_at):
            raise ValueError(
                "Restaurant is closed at the scheduled delivery time"
            )

    created_at = now.isoformat()


    # 7. Determine the order status.
    if scheduled_for is not None:
        order_status = "SCHEDULED"
        scheduled_value = scheduled_utc.isoformat()
    else:
        order_status = "PLACED"
        scheduled_value = None

    # 8. Save the order.
    order_id = order_repository.create_order(
        restaurant_id=order_request.restaurant_id,
        total_cents=total_cents,
        address=order_request.address,
        created_at=created_at,
        items=order_items,
        status=order_status,
        scheduled_for=scheduled_value
    )

    return {
        "order_id": order_id,
        "restaurant_id": order_request.restaurant_id,
        "status": order_status,
        "scheduled_for": scheduled_value,
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


def change_order_status(order_id, status, clock):
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

    # Handle scheduled-order cancellation separately.
    if status == "CANCELLED":
        now = clock()

        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError(
                "Clock must return a timezone-aware datetime"
            )

        cancellation_cutoff = (
            now.astimezone(timezone.utc) + timedelta(minutes=30)
        ).isoformat()

        cancelled = order_repository.cancel_scheduled_order(
            order_id,
            cancellation_cutoff
        )

        if not cancelled:
            order = order_repository.get_order(order_id)

            if order is None:
                raise ValueError("Order not found")

            raise ValueError(
                "Only scheduled orders can be cancelled before their release time"
            )

        return order_repository.get_order(order_id)

    updated = order_repository.update_order_status(
        order_id,
        status
    )

    if not updated:
        raise ValueError("Order not found")

    return order_repository.get_order(order_id)

def release_scheduled_orders(clock):
    """Release scheduled orders 30 minutes before delivery."""
    now = clock()

    # The clock must provide a timezone-aware datetime.
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Clock must return a timezone-aware datetime")

    # Calculate the release cutoff.
    release_cutoff = (
        now.astimezone(timezone.utc) + timedelta(minutes=30)
    ).isoformat()

    # Release all orders due by this cutoff.
    return order_repository.release_due_orders(release_cutoff)
