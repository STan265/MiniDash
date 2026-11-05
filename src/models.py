
from datetime import datetime

from pydantic import BaseModel, Field


class OrderItemRequest(BaseModel):
    """One menu item included in an order."""

    menu_item_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderCreateRequest(BaseModel):
    """Information required to create a customer order."""

    restaurant_id: int = Field(gt=0)
    address: str = Field(min_length=5)
    items: list[OrderItemRequest] = Field(min_length=1)
    scheduled_for: datetime | None = None


class OrderStatusRequest(BaseModel):
    """Information required to update an order status."""

    status: str = Field(min_length=1)
