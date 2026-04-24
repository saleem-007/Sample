"""Heuristic medical interpretation of blood-cell detection counts.

DISCLAIMER
----------
These rules are simplified heuristics intended for demonstration and triage UX
purposes only. They are NOT a substitute for laboratory analysis or qualified
medical diagnosis. Counts here are *per-image detections* from microscopy, not
absolute clinical values (e.g., cells/uL). Calibrate the thresholds for your
imaging setup before relying on the output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Tuple

from utils.logger import get_logger

logger = get_logger(__name__)

DISCLAIMER = (
    "Heuristic interpretation based on per-image detection counts. "
    "Not a clinical diagnosis. Consult a qualified medical professional."
)

_SEVERITY_RANK = {"info": 0, "warning": 1, "alert": 2}


@dataclass(frozen=True)
class CountThresholds:
    """Per-image detection-count thresholds.

    Each pair defines an inclusive normal range ``[low, high]``. Counts strictly
    below ``low`` are flagged as "low"; counts strictly above ``high`` as "high".
    Defaults are illustrative and should be tuned for the imaging pipeline.
    """

    rbc_low: int = 50
    rbc_high: int = 250
    wbc_low: int = 2
    wbc_high: int = 15
    platelets_low: int = 5
    platelets_high: int = 80


def _classify(
    cell: str,
    count: int,
    low: int,
    high: int,
    *,
    indication_low: str,
    indication_high: str,
    severity_low: str = "warning",
    severity_high: str = "warning",
) -> Optional[Dict[str, Any]]:
    if count < low:
        return {
            "cell": cell,
            "level": "low",
            "severity": severity_low,
            "count": count,
            "reference_range": [low, high],
            "message": f"Low {cell} count ({count} < {low}): {indication_low}.",
        }
    if count > high:
        return {
            "cell": cell,
            "level": "high",
            "severity": severity_high,
            "count": count,
            "reference_range": [low, high],
            "message": f"High {cell} count ({count} > {high}): {indication_high}.",
        }
    return None


def _normalise(counts: Mapping[str, int]) -> Tuple[int, int, int]:
    norm = {str(k).strip().lower(): int(v) for k, v in counts.items()}
    rbc = norm.get("rbc", 0)
    wbc = norm.get("wbc", 0)
    platelets = norm.get("platelets", norm.get("platelet", 0))
    return rbc, wbc, platelets


def interpret_counts(
    counts: Mapping[str, int],
    thresholds: Optional[CountThresholds] = None,
) -> Dict[str, Any]:
    """Convert per-class cell counts into a structured interpretation.

    Args:
        counts: Mapping of class name -> count, e.g. ``{"RBC": 120, "WBC": 25, "Platelets": 4}``.
            Keys are matched case-insensitively. ``"Platelet"`` and ``"Platelets"`` are aliased.
        thresholds: Optional ``CountThresholds``. Defaults to the (illustrative) values
            on the dataclass.

    Returns:
        A dict shaped as::

            {
                "status": [ {cell, level, severity, count, reference_range, message}, ... ],
                "summary": "...",
                "overall_severity": "info" | "warning" | "alert",
                "counts": {"RBC": int, "WBC": int, "Platelets": int},
                "disclaimer": str,
            }

    Raises:
        ValueError: If any provided count is negative.
    """
    thresholds = thresholds or CountThresholds()
    rbc, wbc, platelets = _normalise(counts)

    if min(rbc, wbc, platelets) < 0:
        raise ValueError("Cell counts must be non-negative.")

    if rbc + wbc + platelets == 0:
        result: Dict[str, Any] = {
            "status": [],
            "summary": (
                "No blood cells were detected in the uploaded image. "
                "The result is inconclusive and should not be interpreted as low cell counts."
            ),
            "overall_severity": "warning",
            "analysis_quality": "no_detections",
            "counts": {"RBC": rbc, "WBC": wbc, "Platelets": platelets},
            "disclaimer": DISCLAIMER,
        }
        logger.info("Interpretation: no blood-cell detections, result=inconclusive")
        return result

    findings: List[Dict[str, Any]] = []

    rbc_finding = _classify(
        "RBC", rbc, thresholds.rbc_low, thresholds.rbc_high,
        indication_low="possible anemia indication",
        indication_high="possible polycythemia or dehydration",
    )
    if rbc_finding:
        findings.append(rbc_finding)

    wbc_finding = _classify(
        "WBC", wbc, thresholds.wbc_low, thresholds.wbc_high,
        indication_low="possible immunodeficiency or marrow suppression",
        indication_high="possible infection or inflammatory response",
        severity_high="alert",
    )
    if wbc_finding:
        findings.append(wbc_finding)

    platelets_finding = _classify(
        "Platelets", platelets, thresholds.platelets_low, thresholds.platelets_high,
        indication_low="clotting risk (thrombocytopenia indication)",
        indication_high="possible thrombocytosis",
        severity_low="alert",
    )
    if platelets_finding:
        findings.append(platelets_finding)

    if not findings:
        summary = (
            "All measured cell counts fall within heuristic reference ranges. "
            "No abnormalities flagged."
        )
        overall_severity = "info"
    else:
        findings.sort(key=lambda f: _SEVERITY_RANK[f["severity"]], reverse=True)
        overall_severity = findings[0]["severity"]
        bullet_list = "; ".join(f["message"] for f in findings)
        prefix = "Alert" if overall_severity == "alert" else "Notice"
        summary = (
            f"{prefix}: {len(findings)} finding(s) detected. {bullet_list} "
            "Clinical follow-up recommended."
        )

    result: Dict[str, Any] = {
        "status": findings,
        "summary": summary,
        "overall_severity": overall_severity,
        "counts": {"RBC": rbc, "WBC": wbc, "Platelets": platelets},
        "disclaimer": DISCLAIMER,
    }

    logger.info(
        "Interpretation: %d finding(s), overall=%s, counts=RBC:%d WBC:%d Plt:%d",
        len(findings), overall_severity, rbc, wbc, platelets,
    )
    return result


# ---------------------------------------------------------------------------
# Human-readable report layer
# ---------------------------------------------------------------------------

# Plain-language phrasing for each (cell, level) pair. Hedged on purpose:
# we never claim a diagnosis, only describe what the count "may suggest".
_PLAIN_LANGUAGE: Dict[Tuple[str, str], str] = {
    ("RBC", "low"): (
        "The red blood cell count appears lower than expected. "
        "Lower red cell counts are sometimes associated with anemia."
    ),
    ("RBC", "high"): (
        "The red blood cell count appears higher than expected. "
        "Higher counts can sometimes occur with dehydration or certain other conditions."
    ),
    ("WBC", "low"): (
        "The white blood cell count appears lower than expected. "
        "Lower white cell counts can sometimes occur when the immune system is weakened."
    ),
    ("WBC", "high"): (
        "The white blood cell count appears higher than expected. "
        "Higher white cell counts are sometimes seen with infection or inflammation."
    ),
    ("Platelets", "low"): (
        "The platelet count appears lower than expected. "
        "Lower platelet counts can affect how easily the blood forms clots."
    ),
    ("Platelets", "high"): (
        "The platelet count appears higher than expected. "
        "Higher platelet counts can sometimes occur with inflammation or other conditions."
    ),
}

_RECOMMENDATION_BY_SEVERITY: Dict[str, str] = {
    "info": (
        "No unusual cell counts were flagged by this automated check. "
        "This tool does not replace a clinical blood test — please continue any "
        "care plan recommended by your healthcare provider."
    ),
    "warning": (
        "Some measurements fell outside the expected range. "
        "It may be helpful to share these results with a qualified healthcare "
        "professional for review."
    ),
    "alert": (
        "One or more measurements fell well outside the expected range. "
        "Please consider consulting a qualified healthcare professional soon "
        "so the results can be reviewed in proper clinical context."
    ),
}

_RECOMMENDATION_BY_QUALITY: Dict[str, str] = {
    "no_detections": (
        "Please try another clear microscope image or use a trained blood-cell "
        "YOLO model. If this image should contain visible cells, have the result "
        "reviewed by a qualified professional."
    ),
}


def _observation_for(finding: Dict[str, Any]) -> str:
    cell = finding["cell"]
    level = finding["level"]
    count = finding["count"]
    low, high = finding["reference_range"]

    base = _PLAIN_LANGUAGE.get(
        (cell, level),
        f"The {cell} count is {level} compared to the expected range.",
    )
    return f"{base} (Detected {count}; expected range {low}-{high}.)"


def _summary_for(interpretation: Mapping[str, Any]) -> str:
    findings = interpretation.get("status") or []
    counts = interpretation.get("counts", {})
    counts_str = ", ".join(f"{k}: {v}" for k, v in counts.items())

    if interpretation.get("analysis_quality") == "no_detections":
        return (
            "No blood cells were detected in the uploaded image "
            f"({counts_str}). This means the analysis is inconclusive, not that "
            "the cell counts are medically low."
        )

    if not findings:
        return (
            f"This automated review of the image found no unusual cell counts "
            f"({counts_str}). All measured values fall within the expected ranges "
            "used by this tool."
        )

    severity = interpretation.get("overall_severity", "warning")
    n = len(findings)
    word = "observation" if n == 1 else "observations"

    if severity == "alert":
        lead = (
            f"This automated review identified {n} {word} that may need attention "
            f"({counts_str})."
        )
    else:
        lead = (
            f"This automated review identified {n} {word} outside the expected "
            f"range ({counts_str})."
        )
    return lead + " Please review the details below."


def build_report(interpretation: Mapping[str, Any]) -> Dict[str, Any]:
    """Convert ``interpret_counts`` output into a Summary / Observations / Recommendation report.

    Args:
        interpretation: The dict returned by :func:`interpret_counts`.

    Returns:
        A dict with structured sections plus a pre-rendered ``report_text``::

            {
                "summary": "...",
                "observations": ["...", ...],
                "recommendation": "...",
                "report_text": "Summary\\n-------\\n...",
                "disclaimer": "...",
            }
    """
    findings = list(interpretation.get("status") or [])
    severity = interpretation.get("overall_severity", "info")

    summary = _summary_for(interpretation)
    observations = [_observation_for(f) for f in findings]
    recommendation = _RECOMMENDATION_BY_QUALITY.get(
        str(interpretation.get("analysis_quality")),
        _RECOMMENDATION_BY_SEVERITY.get(
            severity, _RECOMMENDATION_BY_SEVERITY["warning"]
        ),
    )
    disclaimer = interpretation.get("disclaimer", DISCLAIMER)

    report_text = _render_text_report(summary, observations, recommendation, disclaimer)

    return {
        "summary": summary,
        "observations": observations,
        "recommendation": recommendation,
        "report_text": report_text,
        "disclaimer": disclaimer,
    }


def _render_text_report(
    summary: str,
    observations: List[str],
    recommendation: str,
    disclaimer: str,
) -> str:
    obs_block = (
        "\n".join(f"- {item}" for item in observations)
        if observations
        else "- No blood-cell abnormalities were reported by the rule engine."
    )
    return (
        "Summary\n"
        "-------\n"
        f"{summary}\n\n"
        "Observations\n"
        "------------\n"
        f"{obs_block}\n\n"
        "Recommendation\n"
        "--------------\n"
        f"{recommendation}\n\n"
        f"Note: {disclaimer}"
    )


def report_from_counts(
    counts: Mapping[str, int],
    thresholds: Optional[CountThresholds] = None,
) -> Dict[str, Any]:
    """Convenience: run :func:`interpret_counts` and immediately build a report."""
    return build_report(interpret_counts(counts, thresholds=thresholds))


if __name__ == "__main__":  # pragma: no cover
    import json

    demo = {"RBC": 30, "WBC": 25, "Platelets": 4}
    report = report_from_counts(demo)
    print(json.dumps({k: v for k, v in report.items() if k != "report_text"}, indent=2))
    print("\n" + report["report_text"])
