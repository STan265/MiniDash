
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI

from src.database import initialize_database
from src.routes.restaurants import router as restaurant_router
from src.routes.orders import router as order_router
from src.services.orders import release_scheduled_orders


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def scheduled_order_worker():
    """Check periodically for scheduled orders ready for release."""

    while True:
        try:
            released_count = release_scheduled_orders(
                clock=lambda: datetime.now(timezone.utc)
            )

            if released_count > 0:
                logger.info(
                    "Released %s scheduled order(s)",
                    released_count
                )

        except Exception:
            logger.exception("Scheduled order release failed")

        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database and start the scheduled-order worker."""

    initialize_database()

    worker_task = asyncio.create_task(scheduled_order_worker())

    try:
        yield
    finally:
        worker_task.cancel()

        try:
            await worker_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="MiniDash API",
    description="Restaurant ordering and scheduled delivery API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(restaurant_router)
app.include_router(order_router)


@app.get("/")
def home():
    return {"message": "Welcome to MiniDash API"}