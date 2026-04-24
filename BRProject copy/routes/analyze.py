"""End-to-end analysis endpoint: detect cells, count them, and build a report."""

from __future__ import annotations

import time
from collections import Counter

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from app.config import settings
from app.schemas import AnalyzeResponse, Report
from models.yolo_loader import yolo_model
from routes._common import enforce_size, to_detections
from utils.image_processing import image_dimensions, read_image_bytes
from utils.interpretation import interpret_counts, build_report
from utils.logger import get_logger

router = APIRouter(tags=["analyze"])
logger = get_logger(__name__)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    file: UploadFile = File(..., description="Microscope image (JPEG/PNG/BMP/TIFF)."),
    enhance_with_ai: bool = Query(
        default=False,
        description="If true, optionally use OpenAI to add a short, safe explanation.",
    ),
) -> AnalyzeResponse:
    """Run YOLO detection, count cells per class, and return a human-readable report.

    Pipeline:
        1. Validate and decode the uploaded image.
        2. Run YOLO inference (uses the singleton loaded at app startup).
        3. Aggregate detections into per-class counts.
        4. Apply the heuristic rule engine (`utils.interpretation.interpret_counts`).
        5. Format a Summary / Observations / Recommendation report.
    """
    raw = await file.read()
    enforce_size(raw)

    try:
        image = read_image_bytes(raw)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    width, height = image_dimensions(image)

    start = time.perf_counter()
    results = yolo_model.predict(image)
    inference_ms = (time.perf_counter() - start) * 1000

    detections = to_detections(results[0]) if results else []
    counts: dict[str, int] = dict(Counter(d.class_name for d in detections))

    rule_based = interpret_counts(counts)
    report_payload = build_report(rule_based)
    if enhance_with_ai:
        if settings.openai_api_key is None:
            report_payload["ai_error"] = "OpenAI API key is not configured."
        else:
            try:
                from utils.openai_report import generate_ai_explanation

                report_payload["ai_explanation"] = generate_ai_explanation(
                    report_payload,
                    api_key=settings.openai_api_key.get_secret_value(),
                    model=settings.openai_model,
                    timeout_seconds=settings.openai_timeout_seconds,
                )
                report_payload["ai_enabled"] = True
            except RuntimeError as exc:
                report_payload["ai_error"] = str(exc)

    logger.info(
        "Analyzed %s in %.1f ms — %d detections, %d finding(s), severity=%s",
        file.filename,
        inference_ms,
        len(detections),
        len(rule_based.get("status", [])),
        rule_based.get("overall_severity"),
    )

    return AnalyzeResponse(
        filename=file.filename or "uploaded.png",
        image_width=width,
        image_height=height,
        inference_time_ms=round(inference_ms, 2),
        counts=counts,
        report=Report(**report_payload),
        rule_based=rule_based,
    )
