#!/usr/bin/env python3
"""Create a practical automotive test-priority report for a merge request.

The script is intentionally rule-based. It does not try to replace an experienced
test engineer; it helps them quickly see where the MR is most likely to create
vehicle-level risk.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class TestArea:
    """One module or vehicle function that may need focused testing."""

    name: str
    score: int
    priority: str
    reasons: list[str]
    requirement: str
    defect_history: str
    suggested_focus: str


SAFETY_RELATED_AREAS = {
    "adas": "advanced driver assistance",
    "aeb": "automatic emergency braking",
    "brake": "braking control",
    "braking": "braking control",
    "steer": "steering control",
    "steering": "steering control",
    "airbag": "occupant safety",
    "abs": "brake stability control",
    "esp": "vehicle stability control",
    "powertrain": "powertrain control",
    "battery": "battery management",
    "bms": "battery management",
    "charging": "charging control",
    "thermal": "thermal management",
    "motor": "traction control",
    "torque": "torque control",
    "camera": "perception input",
    "radar": "perception input",
    "lidar": "perception input",
}

RISKY_AUTOMOTIVE_TOPICS = {
    "can": "vehicle network integration",
    "lin": "vehicle network integration",
    "flexray": "vehicle network integration",
    "ethernet": "vehicle network integration",
    "uds": "diagnostic communication",
    "obd": "diagnostic communication",
    "diagnostic": "diagnostic behavior",
    "dtc": "fault code handling",
    "calibration": "calibration behavior",
    "autosar": "platform integration",
    "state machine": "state transition logic",
    "fail-safe": "fallback logic",
    "fallback": "fallback logic",
    "degradation": "degraded mode logic",
    "timeout": "timing behavior",
    "timing": "timing behavior",
    "sensor fusion": "multi-sensor decision logic",
    "latency": "real-time behavior",
}

INTEGRATION_HINTS = {
    "ecu": "ECU interface behavior",
    "gateway": "bus routing and signal propagation",
    "telematics": "cloud-to-vehicle interaction",
    "infotainment": "HMI and integration behavior",
    "cluster": "driver display accuracy",
    "diagnostics": "fault detection and service behavior",
    "charging": "plug-in and charge-control behavior",
    "battery": "SOC and thermal protection behavior",
    "adas": "scenario and perception behavior",
    "body control": "vehicle state and actuator behavior",
}

COMPLIANCE_TAGS_THAT_RAISE_TEST_DEPTH = (
    "iso 26262",
    "aspice",
    "sotif",
    "cybersecurity",
    "unece",
)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def as_text(value: Any) -> str:
    """Convert optional JSON values into searchable text."""

    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return str(value)


def words(value: str) -> list[str]:
    clean_value = value.lower().replace("/", " ").replace("_", " ")
    return [word for word in clean_value.split() if word]


def mentions_area(text: str, area: str) -> bool:
    text_lower = text.lower()
    area_words = words(area)
    return area.lower() in text_lower or any(word in text_lower for word in area_words)


def first_matching_requirement(area: str, requirements: list[str]) -> str:
    for requirement in requirements:
        if mentions_area(requirement, area):
            return requirement
    return "No exact requirement match found; treating this as inferred from the touched module."


def matching_defect_history(area: str, defects: list[dict[str, Any]]) -> str:
    matches = []

    for defect in defects:
        module = as_text(defect.get("module"))
        summary = as_text(defect.get("summary"))

        if mentions_area(module, area):
            matches.append(summary or "A previous vehicle defect was recorded for this module.")

    if matches:
        return "; ".join(matches[:2])

    return "No direct field-defect history was supplied for this area."


def related_items(area: str, items: list[str]) -> list[str]:
    return [item for item in items if mentions_area(str(item), area)]


def area_has_known_defects(area: str, defects: list[dict[str, Any]]) -> bool:
    return any(mentions_area(as_text(defect.get("module")), area) for defect in defects)


def build_evidence_text(
    area: str,
    mr_data: dict[str, Any],
    matching_files: list[str],
    matching_requirements: list[str],
) -> str:
    evidence = [
        area,
        " ".join(matching_files),
        " ".join(matching_requirements),
        as_text(mr_data.get("mr_title")),
        as_text(mr_data.get("mr_description")),
        as_text(mr_data.get("diff_summary")),
        as_text(mr_data.get("acceptance_criteria")),
        as_text(mr_data.get("safety_notes")),
        as_text(mr_data.get("vehicle_platform")),
        as_text(mr_data.get("affected_ecus")),
        as_text(mr_data.get("compliance_tags")),
    ]
    return " ".join(evidence).lower()


def priority_from_score(score: int) -> str:
    if score >= 4:
        return "High"
    if score == 3:
        return "Medium"
    return "Low"


def assess_test_area(
    area: str,
    mr_data: dict[str, Any],
    requirements: list[str],
    defects: list[dict[str, Any]],
) -> TestArea:
    changed_files = mr_data.get("changed_files", []) or []
    affected_ecus = mr_data.get("affected_ecus", []) or []

    matching_files = related_items(area, changed_files)
    matching_requirements = related_items(area, requirements)
    matching_ecus = related_items(area, affected_ecus)
    evidence_text = build_evidence_text(area, mr_data, matching_files, matching_requirements)

    score = 1
    reasons: list[str] = []
    area_lower = area.lower()
    has_defect_history = area_has_known_defects(area, defects)

    if area_lower in SAFETY_RELATED_AREAS or any(topic in area_lower for topic in SAFETY_RELATED_AREAS):
        score += 2
        reasons.append("This touches a safety-related vehicle function.")
    elif matching_requirements:
        score += 1
        reasons.append("This maps directly to a stated vehicle requirement.")

    known_risky_modules = as_text(mr_data.get("known_risky_modules")).lower()
    if mentions_area(known_risky_modules, area):
        score += 1
        reasons.append("The module is already known to be fragile or defect-prone.")

    if has_defect_history:
        score += 2
        reasons.append("Similar past bugs or field issues exist for this module.")

    if any(topic in evidence_text for topic in RISKY_AUTOMOTIVE_TOPICS):
        score += 1
        reasons.append("The change involves automotive timing, diagnostics, network, or integration behavior.")

    if len(matching_files) >= 3:
        score += 1
        reasons.append("Several files changed in this area, so the blast radius is larger.")

    if matching_ecus:
        score += 1
        reasons.append("One or more ECUs/controllers are affected.")

    compliance_text = as_text(mr_data.get("compliance_tags")).lower()
    if any(tag in compliance_text for tag in COMPLIANCE_TAGS_THAT_RAISE_TEST_DEPTH):
        score += 1
        reasons.append("Safety/process compliance tags suggest deeper validation is needed.")

    looks_like_fix = any(word in evidence_text for word in ("fix", "regression", "incident"))
    if looks_like_fix and (has_defect_history or matching_requirements):
        score += 1
        reasons.append("This looks like a fix or regression path, so retesting the old failure mode matters.")

    score = max(1, min(score, 5))

    return TestArea(
        name=area,
        score=score,
        priority=priority_from_score(score),
        reasons=reasons or ["This looks localized and has limited risk based on the supplied data."],
        requirement=first_matching_requirement(area, requirements),
        defect_history=matching_defect_history(area, defects),
        suggested_focus=suggest_test_focus(area, score, mr_data),
    )


def suggest_test_focus(area: str, score: int, mr_data: dict[str, Any]) -> str:
    area_lower = area.lower()
    focus = ["normal vehicle behavior", "negative and fault-injection checks"]

    if any(word in area_lower for word in ("adas", "camera", "radar", "lidar", "perception")):
        focus.append("scenario-based perception validation")
    if any(word in area_lower for word in ("battery", "charging", "thermal", "bms", "powertrain", "torque")):
        focus.append("boundary, thermal, and control-limit cases")
    if any(word in area_lower for word in ("can", "lin", "gateway", "ecu", "network", "diagnostic", "uds", "obd")):
        focus.append("bus communication and diagnostic checks")
    if any(word in area_lower for word in ("cluster", "infotainment", "display", "hmi")):
        focus.append("driver-visible behavior and HMI regression")

    mr_context = " ".join(
        [
            as_text(mr_data.get("diff_summary")),
            as_text(mr_data.get("acceptance_criteria")),
            as_text(mr_data.get("safety_notes")),
        ]
    ).lower()

    if any(word in mr_context for word in ("fallback", "fail-safe", "degradation", "dtc", "diagnostic")):
        focus.append("fail-safe and degraded-mode behavior")
    if score >= 4:
        focus.append("targeted regression based on previous field defects")
    if as_text(mr_data.get("acceptance_criteria")).strip():
        focus.append("requirement traceability checks")

    return ", ".join(dict.fromkeys(focus))


def overall_risk(areas: list[TestArea]) -> tuple[str, str]:
    if not areas:
        return "Low", "No modules or vehicle functions were supplied, so there is not enough risk evidence."

    highest_score = max(area.score for area in areas)
    if highest_score >= 4:
        return "High", "At least one changed area is safety-related, historically fragile, or integration-heavy."
    if highest_score == 3:
        return "Medium", "The MR has moderate vehicle regression risk and should get focused validation."
    return "Low", "The supplied changes look localized and lower risk for the vehicle program."


def best_integration_hint(area_name: str) -> str:
    area_lower = area_name.lower()
    return next(
        (hint for keyword, hint in INTEGRATION_HINTS.items() if keyword in area_lower),
        "vehicle-level behavior",
    )


def build_report(mr_data: dict[str, Any]) -> str:
    requirements = mr_data.get("project_requirements", []) or []
    touched_modules = mr_data.get("modules_touched", []) or []
    defects = mr_data.get("bug_history", []) or []

    assessed_areas = [
        assess_test_area(module, mr_data, requirements, defects)
        for module in touched_modules
    ]
    assessed_areas.sort(key=lambda area: area.score, reverse=True)

    risk_level, risk_reason = overall_risk(assessed_areas)
    vehicle_platform = as_text(mr_data.get("vehicle_platform")) or "Not provided"
    affected_ecus = as_text(mr_data.get("affected_ecus")) or "Not provided"

    lines = [
        "# Automotive MR Test Priority Report",
        "",
        "## Program Context",
        "",
        f"- Vehicle platform: {vehicle_platform}",
        f"- Affected ECUs/controllers: {affected_ecus}",
        "",
        "## Quick Read",
        "",
        f"- Overall risk: {risk_level}",
        f"- Why: {risk_reason}",
        "",
        "## What To Test First",
        "",
        "| Priority | Score | Module/Function | Why It Matters | Requirement Link | Defect History | Suggested Focus |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for area in assessed_areas:
        lines.append(
            f"| {area.priority} | {area.score} | {area.name} | {' '.join(area.reasons)} | "
            f"{area.requirement} | {area.defect_history} | {area.suggested_focus} |"
        )

    lines.extend(["", "## Areas That Deserve Regression Attention", ""])
    high_risk_areas = [area for area in assessed_areas if area.score >= 4]
    if high_risk_areas:
        for area in high_risk_areas:
            lines.append(f"- {area.name}: {area.defect_history}")
    else:
        lines.append("- Nothing crossed the high-regression-risk threshold from the supplied data.")

    lines.extend(["", "## Suggested Test Scenarios", ""])
    if assessed_areas:
        top_area = assessed_areas[0]
        integration_hint = best_integration_hint(top_area.name)
        lines.extend(
            [
                f"- Normal case: Confirm `{top_area.name}` behaves correctly on the target vehicle, bench, or HIL setup.",
                f"- Boundary case: Cover limits, timing windows, state transitions, and recovery behavior around `{top_area.name}`.",
                f"- Fault case: Inject bad signals, missing inputs, timeouts, or relevant DTC/fault conditions.",
                f"- Regression case: Recreate known field issues linked to `{top_area.name}` and nearby controllers.",
                f"- Integration case: Check {integration_hint} across the impacted ECUs, buses, and dependent modules.",
            ]
        )
    else:
        lines.append("- No scenarios were generated because no automotive modules were supplied.")

    lines.extend(["", "## Lower-Priority Areas", ""])
    low_risk_areas = [area for area in assessed_areas if area.score <= 2]
    if low_risk_areas:
        for area in low_risk_areas:
            lines.append(f"- {area.name}: lower risk based on the supplied module, ECU, and defect evidence.")
    else:
        lines.append("- No clearly low-priority areas were identified from the supplied input.")

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an automotive MR test-priority report from requirements and defect history."
    )
    parser.add_argument("input", type=Path, help="JSON file containing MR and vehicle-program details.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional Markdown output path. If omitted, the report is printed to the terminal.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mr_data = read_json(args.input)
    report = build_report(mr_data)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
