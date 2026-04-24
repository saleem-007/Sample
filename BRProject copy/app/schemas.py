"""Pydantic schemas describing API request and response payloads."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x_min: float = Field(..., description="Top-left X coordinate in pixels.")
    y_min: float = Field(..., description="Top-left Y coordinate in pixels.")
    x_max: float = Field(..., description="Bottom-right X coordinate in pixels.")
    y_max: float = Field(..., description="Bottom-right Y coordinate in pixels.")


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: BoundingBox


class DetectionResponse(BaseModel):
    filename: str
    image_width: int
    image_height: int
    inference_time_ms: float
    detections: List[Detection]
    counts: dict[str, int]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str


class Report(BaseModel):
    summary: str
    observations: List[str]
    recommendation: str
    report_text: str
    disclaimer: str
    ai_explanation: str | None = Field(
        default=None,
        description="Optional OpenAI-generated short, patient-friendly explanation.",
    )
    ai_enabled: bool = Field(
        default=False,
        description="True when OpenAI enhancement was requested and succeeded.",
    )
    ai_error: str | None = Field(
        default=None,
        description="Non-blocking OpenAI enhancement error, if enhancement was requested.",
    )


class AnalyzeResponse(BaseModel):
    """Top-level payload returned by ``POST /analyze``."""

    filename: str
    image_width: int
    image_height: int
    inference_time_ms: float
    counts: Dict[str, int] = Field(
        default_factory=dict,
        description="Per-class detection counts, e.g. {\"RBC\": 120, \"WBC\": 10, \"Platelets\": 50}.",
    )
    report: Report
    rule_based: Dict[str, Any] = Field(
        default_factory=dict,
        description="Raw rule-engine output (status, severity, reference ranges).",
    )
