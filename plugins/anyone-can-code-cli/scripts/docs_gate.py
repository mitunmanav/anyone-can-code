#!/usr/bin/env python3
"""Docs gate: check local docs first, web search when stale. Surface missing requirements."""

from __future__ import annotations

from pathlib import Path
from typing import Any

PLATFORM_MECHANICS_KEYWORDS = (
    "hook", "sessionstart", "pretooluse", "posttooluse", "permissionrequest",
    "plugin runtime", "mcp", "tool plumbing", "codex desktop", "windows launch",
    "ui lifecycle", "telemetry", "installed cache", "subagent", "subagentstart",
)

DOMAIN_REQUIREMENTS = {
    "auth": ["login", "account", "user", "sign in", "signup", "password", "oauth"],
    "payments": ["payment", "stripe", "checkout", "billing", "subscription", "paid"],
    "seo": ["seo", "search engine", "google", "public website", "marketing"],
    "analytics": ["analytics", "tracking", "metrics", "usage", "events"],
    "deploy": ["deploy", "launch", "publish", "host", "production"],
    "db": ["database", "store data", "persist", "save", "postgres", "mysql", "sqlite"],
    "ci": ["ci", "pipeline", "github actions", "automated tests"],
    "performance": ["performance", "fast", "speed", "latency", "load time"],
    "security": ["secure", "security", "csrf", "xss", "sql injection", "vulnerability"],
}


def needs_docs_check(request: str) -> bool:
    lower = request.lower()
    return any(keyword in lower for keyword in PLATFORM_MECHANICS_KEYWORDS)


def build_docs_context(request: str) -> dict[str, Any]:
    lower = request.lower()
    ref_dir = Path(__file__).resolve().parents[1] / "reference"
    local_docs: list[str] = []
    if ref_dir.exists():
        for f in ref_dir.rglob("*.md"):
            if any(keyword in f.name.lower() for keyword in PLATFORM_MECHANICS_KEYWORDS):
                local_docs.append(str(f.relative_to(ref_dir)))

    matched_terms = [k for k in PLATFORM_MECHANICS_KEYWORDS if k in lower]
    search_query = f"Codex plugin {' '.join(matched_terms[:3])} official documentation"

    return {
        "local_docs": local_docs,
        "web_needed": len(local_docs) == 0,
        "search_query": search_query,
        "instruction": "Use WebSearch tool with this query before writing any code.",
    }


def discover_missing_requirements(
    current_checklist: list[str],
    request: str,
) -> list[str]:
    lower = request.lower()
    current_set = {item.lower() for item in current_checklist}
    missing: list[str] = []
    for domain, keywords in DOMAIN_REQUIREMENTS.items():
        if domain not in current_set:
            if any(kw in lower for kw in keywords):
                missing.append(domain)
    return missing
