"""Smoke-test the FastAPI /api/v1/analyze endpoint with a sample image.

Usage:
    python test_api.py data/samples/blood_smear.jpg
    python test_api.py data/samples/blood_smear.jpg --url http://localhost:8000/api/v1/analyze
    python test_api.py data/samples/blood_smear.jpg --enhance-with-ai
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_URL = "http://localhost:8000/api/v1/analyze"
TIMEOUT_SECONDS = 60


def _build_multipart_body(file_path: Path, field_name: str = "file") -> tuple[bytes, str]:
    """Build a minimal multipart/form-data request body using stdlib only."""
    boundary = f"----blood-cell-api-{uuid.uuid4().hex}"
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    file_bytes = file_path.read_bytes()

    parts = [
        f"--{boundary}\r\n".encode(),
        (
            f'Content-Disposition: form-data; name="{field_name}"; '
            f'filename="{file_path.name}"\r\n'
        ).encode(),
        f"Content-Type: {content_type}\r\n\r\n".encode(),
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def send_image(api_url: str, image_path: Path) -> Dict[str, Any]:
    """Upload an image to the analyze endpoint and return parsed JSON."""
    body, content_type = _build_multipart_body(image_path)
    request = Request(
        api_url,
        data=body,
        method="POST",
        headers={
            "Content-Type": content_type,
            "Content-Length": str(len(body)),
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API returned HTTP {exc.code}: {error_body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not connect to API at {api_url}: {exc.reason}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"API response was not valid JSON: {raw[:500]}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("API response JSON must be an object.")
    return payload


def validate_response(payload: Dict[str, Any]) -> List[str]:
    """Return a list of output-format validation errors."""
    errors: List[str] = []

    counts = payload.get("counts")
    if not isinstance(counts, dict):
        errors.append("`counts` must be an object.")
    else:
        for key, value in counts.items():
            if not isinstance(key, str):
                errors.append("All `counts` keys must be strings.")
            if not isinstance(value, int):
                errors.append(f"`counts.{key}` must be an integer.")

    report = payload.get("report")
    if not isinstance(report, dict):
        errors.append("`report` must be an object.")
        return errors

    for field in ("summary", "recommendation", "disclaimer"):
        if not isinstance(report.get(field), str) or not report[field].strip():
            errors.append(f"`report.{field}` must be a non-empty string.")

    observations = report.get("observations")
    if not isinstance(observations, list):
        errors.append("`report.observations` must be a list.")
    elif not all(isinstance(item, str) for item in observations):
        errors.append("Every `report.observations` item must be a string.")

    if "ai_enabled" in report and not isinstance(report["ai_enabled"], bool):
        errors.append("`report.ai_enabled` must be a boolean when present.")

    for optional_field in ("ai_explanation", "ai_error"):
        value = report.get(optional_field)
        if value is not None and not isinstance(value, str):
            errors.append(f"`report.{optional_field}` must be a string or null.")

    return errors


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test the Blood Cell Detection API.")
    parser.add_argument("image", type=Path, help="Path to a sample image.")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"API URL (default: {DEFAULT_URL}).")
    parser.add_argument(
        "--enhance-with-ai",
        action="store_true",
        help="Call the optional OpenAI-enhanced report path.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if not args.image.is_file():
        print(f"Image file not found: {args.image}", file=sys.stderr)
        return 1

    api_url = args.url
    if args.enhance_with_ai:
        separator = "&" if "?" in api_url else "?"
        api_url = f"{api_url}{separator}enhance_with_ai=true"

    print(f"Sending {args.image} -> {api_url}")

    try:
        payload = send_image(api_url, args.image)
    except RuntimeError as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1

    print("\nResponse JSON:")
    print(json.dumps(payload, indent=2))

    errors = validate_response(payload)
    if errors:
        print("\nValidation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("\nValidation passed: response contains valid `counts` and `report` fields.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
