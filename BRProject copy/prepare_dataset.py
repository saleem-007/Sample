"""CLI: turn a flat folder of images + YOLO .txt labels into the canonical YOLO layout.

Examples:
    # Default 80/20 split, copy files into ./data/dataset, write dataset.yaml.
    python prepare_dataset.py \\
        --images-dir raw/images \\
        --labels-dir raw/labels \\
        --output-dir data/dataset

    # Symlink instead of copy, custom split, custom classes:
    python prepare_dataset.py \\
        --images-dir raw/images --labels-dir raw/labels \\
        --output-dir data/dataset \\
        --val-split 0.15 --seed 7 --mode symlink \\
        --classes RBC WBC Platelets
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from utils.dataset import prepare_dataset
from utils.logger import get_logger

logger = get_logger("prepare_dataset")

DEFAULT_CLASSES = ("RBC", "WBC", "Platelets")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a YOLO-format dataset (images/{train,val}, labels/{train,val}).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--images-dir", type=Path, required=True, help="Folder of source images.")
    parser.add_argument("--labels-dir", type=Path, required=True, help="Folder of YOLO .txt label files.")
    parser.add_argument(
        "--output-dir", type=Path, default=Path("data/dataset"),
        help="Destination dataset root (default: data/dataset).",
    )
    parser.add_argument(
        "--classes", nargs="+", default=list(DEFAULT_CLASSES),
        help=f"Class names in class_id order (default: {' '.join(DEFAULT_CLASSES)}).",
    )
    parser.add_argument("--val-split", type=float, default=0.2, help="Validation fraction (0-1).")
    parser.add_argument("--seed", type=int, default=42, help="Shuffle seed for reproducibility.")
    parser.add_argument(
        "--mode", choices=("copy", "symlink", "move"), default="copy",
        help="How to place files into the dataset folder.",
    )
    parser.add_argument(
        "--allow-missing-labels", action="store_true",
        help="Skip images without a matching label instead of erroring.",
    )
    parser.add_argument(
        "--no-yaml", action="store_true",
        help="Do not generate dataset.yaml (useful if you maintain it by hand).",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    try:
        summary = prepare_dataset(
            images_dir=args.images_dir,
            labels_dir=args.labels_dir,
            output_dir=args.output_dir,
            class_names=args.classes,
            val_split=args.val_split,
            seed=args.seed,
            mode=args.mode,
            require_labels=not args.allow_missing_labels,
            write_yaml=not args.no_yaml,
        )
    except (FileNotFoundError, ValueError) as exc:
        logger.error("%s", exc)
        return 1

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
