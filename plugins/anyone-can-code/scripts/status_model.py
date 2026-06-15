#!/usr/bin/env python3
"""Closed workflow state vocabulary and evidence-first status helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ALLOWED_STATES = (
    "in scope",
    "designed",
    "approved",
    "implemented",
    "verified",
    "blocked",
    "deferred",
)
_ALLOWED_STATE_SET = set(ALLOWED_STATES)

EVIDENCE_LEVELS = (
    "implemented",
    "source_inspected",
    "automated_tests",
    "build_passed",
    "dependency_audit",
    "http_smoke",
    "interaction_tested",
    "visual_qa",
    "user_accepted",
)
_EVIDENCE_LEVEL_SET = set(EVIDENCE_LEVELS)

_EVIDENCE_LABELS = {
    "implemented": "implemented",
    "source_inspected": "source inspected",
    "automated_tests": "automated tests passed",
    "build_passed": "Build passed",
    "dependency_audit": "dependency audit passed",
    "http_smoke": "HTTP smoke passed",
    "interaction_tested": "interactions tested",
    "visual_qa": "visual QA passed",
    "user_accepted": "user accepted",
}

_MISSING_LABELS = {
    "interaction_tested": "interactions unverified",
    "visual_qa": "visual quality unverified",
    "user_accepted": "user acceptance unverified",
}


def _clean_list(values: list[Any] | None) -> list[str]:
    return [str(value).strip() for value in values or [] if str(value).strip()]


def normalize_evidence_levels(levels: list[Any] | None) -> list[str]:
    cleaned = []
    for level in _clean_list(levels):
        clean_level = level.strip().lower().replace("-", "_").replace(" ", "_")
        if clean_level not in _EVIDENCE_LEVEL_SET:
            raise ValueError(f"Invalid evidence level: {level}")
        if clean_level not in cleaned:
            cleaned.append(clean_level)
    return cleaned


def required_levels_for_claim(claim: str) -> list[str]:
    text = str(claim or "").lower()
    required = []
    if any(
        marker in text
        for marker in (
            "work",
            "works",
            "working",
            "function",
            "functions",
            "interactive",
            "toggle",
            "filter",
            "filters",
            "tabs",
            "carousel",
            "menu",
            "form",
            "link",
            "scroll",
        )
    ):
        required.append("interaction_tested")
    if any(
        marker in text
        for marker in (
            "visual",
            "visually",
            "polish",
            "polished",
            "beautiful",
            "demo quality",
            "quality",
        )
    ):
        required.append("visual_qa")
    if any(
        marker in text
        for marker in (
            "perfect",
            "proper",
            "accepted",
            "final",
            "complete",
            "done",
            "ready",
        )
    ):
        required.append("user_accepted")
    return required


def build_safe_claim_wording(
    evidence_levels: list[str],
    missing_levels: list[str],
) -> str:
    passed = [
        _EVIDENCE_LABELS[level]
        for level in evidence_levels
        if level in _EVIDENCE_LABELS and level not in {"user_accepted"}
    ]
    missing = [
        _MISSING_LABELS[level]
        for level in missing_levels
        if level in _MISSING_LABELS
    ]
    parts = []
    if passed:
        parts.append("; ".join(passed) + ".")
    if missing:
        parts.append("; ".join(missing) + ".")
    return " ".join(parts) or "No verification evidence recorded."


def assess_success_claim(
    claim: str,
    evidence_levels: list[Any] | None,
) -> dict[str, Any]:
    clean_levels = normalize_evidence_levels(evidence_levels)
    required = required_levels_for_claim(claim)
    missing = [level for level in required if level not in clean_levels]
    return {
        "claim": str(claim or "").strip(),
        "supported": not missing,
        "required_levels": required,
        "evidence_levels": clean_levels,
        "missing_levels": missing,
        "safe_wording": build_safe_claim_wording(clean_levels, missing),
    }


def validate_states(states: dict[str, str]) -> dict[str, str]:
    cleaned = {}
    for label, state in states.items():
        clean_label = str(label).strip()
        clean_state = str(state).strip().lower()
        if not clean_label:
            raise ValueError("Status label cannot be empty")
        if clean_state not in _ALLOWED_STATE_SET:
            raise ValueError(f"Invalid state for {clean_label}: {state}")
        cleaned[clean_label] = clean_state
    if not cleaned:
        raise ValueError("At least one status state is required")
    return cleaned


def render_status_line(states: dict[str, str]) -> str:
    clean_states = validate_states(states)
    parts = [f"{label} {state}" for label, state in clean_states.items()]
    return f"Status: {', '.join(parts)}"


def build_observability(
    *,
    route: str,
    states: dict[str, str],
    next_step: str,
    evidence: list[Any] | None = None,
    failures: list[Any] | None = None,
    silent_failures: list[Any] | None = None,
    uncertainty: list[Any] | None = None,
) -> dict[str, Any]:
    clean_states = validate_states(states)
    clean_evidence = _clean_list(evidence)
    if "verified" in clean_states.values() and not clean_evidence:
        raise ValueError("Verified state requires evidence")
    return {
        "route": str(route).strip(),
        "states": clean_states,
        "status_line": render_status_line(clean_states),
        "next_step": str(next_step).strip(),
        "evidence": clean_evidence,
        "failures": _clean_list(failures),
        "silent_failures": _clean_list(silent_failures),
        "unverified": [
            label
            for label, state in clean_states.items()
            if state in {"in scope", "designed", "approved", "implemented"}
        ],
        "uncertainty": _clean_list(uncertainty),
    }


def build_verification_record(
    *,
    checked: list[Any],
    passed: list[Any],
    failed: list[Any],
    evidence: list[Any],
    uncertainty: list[Any],
    evidence_levels: list[Any] | None = None,
    claims: list[Any] | None = None,
) -> dict[str, Any]:
    clean_failed = _clean_list(failed)
    clean_uncertainty = _clean_list(uncertainty)
    if clean_failed:
        result = "fail"
    elif clean_uncertainty:
        result = "pass with uncertainty"
    else:
        result = "pass"
    record = {
        "checked": _clean_list(checked),
        "result": result,
        "passed": _clean_list(passed),
        "failed": clean_failed,
        "evidence": _clean_list(evidence),
        "uncertainty": clean_uncertainty,
    }
    clean_levels = normalize_evidence_levels(evidence_levels)
    if clean_levels:
        record["evidence_levels"] = clean_levels
    clean_claims = _clean_list(claims)
    if clean_claims:
        record["claim_assessments"] = [
            assess_success_claim(claim, clean_levels)
            for claim in clean_claims
        ]
    return record


def update_workflow_file(
    path: Path,
    *,
    route: str,
    states: dict[str, str],
    next_step: str,
    evidence: list[Any] | None = None,
    failures: list[Any] | None = None,
    silent_failures: list[Any] | None = None,
    uncertainty: list[Any] | None = None,
) -> dict[str, Any]:
    current = {}
    if path.exists():
        try:
            current = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            current = {}
    observation = build_observability(
        route=route,
        states=states,
        next_step=next_step,
        evidence=evidence,
        failures=failures,
        silent_failures=silent_failures,
        uncertainty=uncertainty,
    )
    current.update(observation)
    current["work_state"] = observation["states"].get("build", "in scope")
    current["verification_state"] = observation["states"].get("tests", "in scope")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    return current


def smoke_check() -> tuple[bool, str]:
    observation = build_observability(
        route="execute -> verify",
        states={"build": "implemented", "tests": "verified", "deploy": "blocked"},
        next_step="Fix deploy blocker.",
        evidence=["22 tests passed."],
        failures=["Deploy credentials missing."],
        silent_failures=["Plugin returned no result; ACC fallback used."],
        uncertainty=["Live deploy not checked."],
    )
    expected = "Status: build implemented, tests verified, deploy blocked"
    if observation["status_line"] != expected:
        return False, observation["status_line"]
    if observation["unverified"] != ["build"]:
        return False, f"bad unverified list: {observation['unverified']}"
    claim = assess_success_claim(
        "Interactive controls work perfectly.",
        ["build_passed", "http_smoke"],
    )
    if claim["supported"] or claim["missing_levels"] != [
        "interaction_tested",
        "user_accepted",
    ]:
        return False, "success claim assessment mismatch"
    return True, expected


if __name__ == "__main__":
    ok, evidence = smoke_check()
    print(evidence)
    raise SystemExit(0 if ok else 1)
