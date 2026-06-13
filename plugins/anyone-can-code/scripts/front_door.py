#!/usr/bin/env python3
"""Deterministic front-door routing and installed-plugin discovery for ACC."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import product_intake


ROUTES = {
    "idea": ["intake", "checklist", "plan"],
    "written-spec": ["plan", "execute", "verify"],
    "existing-repo": ["onboard", "plan", "execute", "verify"],
    "feature-request": ["plan", "execute", "verify"],
    "bug-fix": ["fix", "verify"],
    "polish-review": ["review", "polish", "verify"],
    "ship-verify": ["verify"],
}

STOP_WORDS = {
    "a",
    "an",
    "and",
    "add",
    "for",
    "from",
    "in",
    "it",
    "my",
    "of",
    "on",
    "please",
    "the",
    "this",
    "to",
    "use",
    "with",
    "build",
    "change",
    "code",
    "create",
    "execute",
    "existing",
    "fix",
    "implement",
    "plan",
    "project",
    "repo",
    "repository",
    "review",
    "route",
    "task",
    "test",
    "verify",
    "workflow",
}


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def has_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def classify_entry_mode(request: str) -> str:
    text = normalize_text(request)
    if has_any(text, ("verify", "ship", "release", "ready to publish", "ready to deploy")):
        return "ship-verify"
    if has_any(text, ("bug", "broken", "crash", "error", "failure", "fails", "fix ")):
        return "bug-fix"
    if has_any(text, ("polish", "review the ux", "review this", "improve the design", "refine")):
        return "polish-review"
    if has_any(text, ("spec.md", "written spec", "requirements file", "requirements in", "prd")):
        return "written-spec"
    if has_any(text, ("add ", "implement ", "feature", "support ", "change ")):
        return "feature-request"
    if has_any(text, ("existing repo", "current repo", "this repo", "codebase", "repository")):
        return "existing-repo"
    return "idea"


def codex_cache_root() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    return codex_home / "plugins" / "cache"


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def frontmatter_value(path: Path, key: str) -> str:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return ""
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return ""
    key_match = re.search(
        rf"^{re.escape(key)}:\s*(.+?)\s*$",
        match.group(1),
        re.MULTILINE,
    )
    if not key_match:
        return ""
    return key_match.group(1).strip().strip("\"'")


def resolve_skills_root(plugin_root: Path, manifest: dict[str, Any]) -> Path | None:
    value = manifest.get("skills")
    if not isinstance(value, str) or not value.strip():
        return None
    root = (plugin_root / value).resolve()
    try:
        root.relative_to(plugin_root.resolve())
    except ValueError:
        return None
    return root if root.is_dir() else None


def scan_installed_plugins(cache_root: Path | None = None) -> list[dict[str, Any]]:
    root = cache_root or codex_cache_root()
    if not root.is_dir():
        return []

    plugins = []
    for manifest_path in sorted(root.glob("*/*/*/.codex-plugin/plugin.json")):
        manifest = read_json(manifest_path)
        if not manifest:
            continue
        name = normalize_text(manifest.get("name"))
        if not name:
            continue

        plugin_root = manifest_path.parent.parent
        description = str(manifest.get("description") or "").strip()
        interface = manifest.get("interface") if isinstance(manifest.get("interface"), dict) else {}
        interface_text = " ".join(
            str(interface.get(key) or "")
            for key in ("displayName", "shortDescription", "longDescription")
        )
        skill_names = []
        skill_descriptions = []
        skills_root = resolve_skills_root(plugin_root, manifest)
        if skills_root:
            for skill_file in sorted(skills_root.glob("*/SKILL.md")):
                skill_name = frontmatter_value(skill_file, "name") or skill_file.parent.name
                skill_description = frontmatter_value(skill_file, "description")
                skill_names.append(skill_name)
                if skill_description:
                    skill_descriptions.append(skill_description)

        capability_text = normalize_text(
            " ".join([name, description, interface_text, *skill_names, *skill_descriptions])
        )
        plugins.append(
            {
                "name": name,
                "description": description,
                "skills": skill_names,
                "capability_text": capability_text,
                "manifest": str(manifest_path),
            }
        )
    return plugins


def meaningful_tokens(value: str) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9]+", normalize_text(value)))
    return {token for token in tokens if len(token) > 2 and token not in STOP_WORDS}


def choose_plugin_route(
    request: str,
    plugins: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    request_text = normalize_text(request)
    request_tokens = meaningful_tokens(request_text)
    best: tuple[int, str, dict[str, Any]] | None = None

    for plugin in plugins or []:
        name = normalize_text(plugin.get("name"))
        if not name or name == "anyone-can-code":
            continue
        capability_text = normalize_text(plugin.get("capability_text"))
        overlap = request_tokens & meaningful_tokens(capability_text)
        explicit_name = name in request_text or name.replace("-", " ") in request_text
        skill_match = any(
            normalize_text(skill) in request_text
            for skill in plugin.get("skills", [])
            if normalize_text(skill)
        )
        score = len(overlap) + (3 if explicit_name else 0) + (2 if skill_match else 0)
        if score < 2:
            continue
        candidate = (score, name, plugin)
        if best is None or candidate[:2] > best[:2]:
            best = candidate

    if best is None:
        return {
            "matched": False,
            "source": "acc",
            "plugin": None,
            "capability": None,
            "reason": "no-confident-plugin-match",
        }

    _, _, plugin = best
    return {
        "matched": True,
        "source": "plugin",
        "plugin": plugin["name"],
        "capability": plugin.get("description") or ", ".join(plugin.get("skills", [])),
        "reason": "installed-manifest-match",
    }


def complete_plugin_route(
    decision: dict[str, Any],
    plugin_result: Any,
) -> dict[str, Any]:
    if not decision.get("matched"):
        return decision
    if plugin_result is None or plugin_result is False or plugin_result == "":
        return {
            "matched": False,
            "source": "acc",
            "plugin": decision.get("plugin"),
            "capability": decision.get("capability"),
            "reason": "plugin-returned-no-result",
        }
    return {**decision, "result": plugin_result}


def route_request(
    request: str,
    context: dict[str, Any] | None = None,
    plugins: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    context = context or {}
    text = normalize_text(request)
    if context.get("workflow_active") and has_any(
        text,
        ("actually", "instead", "change", "new requirement", "also add", "remove "),
    ):
        resume_step = normalize_text(context.get("resume_step")) or "resume"
        return {
            "entry_mode": "requirement-change",
            "product_type": "unknown",
            "banner": "Detected: requirement change",
            "route": ["update-plan", "update-state", resume_step],
            "bridge": {
                "matched": False,
                "source": "acc",
                "reason": "resume-active-workflow",
            },
        }

    entry_mode = classify_entry_mode(request)
    intake = None
    product_type = product_intake.classify_product_type(request)
    if entry_mode == "idea":
        intake = product_intake.run_product_intake(request, context)
        product_type = intake["product_type"]

    bridge_plugins = plugins if plugins is not None else scan_installed_plugins()
    bridge = choose_plugin_route(request, bridge_plugins)
    detected = entry_mode
    if entry_mode == "feature-request" and product_type == "existing repo":
        detected = "existing repo + feature request"
    if product_type != "unknown":
        if detected == entry_mode:
            detected = f"{entry_mode} + {product_type}"

    local_route = list(ROUTES[entry_mode])
    active_route = local_route
    fallback_route = None
    if bridge.get("matched"):
        active_route = [f"plugin:{bridge['plugin']}"]
        fallback_route = local_route
    result = {
        "entry_mode": entry_mode,
        "product_type": product_type,
        "banner": f"Detected: {detected}",
        "route": active_route,
        "bridge": bridge,
    }
    if fallback_route is not None:
        result["fallback_route"] = fallback_route
    if intake is not None:
        result["intake"] = intake
    return result


def smoke_check() -> tuple[bool, str]:
    idea = route_request("I want to build a website", plugins=[])
    bug = route_request("Fix the login crash", plugins=[])
    if idea["route"] != ["intake", "checklist", "plan"]:
        return False, "idea route mismatch"
    if bug["route"] != ["fix", "verify"]:
        return False, "bug route mismatch"
    return True, "idea -> intake; bug -> fix; plugin fallback ready"


if __name__ == "__main__":
    request = " ".join(sys.argv[1:]).strip() or "I want to build something"
    print(json.dumps(route_request(request), indent=2))
