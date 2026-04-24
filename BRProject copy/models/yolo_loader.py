"""Thread-safe singleton wrapper around the Ultralytics YOLO model."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, List, Optional

import numpy as np

from app.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class YOLOModel:
    """Lazy, thread-safe wrapper so the heavy YOLO import only happens once."""

    def __init__(self, weights_path: Path, device: str) -> None:
        self._weights_path = weights_path
        self._device = device
        self._model: Optional[Any] = None
        self._lock = threading.Lock()

    def load(self) -> None:
        if self._model is not None:
            return

        with self._lock:
            if self._model is not None:
                return

            try:
                from ultralytics import YOLO
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "ultralytics is not installed. Install dependencies from requirements.txt."
                ) from exc

            if not self._weights_path.exists():
                logger.warning(
                    "Weights file %s not found. Falling back to pretrained 'yolov8n.pt'.",
                    self._weights_path,
                )
                self._model = YOLO("yolov8n.pt")
            else:
                self._model = YOLO(str(self._weights_path))

            self._model.to(self._device)

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def class_names(self) -> dict[int, str]:
        if self._model is None:
            return {}
        return dict(self._model.names)

    def predict(self, image: np.ndarray) -> List[Any]:
        if self._model is None:
            self.load()
        assert self._model is not None
        return self._model.predict(
            source=image,
            imgsz=settings.image_size,
            conf=settings.confidence_threshold,
            iou=settings.iou_threshold,
            device=self._device,
            verbose=False,
        )


yolo_model = YOLOModel(
    weights_path=settings.model_weights_path,
    device=settings.device,
)
