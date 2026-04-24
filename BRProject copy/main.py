"""FastAPI entry point for the Blood Cell Detection service."""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from models.yolo_loader import yolo_model
from routes import analyze, detection, health
from utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Warm up the YOLO model so the first request is fast.
    logger.info("Loading YOLO weights from %s", settings.model_weights_path)
    yolo_model.load()
    logger.info("Model loaded. Service is ready.")
    yield
    logger.info("Shutting down Blood Cell Detection service.")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="REST API for detecting RBCs, WBCs and platelets in microscope images.",
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(detection.router, prefix="/api/v1")
    app.include_router(analyze.router, prefix="/api/v1")

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
