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
import capability_registry
import work_visibility


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

SPECIALIST_FORBIDDEN_ACTIONS = (
    "change-workflow-owner",
    "create-controlling-plan",
    "create-task-tracker",
    "require-commit",
    "add-approval-gate",
    "change-user-style",
    "replace-acc-route",
    "write-workflow-state",
    "offer-visual-companion",
    "open-browser",
    "start-server",
)

TAKEOVER_CONTROL_KEYS = {
    "browser_action",
    "workflow_owner",
    "workflow_state",
    "plan",
    "tracker",
    "commit_required",
    "approval_gate",
    "response_style",
    "route",
    "server_action",
    "visual_companion",
}

RESPONSE_CONTRACT = {
    "visible_text_required": True,
    "next_action_required": True,
    "empty_result_action": "acc-fallback-response",
    "required_fields": ["summary", "next_action"],
}

MEMORY_PREFLIGHT_CONTRACT = {
    "required": True,
    "source": "portable-markdown",
    "script": "scripts/memory_preflight.py",
    "visible_line_required": True,
    "visible_line_prefix": "Relevant memory used:",
    "top_limit": 5,
    "required_before": [
        "ask-question",
        "plan",
        "route-specialist",
        "browser-action",
        "server-action",
        "tool-action",
    ],
    "empty_result_action": "say-none-found-and-continue",
}

COMMAND_GUARD_CONTRACT = {
    "required": True,
    "required_before": [
        "shell-command",
        "package-manager",
        "git-command",
        "browser-action",
        "server-action",
        "tool-action",
    ],
    "cwd_rule": "resolve-repo-root-before-git",
    "failure_policy": "report-failed-command-before-retry",
}

USAGE_CHECKPOINT_CONTRACT = {
    "required": True,
    "source": "reported-primary-usage-percent",
    "required_before": [
        "checkpoint",
        "long-read",
        "large-loop",
        "subagent-work",
        "tool-loop",
        "continue-after-85-percent",
        "continue-after-90-percent",
    ],
}

PATCH_RETRY_CONTRACT = {
    "required": True,
    "required_after": [
        "failed-patch",
        "patch-context-mismatch",
        "stale-edit-target",
    ],
    "required_before": [
        "retry-patch",
        "second-edit-attempt",
    ],
}

MECHANICS_DOCS_GATE_CONTRACT = {
    "required": True,
    "required_before": [
        "platform-mechanics-change",
        "hook-change",
        "plugin-runtime-change",
        "installed-cache-change",
        "windows-launch-change",
        "ui-lifecycle-change",
        "telemetry-or-log-change",
        "mcp-or-tool-plumbing-change",
    ],
    "failure_policy": "write-docs-brief-or-record-controlled-proof-before-code",
}

WORKFLOW_CONTRACT = {
    "workflow_owner": "acc",
    "explicit_handoff_required": True,
    "load_project_context_first": True,
    "specialist_process": "advisory",
    "specialist_may_change_route": False,
    "specialist_may_change_state": False,
    "browser_server_visual_actions": "acc-and-user-permission-only",
}

DEFAULT_GIT_MODE = "auto"
VALID_GIT_MODES = {"auto", "manual"}

SPECIALIST_INTENTS = (
    {
        "requested": "brainstorming",
        "markers": ("brainstorming", "brainstorm"),
        "match_terms": ("brainstorming", "brainstorm", "superpowers"),
    },
    {
        "requested": "product design",
        "markers": ("product design", "product-design"),
        "match_terms": ("product design", "product-design"),
    },
    {
        "requested": "build web apps",
        "markers": ("build web apps", "build-web-apps"),
        "match_terms": ("build web apps", "build-web-apps", "frontend app builder"),
    },
    {
        "requested": "ui skills",
        "markers": ("ui skills", "ui skill", "ui design", "design skills"),
        "match_terms": ("ui", "ui design", "visual design", "product design"),
    },
    {
        "requested": "browser",
        "markers": ("browser", "browser-use"),
        "match_terms": ("browser", "browser-use"),
    },
)


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
    if has_any(
        text,
        ("existing website", "current website", "existing site", "current site"),
    ) and has_any(text, ("improve", "polish", "review", "refine", "perfect")):
        return "polish-review"
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


