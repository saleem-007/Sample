"""Image decoding, validation, preprocessing and annotation helpers."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Iterable, Tuple, Union

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from app.schemas import Detection
from utils.logger import get_logger

logger = get_logger(__name__)

_ALLOWED_FORMATS = {"JPEG", "JPG", "PNG", "BMP", "TIFF"}
_DEFAULT_TARGET_SIZE: Tuple[int, int] = (640, 640)


def preprocess_image(
    image_path: Union[str, Path],
    target_size: Tuple[int, int] = _DEFAULT_TARGET_SIZE,
    *,
    to_rgb: bool = True,
    dtype: np.dtype = np.float32,
) -> np.ndarray:
    """Load an image from disk and prepare it for model inference.

    Steps:
        1. Validate the path and load the image with OpenCV.
        2. Convert BGR -> RGB (OpenCV loads BGR by default).
        3. Resize to ``target_size`` using area interpolation (good for downscaling).
        4. Normalise pixel values from [0, 255] -> [0.0, 1.0].

    Args:
        image_path: Filesystem path to the image (jpg/png/bmp/tiff).
        target_size: ``(width, height)`` to resize to. Defaults to ``(640, 640)``.
        to_rgb: If True, convert BGR to RGB. Set False if the consumer expects BGR.
        dtype: Output dtype for the normalised array. Defaults to ``np.float32``.

    Returns:
        A normalised ``np.ndarray`` of shape ``(target_h, target_w, 3)`` with
        values in ``[0.0, 1.0]``.

    Raises:
        FileNotFoundError: If ``image_path`` does not exist.
        ValueError: If the file cannot be decoded as an image or ``target_size``
            is invalid.
    """
    path = Path(image_path)

    if not path.exists():
        logger.error("Image file not found: %s", path)
        raise FileNotFoundError(f"Image file not found: {path}")

    if not path.is_file():
        logger.error("Path is not a regular file: %s", path)
        raise ValueError(f"Path is not a regular file: {path}")

    width, height = target_size
    if width <= 0 or height <= 0:
        raise ValueError(f"target_size must be positive, got {target_size}")

    logger.debug("Loading image from %s", path)
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        logger.error("OpenCV failed to decode image: %s", path)
        raise ValueError(
            f"Failed to load image at {path}. The file may be corrupt or in an unsupported format."
        )

    try:
        if to_rgb:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        original_h, original_w = image.shape[:2]
        resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

        normalised = resized.astype(dtype) / 255.0
    except cv2.error as exc:
        logger.exception("OpenCV error while preprocessing %s", path)
        raise ValueError(f"OpenCV failed while preprocessing {path}: {exc}") from exc

    logger.info(
        "Preprocessed %s: %dx%d -> %dx%d (dtype=%s, range=[%.3f, %.3f])",
        path.name,
        original_w,
        original_h,
        width,
        height,
        normalised.dtype,
        float(normalised.min()),
        float(normalised.max()),
    )

    return normalised


def read_image_bytes(raw: bytes) -> np.ndarray:
    """Decode raw bytes into an RGB numpy array, raising on invalid input."""
    try:
        image = Image.open(BytesIO(raw))
        image.verify()
    except Exception as exc:  # noqa: BLE001
        raise ValueError("Uploaded file is not a valid image.") from exc

    image = Image.open(BytesIO(raw))
    if image.format and image.format.upper() not in _ALLOWED_FORMATS:
        raise ValueError(f"Unsupported image format: {image.format}")

    return np.array(image.convert("RGB"))


def image_dimensions(image: np.ndarray) -> Tuple[int, int]:
    height, width = image.shape[:2]
    return width, height


def annotate_image(image: np.ndarray, detections: Iterable[Detection]) -> Image.Image:
    """Draw bounding boxes and labels on a copy of the image."""
    pil_image = Image.fromarray(image).convert("RGB")
    draw = ImageDraw.Draw(pil_image)

    try:
        font = ImageFont.load_default()
    except Exception:  # noqa: BLE001
        font = None

    for det in detections:
        box = det.bbox
        draw.rectangle(
            [(box.x_min, box.y_min), (box.x_max, box.y_max)],
            outline="red",
            width=2,
        )
        label = f"{det.class_name} {det.confidence:.2f}"
        draw.text((box.x_min, max(box.y_min - 12, 0)), label, fill="red", font=font)

    return pil_image
