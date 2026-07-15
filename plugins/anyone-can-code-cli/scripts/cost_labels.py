#!/usr/bin/env python3
"""Item 17: cost labels on suggestions — [CHEAP] vs [HUNGRY]."""

from __future__ import annotations

from typing import Any


def label(kind: str) -> str:
    k = (kind or "").strip().lower()
    if k in {"cheap", "free", "local", "hook", "0"}:
        return "[CHEAP]"
    if k in {"hungry", "ai", "subagent", "deep", "cloud", "audit"}:
        return "[HUNGRY]"
    return "[CHEAP]" if k else "[CHEAP]"


def tag_line(text: str, kind: str) -> str:
    """Prefix a suggestion with its cost tag."""
    tag = label(kind)
    body = (text or "").strip()
    if body.startswith("[CHEAP]") or body.startswith("[HUNGRY]"):
        return body
    return f"{tag} {body}"


def annotate_suggestion(item: dict[str, Any]) -> dict[str, Any]:
    """Return a copy with cost_label filled."""
    out = dict(item)
    kind = str(out.get("cost") or out.get("token") or "cheap")
    out["cost_label"] = label(kind)
    if "text" in out:
        out["text"] = tag_line(str(out["text"]), kind)
    return out


def format_menu(items: list[dict[str, Any]]) -> str:
    lines = []
    for item in items:
        tagged = annotate_suggestion(item)
        lines.append(tagged.get("text") or f"{tagged['cost_label']} {tagged.get('name', '')}")
    return "\n".join(lines)
