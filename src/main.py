
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database import initialize_database
from src.routes.restaurants import router as restaurant_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database when the application starts."""
    initialize_database()
    yield


app = FastAPI(
    title="MiniDash API",
    description="Restaurant ordering and scheduled delivery API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(restaurant_router)

@app.get("/")
def home():
    return {"message": "Welcome to MiniDash API"}
