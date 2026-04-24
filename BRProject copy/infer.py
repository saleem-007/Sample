"""CLI: run YOLO inference on a single image and save an annotated copy.

Usage:
    python infer.py path/to/image.jpg
    python infer.py path/to/image.jpg --weights models/weights/best.pt --device cuda
    python infer.py path/to/image.jpg -o data/outputs/result.jpg --conf 0.4
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from utils.inference import run_inference
from utils.logger import get_logger

logger = get_logger("infer")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run YOLO inference on an image.")
    parser.add_argument("image", type=Path, help="Path to the input image.")
    parser.add_argument(
        "--weights",
        default="yolov8n.pt",
        help="Path to .pt weights or an Ultralytics model alias (default: yolov8n.pt).",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Where to save the annotated image. Defaults to data/outputs/<name>_pred.jpg.",
    )
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold.")
    parser.add_argument("--iou", type=float, default=0.45, help="NMS IoU threshold.")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference image size.")
    parser.add_argument("--device", default="cpu", help="cpu | cuda | cuda:0 | mps ...")
    parser.add_argument(
        "--no-save", action="store_true", help="Skip writing the annotated image."
    )
    parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Do not draw the per-class counts panel on the annotated image.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    try:
        result = run_inference(
            image_path=args.image,
            weights=args.weights,
            output_path=args.output,
            conf=args.conf,
            iou=args.iou,
            imgsz=args.imgsz,
            device=args.device,
            save=not args.no_save,
            draw_summary=not args.no_summary,
        )
    except (FileNotFoundError, ValueError, IOError) as exc:
        logger.error("%s", exc)
        return 1

    payload = {
        "image": str(result.image_path),
        "size": [result.image_width, result.image_height],
        "output": str(result.output_path) if result.output_path else None,
        "num_detections": result.total,
        "counts": result.counts,
        "detections": [d.to_dict() for d in result.detections],
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
