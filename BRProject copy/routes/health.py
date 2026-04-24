"""Liveness / readiness endpoints."""

from fastapi import APIRouter

from app.config import settings
from app.schemas import HealthResponse
from models.yolo_loader import yolo_model

router = APIRouter(tags=["health"])


@router.get("/", response_model=HealthResponse)
def root() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=yolo_model.is_loaded,
        version=settings.app_version,
    )


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=yolo_model.is_loaded,
        version=settings.app_version,
    )
