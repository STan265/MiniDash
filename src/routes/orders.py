
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from src.models import OrderCreateRequest, OrderStatusRequest
from src.services.orders import (
    place_order,
    retrieve_order,
    change_order_status
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", status_code=201)
def create_order(order_request: OrderCreateRequest):
    """Create a new customer order."""

    try:
        return place_order(
            order_request=order_request,
            clock=lambda: datetime.now(timezone.utc)
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error
@router.get("/{order_id}")
def get_order(order_id: int):
    """Retrieve an existing customer order."""

    try:
        return retrieve_order(order_id)

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        ) from error


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    status_request: OrderStatusRequest
):
    """Update the status of an existing order."""

    try:
        return change_order_status(
            order_id,
            status_request.status
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

