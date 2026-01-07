from fastapi import APIRouter, FastAPI

app = FastAPI(
    title="User Registration API",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

api_router = APIRouter(prefix="/api")

from src.routers import user_router

api_router.include_router(user_router)

app.include_router(api_router)
