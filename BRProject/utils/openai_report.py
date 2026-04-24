"""Optional OpenAI helper for rewriting report JSON into plain language.

This module intentionally imports the OpenAI SDK inside the function so the
main API can run without the optional dependency when AI enhancement is off.
"""

from __future__ import annotations

import json
from importlib import import_module
from typing import Any, Mapping

from utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You rewrite automated blood-cell analysis reports for non-experts.
Keep the response short, calm, and safe.
Do not diagnose.
Do not recommend treatment.
Do not add facts that are not present in the JSON.
Use simple language and recommend professional review when results are outside range.
Return only the final explanation text."""


def generate_ai_explanation(
    report: Mapping[str, Any],
    *,
    api_key: str,
    model: str,
    timeout_seconds: float = 8.0,
) -> str:
    """Generate a short, human-friendly explanation from report JSON.

    Raises:
        RuntimeError: If the OpenAI SDK is missing or the API call fails.
    """
    try:
        OpenAI = getattr(import_module("openai"), "OpenAI")
    except (ImportError, AttributeError) as exc:  # pragma: no cover
        raise RuntimeError(
            "OpenAI enhancement requested, but the 'openai' package is not installed."
        ) from exc

    try:
        client = OpenAI(api_key=api_key, timeout=timeout_seconds)
        response = client.chat.completions.create(
            model=model,
            temperature=0.2,
            max_tokens=180,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Rewrite this report JSON as one short, simple explanation "
                        "for a patient-facing app:\n"
                        f"{json.dumps(report, ensure_ascii=False)}"
                    ),
                },
            ],
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("OpenAI report enhancement failed")
        raise RuntimeError("OpenAI report enhancement failed.") from exc

    content = response.choices[0].message.content if response.choices else None
    explanation = (content or "").strip()
    if not explanation:
        raise RuntimeError("OpenAI returned an empty explanation.")

    return explanation
