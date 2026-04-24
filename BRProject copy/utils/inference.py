"""End-to-end YOLO inference: load model, predict, draw boxes, save image."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union

import cv2
import numpy as np

from app.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def count_detections_by_class(
    detections: Iterable["InferenceDetection"],
) -> Dict[str, int]:
    """Aggregate detections into a ``{class_label: count}`` mapping.

    The returned dict is sorted by count (descending) so the most common
    class appears first — handy when serialising for dashboards / reports.

    Example:
        >>> count_detections_by_class(result.detections)
        {'RBC': 120, 'Platelets': 50, 'WBC': 10}
    """
    counter = Counter(d.label for d in detections)
    return dict(counter.most_common())


@dataclass(frozen=True)
class InferenceDetection:
    """Single YOLO detection in a friendly, framework-agnostic shape."""

    class_id: int
    label: str
    confidence: float
    bbox: Tuple[float, float, float, float]  # (x_min, y_min, x_max, y_max) in pixels

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class InferenceResult:
    """Aggregated output of `run_inference`."""

    image_path: Path
    image_width: int
    image_height: int
    output_path: Optional[Path]
    detections: List[InferenceDetection]

    @property
    def boxes(self) -> List[Tuple[float, float, float, float]]:
        return [d.bbox for d in self.detections]

    @property
    def labels(self) -> List[str]:
        return [d.label for d in self.detections]

    @property
    def confidences(self) -> List[float]:
        return [d.confidence for d in self.detections]

    @property
    def counts(self) -> Dict[str, int]:
        """Per-class detection counts, e.g. ``{"RBC": 120, "WBC": 10, "Platelets": 50}``."""
        return count_detections_by_class(self.detections)

    @property
    def total(self) -> int:
        return len(self.detections)


_PALETTE = [
    (255, 56, 56), (255, 157, 151), (255, 112, 31), (255, 178, 29),
    (207, 210, 49), (72, 249, 10), (146, 204, 23), (61, 219, 134),
    (26, 147, 52), (0, 212, 187), (44, 153, 168), (0, 194, 255),
    (52, 69, 147), (100, 115, 255), (0, 24, 236), (132, 56, 255),
    (82, 0, 133), (203, 56, 255), (255, 149, 200), (255, 55, 199),
]


def _color_for(class_id: int) -> Tuple[int, int, int]:
    return _PALETTE[class_id % len(_PALETTE)]


def load_yolo_model(weights: Union[str, Path] = "yolov8n.pt", device: str = "cpu"):
    """Load a YOLO model from local weights or an Ultralytics model name.

    Args:
        weights: Path to a local ``.pt`` file or an Ultralytics model alias
            (e.g. ``"yolov8n.pt"``, ``"yolov8s.pt"``, ``"yolo11n.pt"``).
            Aliases will be downloaded by Ultralytics on first use.
        device: ``"cpu"``, ``"cuda"``, ``"cuda:0"``, ``"mps"``, ...

    Returns:
        An initialised ``ultralytics.YOLO`` instance moved to ``device``.

    Raises:
        RuntimeError: If the ``ultralytics`` package is not installed.
        FileNotFoundError: If a local weights path is given but doesn't exist.
    """
    try:
        from ultralytics import YOLO
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "ultralytics is not installed. Run: pip install -r requirements.txt"
        ) from exc

    weights_str = str(weights)
    is_alias = "/" not in weights_str and "\\" not in weights_str and not Path(weights_str).exists()

    if not is_alias and not Path(weights_str).exists():
        raise FileNotFoundError(f"Weights file not found: {weights_str}")

    logger.info("Loading YOLO model from '%s' on device '%s'", weights_str, device)
    model = YOLO(weights_str)
    model.to(device)
    return model


def _draw_summary_panel(image_bgr: np.ndarray, counts: Dict[str, int]) -> None:
    """Overlay a translucent legend with per-class counts in the top-left corner."""
    if not counts:
        return

    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.55
    thickness = 1
    pad = 8
    line_h = 22

    lines = [f"Total: {sum(counts.values())}"] + [f"{lbl}: {n}" for lbl, n in counts.items()]
    text_w = max(cv2.getTextSize(line, font, scale, thickness)[0][0] for line in lines)
    panel_w = text_w + 2 * pad
    panel_h = line_h * len(lines) + pad

    overlay = image_bgr.copy()
    cv2.rectangle(overlay, (0, 0), (panel_w, panel_h), (0, 0, 0), thickness=-1)
    cv2.addWeighted(overlay, 0.55, image_bgr, 0.45, 0, dst=image_bgr)

    for i, line in enumerate(lines):
        y = pad + (i + 1) * line_h - 6
        cv2.putText(
            image_bgr, line, (pad, y), font, scale, (255, 255, 255), thickness, cv2.LINE_AA
        )


def _draw_detections(
    image_bgr: np.ndarray,
    detections: List[InferenceDetection],
    *,
    draw_summary: bool = True,
) -> np.ndarray:
    """Draw boxes + labels (and optionally a per-class counts panel) on a copy of a BGR image."""
    out = image_bgr.copy()
    for det in detections:
        x1, y1, x2, y2 = (int(round(v)) for v in det.bbox)
        color = _color_for(det.class_id)

        cv2.rectangle(out, (x1, y1), (x2, y2), color, thickness=2)

        label = f"{det.label} {det.confidence:.2f}"
        (tw, th), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
        )
        text_y_top = max(y1 - th - baseline - 2, 0)
        cv2.rectangle(
            out,
            (x1, text_y_top),
            (x1 + tw + 4, text_y_top + th + baseline + 2),
            color,
            thickness=-1,
        )
        cv2.putText(
            out,
            label,
            (x1 + 2, text_y_top + th + baseline - 1),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

    if draw_summary:
        _draw_summary_panel(out, count_detections_by_class(detections))

    return out


def run_inference(
    image_path: Union[str, Path],
    weights: Union[str, Path] = "yolov8n.pt",
    *,
    output_path: Optional[Union[str, Path]] = None,
    conf: float = 0.25,
    iou: float = 0.45,
    imgsz: int = 640,
    device: str = "cpu",
    save: bool = True,
    draw_summary: bool = True,
) -> InferenceResult:
    """Load a YOLO model, run inference on a single image and (optionally) save annotated output.

    Args:
        image_path: Path to the input image.
        weights: Local ``.pt`` path or Ultralytics model alias.
        output_path: Where to save the annotated image. Defaults to
            ``settings.output_dir / "<input-stem>_pred.jpg"`` when ``save`` is True.
        conf: Confidence threshold for detections.
        iou: IoU threshold for NMS.
        imgsz: Inference image size (square).
        device: Torch device string.
        save: Whether to write the annotated image to disk.

    Returns:
        An ``InferenceResult`` with bounding boxes, labels and confidence scores.

    Raises:
        FileNotFoundError: If ``image_path`` does not exist.
        ValueError: If the image cannot be decoded.
    """
    img_path = Path(image_path)
    if not img_path.exists():
        raise FileNotFoundError(f"Image file not found: {img_path}")

    image_bgr = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise ValueError(f"Failed to decode image at {img_path}.")

    height, width = image_bgr.shape[:2]
    logger.info("Running inference on %s (%dx%d)", img_path.name, width, height)

    model = load_yolo_model(weights=weights, device=device)

    results = model.predict(
        source=image_bgr,
        imgsz=imgsz,
        conf=conf,
        iou=iou,
        device=device,
        verbose=False,
    )

    detections: List[InferenceDetection] = []
    if results:
        result = results[0]
        names = dict(result.names) if hasattr(result, "names") else {}
        boxes = getattr(result, "boxes", None)

        if boxes is not None and boxes.xyxy is not None and len(boxes) > 0:
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            cls_ids = boxes.cls.cpu().numpy().astype(int)

            for (x1, y1, x2, y2), c, cls_id in zip(xyxy, confs, cls_ids):
                detections.append(
                    InferenceDetection(
                        class_id=int(cls_id),
                        label=names.get(int(cls_id), str(int(cls_id))),
                        confidence=float(c),
                        bbox=(float(x1), float(y1), float(x2), float(y2)),
                    )
                )

    counts = count_detections_by_class(detections)
    if counts:
        summary = ", ".join(f"{lbl}={n}" for lbl, n in counts.items())
        logger.info(
            "Detected %d object(s) in %s [%s]",
            len(detections),
            img_path.name,
            summary,
        )
    else:
        logger.info("No detections in %s", img_path.name)

    saved_to: Optional[Path] = None
    if save:
        if output_path is None:
            settings.output_dir.mkdir(parents=True, exist_ok=True)
            output_path = settings.output_dir / f"{img_path.stem}_pred.jpg"
        saved_to = Path(output_path)
        saved_to.parent.mkdir(parents=True, exist_ok=True)

        annotated = _draw_detections(image_bgr, detections, draw_summary=draw_summary)
        if not cv2.imwrite(str(saved_to), annotated):
            raise IOError(f"Failed to write annotated image to {saved_to}")
        logger.info("Saved annotated image to %s", saved_to)

    return InferenceResult(
        image_path=img_path,
        image_width=width,
        image_height=height,
        output_path=saved_to,
        detections=detections,
    )
