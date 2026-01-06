from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="User Registration API",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

api_router = APIRouter(prefix="/api")

from src.routers import user_router

api_router.include_router(user_router)


@api_router.get("/health")
def health_check():
    return JSONResponse({"status": "running"})


app.include_router(api_router)