def requested_specialist_intents(request: str) -> list[dict[str, Any]]:
    request_text = normalize_text(request)
    intents = []
    seen = set()
    for intent in SPECIALIST_INTENTS:
        if has_any(request_text, intent["markers"]) and intent["requested"] not in seen:
            intents.append(intent)
            seen.add(intent["requested"])
    return intents


def capability_matches_intent(capability: dict[str, Any], intent: dict[str, Any]) -> bool:
    provider = normalize_text(capability.get("provider"))
    provider_words = provider.replace("-", " ")
    capability_text = normalize_text(capability.get("capability_text"))
    skills = " ".join(normalize_text(skill) for skill in capability.get("skills", []))
    haystack = normalize_text(" ".join([provider, provider_words, capability_text, skills]))
    for term in intent["match_terms"]:
        term_text = normalize_text(term)
        if term_text and term_text in haystack:
            return True
    return False


def resolve_requested_specialists(
    request: str,
    plugins: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    intents = requested_specialist_intents(request)
    if not intents:
        return []

    registry = capability_registry.build_capability_registry(plugins or [])
    results = []
    for intent in intents:
        candidates = [
            capability
            for capability in registry
            if normalize_text(capability.get("provider")) != "anyone-can-code"
            and capability_matches_intent(capability, intent)
        ]
        candidates.sort(key=lambda item: normalize_text(item.get("provider")))
        if not candidates:
            results.append(
                {
                    "requested": intent["requested"],
                    "matched": False,
                    "plugin": None,
                    "reason": "requested-specialist-unavailable",
                    "fallback": {
                        "owner": "acc",
                        "route": "local-acc",
                        "reason": "requested-specialist-unavailable",
                    },
                    "workflow_owner": "acc",
                    "durable_truth": False,
                }
            )
            continue

        healthy = [
            capability
            for capability in candidates
            if capability["health"]["status"] == "healthy"
        ]
        chosen = healthy[0] if healthy else candidates[0]
        matched = bool(healthy)
        reason = (
            "explicit-request-installed-match"
            if matched
            else "requested-specialist-unhealthy"
        )
        fallback = chosen.get("fallback") or {
            "owner": "acc",
            "route": "local-acc",
            "reason": "capability-unavailable",
        }
        results.append(
            {
                "requested": intent["requested"],
                "matched": matched,
                "plugin": chosen.get("provider"),
                "capability": chosen.get("description")
                or ", ".join(chosen.get("skills", [])),
                "reason": reason,
                "health": chosen.get("health"),
                "capability_source": chosen.get("source"),
                "fallback": fallback,
                "workflow_owner": "acc",
                "durable_truth": False,
            }
        )
    return results


def build_memory_preflight(
    request: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = context or {}
    project_root = str(context.get("project_root") or "").strip()
    preflight = {
        **MEMORY_PREFLIGHT_CONTRACT,
        "query": str(request).strip(),
        "status": "required",
    }
    if project_root:
        preflight["project_root"] = project_root
    return preflight


def context_is_windows(context: dict[str, Any] | None = None) -> bool:
    context = context or {}
    os_hint = normalize_text(context.get("os") or context.get("platform"))
    shell_hint = normalize_text(context.get("shell"))
    if os_hint:
        return "windows" in os_hint or os_hint in {"win32", "nt"}
    if shell_hint:
        return shell_hint in {"powershell", "pwsh", "cmd", "cmd.exe"}
    return os.name == "nt"


def command_shell(context: dict[str, Any] | None = None) -> str:
    context = context or {}
    shell = normalize_text(context.get("shell"))
    if shell in {"powershell", "pwsh"}:
        return "powershell"
    if shell in {"cmd", "cmd.exe"}:
        return "cmd"
    if shell in {"bash", "sh", "zsh", "fish"}:
        return "posix"
    return "powershell" if context_is_windows(context) else "posix"


def build_command_guard(context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    windows = context_is_windows(context)
    shell = command_shell(context)
    guard = {
        **COMMAND_GUARD_CONTRACT,
        "windows": windows,
        "shell": shell,
        "package_runner": "npm.cmd" if windows and shell == "powershell" else "npm",
        "forbidden_patterns": [],
        "git_root_required": True,
    }
    if windows and shell == "powershell":
        guard["forbidden_patterns"] = [
            {
                "pattern": "npm",
                "reason": "PowerShell can resolve npm.ps1 and hit execution policy",
                "replacement": "npm.cmd",
            },
            {
                "pattern": "||",
                "reason": "Bash OR operator is not PowerShell-safe guidance",
                "replacement": 'run commands separately or check $LASTEXITCODE',
            },
        ]
    repo_root = str(context.get("repo_root") or context.get("git_root") or "").strip()
    if repo_root:
        guard["repo_root"] = repo_root
    return guard


def build_usage_checkpoint(context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    current = work_visibility.assess_usage_checkpoint(
        primary_percent=context.get("primary_usage_percent"),
    )
    return {
        **USAGE_CHECKPOINT_CONTRACT,
        "checkpoint_threshold_percent": current["checkpoint_threshold_percent"],
        "split_threshold_percent": current["split_threshold_percent"],
        "stop_threshold_percent": current["stop_threshold_percent"],
        "current": current,
        "failure_policy": "do-not-continue-high-usage-without-checkpoint-or-user-choice",
    }


def build_patch_retry_policy(context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    current = work_visibility.assess_patch_retry(
        failed_attempts=context.get("failed_patch_attempts", 0),
        last_patch_failed=bool(context.get("last_patch_failed", False)),
        exact_target_reread=bool(context.get("exact_target_reread", False)),
    )
    return {
        **PATCH_RETRY_CONTRACT,
        "max_failed_attempts": current["max_failed_attempts"],
        "current": current,
        "failure_policy": "reread-exact-target-before-retrying-patch",
    }


def build_mechanics_docs_gate(
    request: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = context or {}
    current = work_visibility.assess_mechanics_docs_gate(
        request,
        docs_brief=str(
            context.get("mechanics_docs_brief")
            or context.get("docs_brief")
            or ""
        ),
        controlled_proof=bool(context.get("controlled_proof", False)),
        uncertainty=str(
            context.get("mechanics_uncertainty")
            or context.get("uncertainty")
            or ""
        ),
    )
    return {
        **MECHANICS_DOCS_GATE_CONTRACT,
        "current": current,
        "session_traces_policy": "failure-evidence-only-not-platform-authority",
    }


def resolve_git_mode(context: dict[str, Any] | None = None) -> str:
    context = context or {}
    git_mode = normalize_text(context.get("git_mode") or DEFAULT_GIT_MODE)
    return git_mode if git_mode in VALID_GIT_MODES else DEFAULT_GIT_MODE


def session_audit_checklist(
    context: dict[str, Any] | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, bool]:
    context = context or {}
    result = result or {}
    return {
        "active_project_resolved": bool(
            str(
                context.get("repo_root")
                or context.get("git_root")
                or context.get("project_root")
                or ""
            ).strip()
        ),
        "memory_preflighted": bool((result.get("memory_preflight") or {}).get("required")),
        "canonical_state_loaded": bool(
            (result.get("workflow_contract") or {}).get("workflow_owner") == "acc"
        ),
        "git_mode_present": resolve_git_mode(context) in VALID_GIT_MODES,
    }


def uses_plain_npm(command: str) -> bool:
    return bool(re.search(r"(?<![\w.-])npm(?![\w.-])", command))


def uses_git(command: str) -> bool:
    return bool(re.search(r"(^|[\s;&|()])git(?:\.exe)?(?=\s|$)", command))


def assess_command_guidance(
    command: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = context or {}
    command_text = str(command or "")
    guard = build_command_guard(context)
    violations: list[str] = []
    recommended: list[str] = []

    if guard["windows"] and guard["shell"] == "powershell" and uses_plain_npm(command_text):
        violations.append("powershell-npm-ps1")
        recommended.append("Use npm.cmd in PowerShell so npm.ps1 execution policy cannot intercept.")
    if guard["windows"] and guard["shell"] == "powershell" and "||" in command_text:
        violations.append("powershell-bash-or")
        recommended.append(
            "Do not use Bash || in PowerShell; split commands or check $LASTEXITCODE."
        )
    repo_root = str(context.get("repo_root") or context.get("git_root") or "").strip()
    if uses_git(command_text) and not repo_root:
        violations.append("git-root-required")
        recommended.append("Resolve repo root first and run Git from that repo root.")

    cwd = repo_root or str(context.get("project_root") or "").strip()
    return {
        "safe": not violations,
        "violations": violations,
        "recommended": " ".join(recommended),
        "cwd": cwd,
        "command_guard": guard,
    }


def choose_plugin_route(
    request: str,
    plugins: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    request_text = normalize_text(request)
    request_tokens = meaningful_tokens(request_text)
    best: tuple[int, str, dict[str, Any]] | None = None
    unhealthy_match: dict[str, Any] | None = None

    registry = capability_registry.build_capability_registry(plugins or [])
    for capability in registry:
        name = normalize_text(capability.get("provider"))
        if not name or name == "anyone-can-code":
            continue
        capability_text = normalize_text(capability.get("capability_text"))
        overlap = request_tokens & meaningful_tokens(capability_text)
        explicit_name = name in request_text or name.replace("-", " ") in request_text
        skill_match = any(
            normalize_text(skill) in request_text
            for skill in capability.get("skills", [])
            if normalize_text(skill)
        )
        score = len(overlap) + (3 if explicit_name else 0) + (2 if skill_match else 0)
        if score < 2:
            continue
        if capability["health"]["status"] != "healthy":
            unhealthy_match = capability
            continue
        candidate = (score, name, capability)
        if best is None or candidate[:2] > best[:2]:
            best = candidate

    if best is None:
        if unhealthy_match:
            return {
                "matched": False,
                "source": "acc",
                "plugin": unhealthy_match["provider"],
                "capability": unhealthy_match["description"],
                "reason": "capability-unhealthy",
                "health": unhealthy_match["health"],
                "fallback": unhealthy_match["fallback"],
                "workflow_owner": "acc",
                "durable_truth": False,
            }
        return {
            "matched": False,
            "source": "acc",
            "plugin": None,
            "capability": None,
            "reason": "no-confident-plugin-match",
        }

    _, _, capability = best
    return {
        "matched": True,
        "source": "plugin",
        "plugin": capability["provider"],
        "capability": capability.get("description") or ", ".join(capability.get("skills", [])),
        "reason": "installed-manifest-match",
        "health": capability["health"],
        "capability_source": capability["source"],
        "fallback": capability["fallback"],
        "workflow_owner": "acc",
        "durable_truth": False,
    }


def build_specialist_assignment(
    decision: dict[str, Any],
    *,
    request: str,
    allowed_output: str,
    user_handoff: bool = False,
) -> dict[str, Any]:
    specialist = normalize_text(decision.get("plugin"))
    owner = specialist if user_handoff else "acc"
    return {
        "workflow_owner": owner,
        "specialist": specialist,
        "request": str(request).strip(),
        "allowed_output": str(allowed_output).strip(),
        "permissions": (
            ["full-workflow"]
            if user_handoff
            else [
                "read-needed-context",
                "follow-project-preferences",
                "produce-bounded-output",
            ]
        ),
        "forbidden_actions": [] if user_handoff else list(SPECIALIST_FORBIDDEN_ACTIONS),
        "return_to": specialist if user_handoff else "acc",
        "user_handoff": bool(user_handoff),
        "load_project_context_first": not user_handoff,
        "process_authority": "owner" if user_handoff else "advisory",
    }


def contain_workflow_controls(value: Any, path: str = "") -> tuple[Any, list[str]]:
    if isinstance(value, dict):
        cleaned = {}
        blocked = []
        for key, item in value.items():
            key_text = normalize_text(key).replace("-", "_").replace(" ", "_")
            item_path = f"{path}.{key}" if path else str(key)
            if key_text in TAKEOVER_CONTROL_KEYS:
                blocked.append(item_path)
                continue
            cleaned_item, nested_blocked = contain_workflow_controls(item, item_path)
            if not (nested_blocked and cleaned_item in ({}, [])):
                cleaned[key] = cleaned_item
            blocked.extend(nested_blocked)
        return cleaned, blocked
    if isinstance(value, list):
        cleaned = []
        blocked = []
        for index, item in enumerate(value):
            item_path = f"{path}[{index}]" if path else f"[{index}]"
            cleaned_item, nested_blocked = contain_workflow_controls(item, item_path)
            cleaned.append(cleaned_item)
            blocked.extend(nested_blocked)
        return cleaned, blocked
    return value, []


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
            "health": {
                "status": "unhealthy",
                "reason": "plugin-returned-no-result",
            },
            "fallback": decision.get("fallback")
            or {"owner": "acc", "route": "local-acc"},
            "workflow_owner": "acc",
            "durable_truth": False,
        }
    if isinstance(plugin_result, dict) and normalize_text(plugin_result.get("status")) in {
        "failed",
        "unavailable",
        "unhealthy",
    }:
        return {
            "matched": False,
            "source": "acc",
            "plugin": decision.get("plugin"),
            "capability": decision.get("capability"),
            "reason": "capability-runtime-failure",
            "health": {
                "status": "unhealthy",
                "reason": normalize_text(plugin_result.get("reason"))
                or normalize_text(plugin_result.get("status")),
            },
            "fallback": decision.get("fallback")
            or {"owner": "acc", "route": "local-acc"},
            "workflow_owner": "acc",
            "durable_truth": False,
        }
    assignment = decision.get("assignment") or {}
    owner = assignment.get("workflow_owner") or "acc"
    if not isinstance(plugin_result, dict) or assignment.get("user_handoff"):
        return {
            **decision,
            "workflow_owner": owner,
            "result": plugin_result,
            "takeover_blocked": False,
            "blocked_controls": [],
            "blocked_control_paths": [],
        }

    contained_result, blocked_control_paths = contain_workflow_controls(plugin_result)
    blocked_controls = sorted(
        {
            path.split(".", 1)[0]
            for path in blocked_control_paths
        }
    )
    technical_result = contained_result.get("technical_result")
    if technical_result is None:
        technical_result = {
            key: value
            for key, value in contained_result.items()
        }
    return {
        **decision,
        "workflow_owner": "acc",
        "durable_truth": False,
        "result": technical_result,
        "takeover_blocked": bool(blocked_controls),
        "blocked_controls": blocked_controls,
        "blocked_control_paths": blocked_control_paths,
    }


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
        result = {
            "entry_mode": "requirement-change",
            "product_type": "unknown",
            "banner": "Detected: requirement change",
            "route": ["update-plan", "update-state", resume_step],
            "workflow_owner": "acc",
            "workflow_contract": dict(WORKFLOW_CONTRACT),
            "response_contract": dict(RESPONSE_CONTRACT),
            "memory_preflight": build_memory_preflight(request, context),
            "command_guard": build_command_guard(context),
            "usage_checkpoint": build_usage_checkpoint(context),
            "patch_retry": build_patch_retry_policy(context),
            "mechanics_docs_gate": build_mechanics_docs_gate(request, context),
            "bridge": {
                "matched": False,
                "source": "acc",
                "reason": "resume-active-workflow",
            },
        }
        result["session_audit_checklist"] = session_audit_checklist(context, result)
        result["git_mode"] = resolve_git_mode(context)
        return result

    entry_mode = classify_entry_mode(request)
    intake = None
    product_type = product_intake.classify_product_type(request)
    if entry_mode == "idea":
        intake = product_intake.run_product_intake(request, context)
        product_type = intake["product_type"]

    bridge_plugins = plugins if plugins is not None else scan_installed_plugins()
    bridge = choose_plugin_route(request, bridge_plugins)
    requested_specialists = resolve_requested_specialists(request, bridge_plugins)
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
        fallback_route = local_route
        bridge = {
            **bridge,
            "assignment": build_specialist_assignment(
                bridge,
                request=request,
                allowed_output="bounded technical result for the matched capability",
            ),
        }
    result = {
        "entry_mode": entry_mode,
        "product_type": product_type,
        "banner": f"Detected: {detected}",
        "route": active_route,
        "workflow_owner": "acc",
        "workflow_contract": dict(WORKFLOW_CONTRACT),
        "response_contract": dict(RESPONSE_CONTRACT),
        "memory_preflight": build_memory_preflight(request, context),
        "command_guard": build_command_guard(context),
        "usage_checkpoint": build_usage_checkpoint(context),
        "patch_retry": build_patch_retry_policy(context),
        "mechanics_docs_gate": build_mechanics_docs_gate(request, context),
        "bridge": bridge,
        "git_mode": resolve_git_mode(context),
    }
    result["session_audit_checklist"] = session_audit_checklist(context, result)
    if requested_specialists:
        result["requested_specialists"] = requested_specialists
    if fallback_route is not None:
        result["fallback_route"] = fallback_route
    if intake is not None:
        result["intake"] = intake
    return result


def smoke_check() -> tuple[bool, str]:
    idea = route_request("I want to build a website", plugins=[])
    bug = route_request("Fix the login crash", plugins=[])
    specialists = route_request(
        "Use Product Design and brainstorming to improve this existing website",
        plugins=[
            {
                "name": "product-design",
                "description": "Product Design UI prototyping.",
                "skills": ["get-context"],
                "capability_text": "product design ui prototyping",
                "manifest": "plugin.json",
            }
        ],
    )
    if idea["route"] != ["intake", "checklist", "plan"]:
        return False, "idea route mismatch"
    if bug["route"] != ["fix", "verify"]:
        return False, "bug route mismatch"
    specialist_results = {
        item["requested"]: item for item in specialists.get("requested_specialists", [])
    }
    if not specialist_results.get("product design", {}).get("matched"):
        return False, "requested specialist match missing"
    if specialist_results.get("brainstorming", {}).get("reason") != "requested-specialist-unavailable":
        return False, "requested specialist fallback missing"
    if (
        not idea.get("memory_preflight", {}).get("required")
        or idea["memory_preflight"].get("visible_line_prefix") != "Relevant memory used:"
        or "plan" not in idea["memory_preflight"].get("required_before", [])
    ):
        return False, "memory preflight contract missing"
    command_guard = build_command_guard({"os": "windows", "shell": "powershell"})
    if (
        not command_guard.get("required")
        or command_guard.get("package_runner") != "npm.cmd"
        or "git-command" not in command_guard.get("required_before", [])
    ):
        return False, "command guard contract missing"
    high_usage = build_usage_checkpoint({"primary_usage_percent": 90})
    if high_usage["current"]["action"] != "split":
        return False, "usage checkpoint contract missing"
    patch_retry = build_patch_retry_policy(
        {"failed_patch_attempts": 1, "last_patch_failed": True}
    )
    if patch_retry["current"]["action"] != "reread-exact-target":
        return False, "patch retry contract missing"
    mechanics_gate = build_mechanics_docs_gate("Change Codex Desktop hook launch")
    if mechanics_gate["current"]["action"] != "write-docs-brief":
        return False, "mechanics docs gate missing"
    unsafe = assess_command_guidance(
        "npm test || git status",
        {"os": "windows", "shell": "powershell"},
    )
    if not {
        "powershell-npm-ps1",
        "powershell-bash-or",
        "git-root-required",
    }.issubset(set(unsafe["violations"])):
        return False, "command guard smoke mismatch"
    decision = {
        "matched": True,
        "source": "plugin",
        "plugin": "specialist",
        "capability": "bounded help",
        "reason": "smoke",
    }
    assignment = build_specialist_assignment(
        decision,
        request="Improve this project",
        allowed_output="technical recommendations",
    )
    contained = complete_plugin_route(
        {**decision, "assignment": assignment},
        {
            "technical_result": ["useful"],
            "process": {"plan": "replace ACC plan"},
        },
    )
    if (
        contained["workflow_owner"] != "acc"
        or not contained["takeover_blocked"]
        or contained["result"] != ["useful"]
    ):
        return False, "workflow ownership containment mismatch"
    return (
        True,
        "idea -> intake; bug -> fix; capability probe and fallback ready; "
        "requested specialist accounting ready; memory preflight required; "
        "command guard ready; usage checkpoint ready; patch retry ready; "
        "mechanics docs gate ready; ownership containment ready",
    )


def run_front_door(
    request: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Public entry point: route a request and return a result with 'mode' key."""
    result = route_request(request, context)
    result["mode"] = result.get("entry_mode", "idea")
    return result


if __name__ == "__main__":
    request = " ".join(sys.argv[1:]).strip() or "I want to build something"
    print(json.dumps(route_request(request), indent=2))
