"""Configurable YOLO training pipeline built on top of Ultralytics."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, Optional, Union

from app.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TrainingConfig:
    """All knobs for a YOLO training run.

    Only the most common Ultralytics arguments are exposed here. Anything else
    can be forwarded by passing ``extra`` to ``train_yolo``.
    """

    data: Path                                     # Path to dataset YAML.
    model: str = "yolov8n.pt"                      # Base model / weights to start from.
    epochs: int = 100
    batch: int = 16                                # -1 lets Ultralytics auto-fit memory.
    imgsz: int = 640
    device: str = "cpu"                            # "cpu" | "cuda" | "0" | "0,1" | "mps"
    workers: int = 8
    optimizer: str = "auto"                        # "SGD" | "Adam" | "AdamW" | "auto"
    lr0: float = 0.01
    patience: int = 50                             # Early-stopping patience (epochs).
    seed: int = 42

    project: Path = Path("runs/detect")            # Parent dir for run outputs.
    name: str = "train"                            # Run subdirectory name.
    exist_ok: bool = False                         # Overwrite existing run directory?
    resume: bool = False                           # Resume from last.pt in `name`.
    pretrained: bool = True

    # Where to copy the best.pt after training. Defaults to the path the API serves from.
    publish_best_to: Optional[Path] = field(
        default_factory=lambda: settings.model_weights_path
    )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        for k in ("data", "project", "publish_best_to"):
            if d[k] is not None:
                d[k] = str(d[k])
        return d


@dataclass
class TrainingResult:
    """Summary of a finished training run."""

    run_dir: Path
    best_weights: Optional[Path]
    last_weights: Optional[Path]
    published_to: Optional[Path]
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_dir": str(self.run_dir),
            "best_weights": str(self.best_weights) if self.best_weights else None,
            "last_weights": str(self.last_weights) if self.last_weights else None,
            "published_to": str(self.published_to) if self.published_to else None,
            "metrics": self.metrics,
        }


def _load_yolo(model_name: str):
    try:
        from ultralytics import YOLO
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "ultralytics is not installed. Run: pip install -r requirements.txt"
        ) from exc
    return YOLO(model_name)


def _extract_metrics(results: Any) -> Dict[str, Any]:
    """Pull the most useful summary metrics out of an Ultralytics results object."""
    metrics: Dict[str, Any] = {}
    results_dict = getattr(results, "results_dict", None)
    if isinstance(results_dict, dict):
        for k, v in results_dict.items():
            try:
                metrics[k] = float(v)
            except (TypeError, ValueError):
                metrics[k] = v

    box = getattr(results, "box", None)
    if box is not None:
        for attr in ("map", "map50", "map75", "mp", "mr"):
            value = getattr(box, attr, None)
            if value is not None:
                try:
                    metrics.setdefault(f"box/{attr}", float(value))
                except (TypeError, ValueError):
                    pass

    return metrics


def train_yolo(
    config: TrainingConfig,
    *,
    extra: Optional[Dict[str, Any]] = None,
) -> TrainingResult:
    """Train a YOLO model end-to-end and (optionally) publish the best weights.

    Args:
        config: Training hyperparameters and IO locations.
        extra: Additional keyword arguments forwarded to ``model.train`` (e.g.
            ``{"mosaic": 1.0, "cos_lr": True}``). Anything in here overrides the
            corresponding fields from ``config``.

    Returns:
        A ``TrainingResult`` with paths to the best/last checkpoints and
        the parsed validation metrics.
    """
    data_path = Path(config.data)
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset YAML not found: {data_path}")
    if not 0 < config.epochs:
        raise ValueError(f"epochs must be > 0, got {config.epochs}")
    if config.batch == 0:
        raise ValueError("batch must be > 0 (or -1 for auto)")
    if config.imgsz <= 0:
        raise ValueError(f"imgsz must be > 0, got {config.imgsz}")

    logger.info("Loading base model '%s'", config.model)
    model = _load_yolo(config.model)

    train_kwargs: Dict[str, Any] = {
        "data": str(data_path),
        "epochs": config.epochs,
        "batch": config.batch,
        "imgsz": config.imgsz,
        "device": config.device,
        "workers": config.workers,
        "optimizer": config.optimizer,
        "lr0": config.lr0,
        "patience": config.patience,
        "seed": config.seed,
        "project": str(config.project),
        "name": config.name,
        "exist_ok": config.exist_ok,
        "resume": config.resume,
        "pretrained": config.pretrained,
    }
    if extra:
        train_kwargs.update(extra)

    logger.info("Starting YOLO training: %s", train_kwargs)
    train_results = model.train(**train_kwargs)

    save_dir = Path(getattr(train_results, "save_dir", config.project / config.name))
    weights_dir = save_dir / "weights"
    best_weights = weights_dir / "best.pt" if (weights_dir / "best.pt").exists() else None
    last_weights = weights_dir / "last.pt" if (weights_dir / "last.pt").exists() else None
    logger.info("Training finished. Run directory: %s", save_dir)

    val_metrics: Dict[str, Any] = {}
    if best_weights is not None:
        try:
            logger.info("Running validation on best weights to capture final metrics")
            val_model = _load_yolo(str(best_weights))
            val_results = val_model.val(
                data=str(data_path),
                imgsz=config.imgsz,
                batch=config.batch if config.batch > 0 else 16,
                device=config.device,
                verbose=False,
            )
            val_metrics = _extract_metrics(val_results)
        except Exception:  # noqa: BLE001
            logger.exception("Validation pass failed; continuing without metrics")

    published_to: Optional[Path] = None
    if best_weights is not None and config.publish_best_to is not None:
        target = Path(config.publish_best_to)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(best_weights, target)
        published_to = target
        logger.info("Published best weights -> %s", target)
    elif config.publish_best_to is not None:
        logger.warning("No best.pt found at %s; nothing to publish", weights_dir)

    return TrainingResult(
        run_dir=save_dir,
        best_weights=best_weights,
        last_weights=last_weights,
        published_to=published_to,
        metrics=val_metrics,
    )
