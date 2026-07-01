from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router

BASE_DIR = Path(__file__).resolve().parent

STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Candidate Intelligence Engine",
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)

app.include_router(router)