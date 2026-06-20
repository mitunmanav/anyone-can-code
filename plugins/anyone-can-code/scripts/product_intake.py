#!/usr/bin/env python3
"""
Deterministic product intake helpers for Anyone Can Code.
"""

from __future__ import annotations

from typing import Any

from status_model import ALLOWED_STATES

PRODUCT_TYPES = {
    "website",
    "app",
    "game",
    "api",
    "script",
    "automation",
    "plugin",
    "data tool",
    "dashboard",
    "native app",
    "existing repo",
    "production repo",
    "unknown",
}
ALLOWED_DECISIONS = {"include", "defer", "skip", "unknown"}
QUESTION_ORDER = [
    ("goal", "What should it do?"),
    ("target_user", "Who will use it?"),
    ("must_haves", "What must be included on day one?"),
    ("repo_mode", "Is this a new repo, existing repo, or production repo?"),
    ("deadline", "Any deadline?"),
]


def normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def has_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


def classify_product_type(request: str) -> str:
    text = normalize_text(request)
    if has_any(text, ["production repo", "prod repo", "hotfix production", "production hotfix"]):
        return "production repo"
    if has_any(text, ["website", "landing page", "site", "portfolio"]):
        return "website"
    if has_any(text, ["dashboard", "admin panel", "analytics panel"]):
        return "dashboard"
    if has_any(text, ["native app", "desktop app", "windows app", "mac app"]):
        return "native app"
    if has_any(text, ["mobile app", "web app", "application", " app"]):
        return "app"
    if has_any(text, ["game"]):
        return "game"
    if has_any(text, [" api", "api ", "rest api", "graphql"]):
        return "api"
    if has_any(text, ["script", "cli", "command line"]):
        return "script"
    if has_any(text, ["automation", "automate", "workflow"]):
        return "automation"
    if has_any(text, ["plugin", "extension", "skill"]):
        return "plugin"
    if has_any(text, ["data tool", "csv", "spreadsheet", "reporting tool"]):
        return "data tool"
    if has_any(text, ["existing repo", "current repo", "this repo", "bug fix"]):
        return "existing repo"
    return "unknown"


def infer_repo_mode(request: str, context: dict[str, Any]) -> str:
    explicit = normalize_text(context.get("repo_mode"))
    if explicit in {"new", "existing", "production", "unknown"}:
        return explicit
    text = normalize_text(request)
    if has_any(text, ["production repo", "prod repo"]):
        return "production"
    if has_any(text, ["existing repo", "current repo", "this repo", "bug fix"]):
        return "existing"
    if has_any(text, ["new repo", "from scratch", "new project"]):
        return "new"
    return "unknown"


def infer_deadline(request: str, context: dict[str, Any]) -> str:
    explicit = str(context.get("deadline") or "").strip()
    if explicit:
        return explicit
    text = normalize_text(request)
    for marker in ["today", "tomorrow", "friday", "monday", "this week", "next week"]:
        if marker in text:
            return marker
    return "unknown"


def infer_must_haves(request: str, context: dict[str, Any]) -> list[str]:
    values = context.get("must_haves") or []
    if isinstance(values, str):
        values = [values]
    found = [str(item).strip() for item in values if str(item).strip()]
    text = normalize_text(request)
    feature_map = {
        "login": "login",
        "auth": "login",
        "payment": "payments",
        "seo": "SEO",
        "deploy": "deploy",
        "deployment": "deploy",
        "sales chart": "sales charts",
        "chart": "charts",
        "csv": "CSV import",
    }
    for marker, label in feature_map.items():
        if marker in text and label not in found:
            found.append(label)
    return found


