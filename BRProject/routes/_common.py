"""Shared helpers for FastAPI route modules."""

from __future__ import annotations

from typing import Any, List

from fastapi import HTTPException, status

from app.config import settings
from app.schemas import BoundingBox, Detection
from models.yolo_loader import yolo_model


def enforce_size(raw: bytes) -> None:
    """Raise 413 if the uploaded payload exceeds the configured size limit."""
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(raw) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.max_upload_size_mb} MB limit.",
        )


def to_detections(result: Any) -> List[Detection]:
    """Convert an Ultralytics result into a list of typed ``Detection`` schemas."""
    detections: List[Detection] = []
    boxes = getattr(result, "boxes", None)
    if boxes is None or boxes.xyxy is None:
        return detections

    names = yolo_model.class_names
    xyxy = boxes.xyxy.cpu().numpy()
    confs = boxes.conf.cpu().numpy()
    cls_ids = boxes.cls.cpu().numpy().astype(int)

    for (x1, y1, x2, y2), conf, cls_id in zip(xyxy, confs, cls_ids):
        detections.append(
            Detection(
                class_id=int(cls_id),
                class_name=names.get(int(cls_id), str(cls_id)),
                confidence=float(conf),
                bbox=BoundingBox(
                    x_min=float(x1),
                    y_min=float(y1),
                    x_max=float(x2),
                    y_max=float(y2),
                ),
            )
        )
    return detections
