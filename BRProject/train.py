"""CLI: train a YOLO model on a custom dataset.

Examples:
    # Quickstart with the project's blood-cell YAML and YOLOv8n.
    python train.py --data data/blood_cells.yaml

    # Custom hyperparameters on a single GPU.
    python train.py \\
        --data data/blood_cells.yaml \\
        --model yolov8s.pt \\
        --epochs 150 --batch 32 --imgsz 640 \\
        --device 0 --name bcd_v1

    # Resume the previous run, no auto-publish to models/weights/best.pt.
    python train.py --data data/blood_cells.yaml --name bcd_v1 --resume --no-publish
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.config import settings
from utils.logger import get_logger
from utils.training import TrainingConfig, train_yolo

logger = get_logger("train")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train a YOLO model with Ultralytics on a custom dataset.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--data", type=Path, required=True, help="Path to dataset YAML.")
    parser.add_argument("--model", default="yolov8n.pt", help="Base model / weights to start from.")

    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs.")
    parser.add_argument(
        "--batch", type=int, default=16,
        help="Batch size. Use -1 to let Ultralytics auto-fit GPU memory.",
    )
    parser.add_argument("--imgsz", type=int, default=640, help="Training image size (square).")

    parser.add_argument("--device", default="cpu", help="cpu | cuda | 0 | 0,1 | mps")
    parser.add_argument("--workers", type=int, default=8, help="DataLoader worker count.")
    parser.add_argument(
        "--optimizer", default="auto",
        choices=("auto", "SGD", "Adam", "AdamW", "RMSProp"),
        help="Optimizer.",
    )
    parser.add_argument("--lr0", type=float, default=0.01, help="Initial learning rate.")
    parser.add_argument(
        "--patience", type=int, default=50,
        help="Early-stopping patience in epochs (0 disables).",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")

    parser.add_argument(
        "--project", type=Path, default=Path("runs/detect"),
        help="Parent directory for run outputs.",
    )
    parser.add_argument("--name", default="train", help="Run subdirectory name.")
    parser.add_argument(
        "--exist-ok", action="store_true",
        help="Overwrite the run directory if it already exists.",
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume from last.pt in <project>/<name>.",
    )
    parser.add_argument(
        "--no-pretrained", action="store_true",
        help="Train from scratch instead of fine-tuning.",
    )

    parser.add_argument(
        "--publish-to", type=Path, default=settings.model_weights_path,
        help=(
            "Where to copy best.pt after training "
            f"(default: {settings.model_weights_path})."
        ),
    )
    parser.add_argument(
        "--no-publish", action="store_true",
        help="Do not copy best.pt to --publish-to.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    config = TrainingConfig(
        data=args.data,
        model=args.model,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        workers=args.workers,
        optimizer=args.optimizer,
        lr0=args.lr0,
        patience=args.patience,
        seed=args.seed,
        project=args.project,
        name=args.name,
        exist_ok=args.exist_ok,
        resume=args.resume,
        pretrained=not args.no_pretrained,
        publish_best_to=None if args.no_publish else args.publish_to,
    )

    try:
        result = train_yolo(config)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        logger.error("%s", exc)
        return 1

    payload = {"config": config.to_dict(), "result": result.to_dict()}
    print(json.dumps(payload, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
