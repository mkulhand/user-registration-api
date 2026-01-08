from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI(
    title="User Registration API",
    openapi_url="/openapi.json",
)


@app.get("/")
def hosted_page():
    return FileResponse("index.html", media_type="text/html")


api_router = APIRouter(prefix="/api")

from src.routers import user_router

api_router.include_router(user_router)


@api_router.get("/health")
def health_check():
    return JSONResponse({"status": "running"})


app.include_router(api_router)