def run_product_intake(initial_request: str, existing_context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = existing_context or {}
    product_type = classify_product_type(initial_request)
    intake = {
        "initial_request": initial_request,
        "product_type": product_type,
        "goal": str(context.get("goal") or "").strip() or "unknown",
        "target_user": str(context.get("target_user") or "").strip() or "unknown",
        "must_haves": infer_must_haves(initial_request, context),
        "repo_mode": infer_repo_mode(initial_request, context),
        "deadline": infer_deadline(initial_request, context),
    }

    questions = []
    for field, text in QUESTION_ORDER:
        value = intake[field]
        if value == "unknown" or value == []:
            questions.append({"field": field, "question": text})
    intake["questions"] = questions[:5]
    return intake


def checklist_item(area: str, decision: str, reason: str) -> dict[str, str]:
    return {"area": area, "decision": decision, "reason": reason, "state": "in scope"}


def decision_from_terms(text: str, include_terms: list[str], defer_terms: list[str] | None = None) -> str:
    defer_terms = defer_terms or []
    if any(
        f"{term} later" in text or f"{term}s later" in text or f"{term} later." in text
        for term in defer_terms + include_terms
    ):
        return "defer"
    if has_any(text, include_terms):
        return "include"
    return "unknown"


def generate_engineering_checklist(intake: dict[str, Any], persona_config: dict[str, Any] | None = None) -> list[dict[str, str]]:
    product_type = intake.get("product_type", "unknown")
    request_text = normalize_text(
        " ".join([str(intake.get("initial_request", "")), str(intake.get("goal", "")), " ".join(intake.get("must_haves", []))])
    )
    must_haves_text = normalize_text(" ".join(intake.get("must_haves", [])))
    text = f"{request_text} {must_haves_text}"

    items = []
    if product_type in {"website", "app", "game", "dashboard", "native app"}:
        items.append(checklist_item("frontend", "include", f"{product_type} needs a user-facing surface"))
        items.append(checklist_item("theme", "unknown", "Visual direction not chosen yet"))
        items.append(checklist_item("responsive", "include", "Builder-facing products should work on common screen sizes"))
        items.append(checklist_item("accessibility", "include", "Basic accessibility prevents avoidable usability failures"))
        items.append(checklist_item("loading states", "include", "User-facing flows need visible progress"))
        items.append(checklist_item("error states", "include", "User-facing flows need recoverable failures"))
    if product_type in {"api", "automation", "plugin", "data tool", "script"}:
        items.append(checklist_item("backend", "include", f"{product_type} needs executable logic"))
    if product_type in {"website", "app", "dashboard", "api"}:
        items.append(checklist_item("backend", "unknown", "Backend need depends on saved data and integrations"))
        items.append(checklist_item("db", "unknown", "Storage need not confirmed"))

    auth_decision = decision_from_terms(text, ["login", "auth", "account"])
    payment_decision = decision_from_terms(text, ["payment", "payments", "checkout", "stripe"])
    seo_decision = "include" if product_type == "website" and has_any(text, ["seo", "marketing", "public"]) else "skip"
    deploy_decision = "include" if has_any(text, ["deploy", "deployment", "publish", "launch"]) else "unknown"

    items.extend(
        [
            checklist_item("auth", auth_decision, "Login is included only when accounts are needed"),
            checklist_item("payments", payment_decision, "Payments stay deferred unless requested for day one"),
            checklist_item("security", "include", "Basic safety is required for generated projects"),
            checklist_item("performance", "include", "Core flows should stay responsive"),
            checklist_item("seo", seo_decision, "SEO matters mainly for public websites"),
            checklist_item("deploy", deploy_decision, "Deployment is included when launch/publish is requested"),
            checklist_item("tests", "include", "Verification target needed before work is called done"),
            checklist_item("docs", "include", "Human-readable handoff stays required"),
        ]
    )

    # Analytics — web-facing products need usage tracking
    if product_type in {"website", "app", "dashboard"}:
        items.append(checklist_item("analytics", "include", "Web products need usage tracking"))

    # CI — every product type needs automated test runs
    items.append(checklist_item("ci", "include", "All products need automated test runs"))

    # Game-specific
    if product_type == "game":
        items.append(checklist_item("game-loop", "include", "Core game loop must be defined before building"))

    # Native app-specific
    if product_type == "native app":
        items.append(checklist_item("platform", "include", "Native apps target specific OS — define platform first"))
        items.append(checklist_item("installer", "include", "Native apps need an installer or package"))

    # Data tool-specific
    if product_type == "data tool":
        items.append(checklist_item("data-pipeline", "include", "Data tools need defined input/output flow"))

    # Script/automation-specific
    if product_type in {"script", "automation"}:
        items.append(checklist_item("error-handling", "include", "Scripts need clear failure modes and exit codes"))
        items.append(checklist_item("logging", "include", "Automation needs audit logs"))

    seen = set()
    deduped = []
    for item in items:
        if item["area"] in seen:
            continue
        seen.add(item["area"])
        deduped.append(item)
    return deduped


def render_plan_line(intake: dict[str, Any], checklist: list[dict[str, str]]) -> str:
    product_type = intake.get("product_type", "unknown")
    included = [item["area"] for item in checklist if item["decision"] == "include"]
    highlights = []
    for area in ["auth", "deploy", "backend", "db", "seo"]:
        if area in included:
            highlights.append(area)
    prefix = " + ".join([product_type] + highlights)
    deferred = [item["area"] for item in checklist if item["decision"] == "defer"]
    if deferred:
        return f"Plan: {prefix}. {', '.join(area.capitalize() for area in deferred)} later."
    return f"Plan: {prefix}."


def smoke_check() -> tuple[bool, str]:
    intake = run_product_intake("I want to build a website with login, deploy, and payments later")
    checklist = generate_engineering_checklist(intake)
    line = render_plan_line(intake, checklist)
    if line != "Plan: website + auth + deploy. Payments later.":
        return False, line
    if len(intake["questions"]) > 5:
        return False, "too many questions"
    return True, line


if __name__ == "__main__":
    ok, evidence = smoke_check()
    print(evidence)
    raise SystemExit(0 if ok else 1)
