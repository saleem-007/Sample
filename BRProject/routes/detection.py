"""Blood cell detection endpoints."""

from __future__ import annotations

import time
import uuid
from collections import Counter

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.config import settings
from app.schemas import DetectionResponse
from models.yolo_loader import yolo_model
from routes._common import enforce_size, to_detections
from utils.image_processing import annotate_image, image_dimensions, read_image_bytes
from utils.logger import get_logger

router = APIRouter(prefix="/detect", tags=["detection"])
logger = get_logger(__name__)


@router.post("", response_model=DetectionResponse)
async def detect(file: UploadFile = File(...)) -> DetectionResponse:
    raw = await file.read()
    enforce_size(raw)

    try:
        image = read_image_bytes(raw)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    width, height = image_dimensions(image)

    start = time.perf_counter()
    results = yolo_model.predict(image)
    inference_ms = (time.perf_counter() - start) * 1000

    detections = to_detections(results[0]) if results else []
    counts = Counter(d.class_name for d in detections)

    logger.info(
        "Processed %s in %.1f ms with %d detections",
        file.filename,
        inference_ms,
        len(detections),
    )

    return DetectionResponse(
        filename=file.filename or "uploaded.png",
        image_width=width,
        image_height=height,
        inference_time_ms=round(inference_ms, 2),
        detections=detections,
        counts=dict(counts),
    )


@router.post("/annotated")
async def detect_annotated(file: UploadFile = File(...)) -> FileResponse:
    raw = await file.read()
    enforce_size(raw)

    try:
        image = read_image_bytes(raw)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    results = yolo_model.predict(image)
    detections = to_detections(results[0]) if results else []
    annotated = annotate_image(image, detections)

    output_path = settings.output_dir / f"{uuid.uuid4().hex}.png"
    annotated.save(output_path, format="PNG")

    return FileResponse(output_path, media_type="image/png", filename=output_path.name)
