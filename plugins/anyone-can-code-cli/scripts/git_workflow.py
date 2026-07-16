#!/usr/bin/env python3
"""ACC-owned git workflow helpers."""

from __future__ import annotations

import json
import re
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any


FAILURE_LIMIT = 2
FAILURE_COUNTS: dict[str, int] = {}
RECEIPT_NAMESPACE = Path(".codex") / "anyone-can-code" / "artifacts" / "receipts"


def today() -> str:
    return time.strftime("%Y%m%d", time.gmtime())


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    return slug or "task"


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )


def repo_root(path: Path | str = ".") -> Path:
    start = Path(path).resolve()
    result = run_command(["git", "rev-parse", "--show-toplevel"], start)
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip()).resolve()
    return start


def main_repo_root(path: Path | str) -> Path:
    resolved = Path(path).resolve()
    parts = resolved.parts
    if ".worktrees" in parts:
        index = parts.index(".worktrees")
        return Path(*parts[:index]).resolve()
    return repo_root(resolved)


def create_worktree(task_slug: str) -> dict[str, Any]:
    root = repo_root(Path.cwd())
    slug = slugify(task_slug)
    dated_slug = f"{slug}-{today()}"
    branch = f"acc/{dated_slug}"
    path = root / ".worktrees" / "acc" / dated_slug

    if check_circuit_breaker("create_worktree")["blocked"]:
        return {"status": "blocked", "path": str(path), "branch": branch}

    result = run_command(["git", "worktree", "add", "-b", branch, str(path)], root)
    if result.returncode != 0:
        record_failure("create_worktree")
        write_git_receipt(
            "create_worktree",
            {"status": "failed", "stderr": result.stderr},
            branch,
            [],
            "",
            repo_root=root,
        )
        return {"status": "failed", "path": str(path), "branch": branch, "stderr": result.stderr}

    clear_failure("create_worktree")
    receipt = write_git_receipt(
        "create_worktree",
        {"status": "created", "path": str(path)},
        branch,
        [],
        "",
        repo_root=root,
    )
    return {"status": "created", "path": str(path), "branch": branch, "receipt": receipt}


def run_tests(path: Path | str) -> dict[str, Any]:
    work_path = Path(path).resolve()
    result = run_command(["python3", "-m", "pytest"], work_path)
    passed = result.returncode == 0
    return {
        "passed": passed,
        "status": "passed" if passed else "failed",
        "command": "python3 -m pytest",
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def conventional_subject(message: str, concern: str) -> str:
    concern_text = slugify(concern).split("-")[0]
    if concern_text not in {"feat", "fix", "chore", "docs", "test", "refactor"}:
        concern_text = "chore"
    subject = str(message or "update workflow").strip()
    if re.match(r"^(feat|fix|chore|docs|test|refactor)(\(.+?\))?:\s+", subject):
        return subject
    return f"{concern_text}: {subject}"


def commit_work(path: Path | str, message: str, concern: str) -> dict[str, Any]:
    work_path = Path(path).resolve()
    test_result = run_tests(work_path)
    if not test_result["passed"]:
        record_failure("commit_work")
        return {"status": "blocked", "reason": "tests-failed", "tests": test_result}

    subject = conventional_subject(message, concern)
    body = (
        "AI context:\n"
        f"- Concern: {concern}\n"
        "- ACC committed only after test gate passed.\n"
        "- Commit intended to remain atomic to one concern.\n"
    )
    add_result = run_command(["git", "add", "-A"], work_path)
    if add_result.returncode != 0:
        record_failure("commit_work")
        return {"status": "failed", "reason": "git-add-failed", "stderr": add_result.stderr}

    commit_result = run_command(["git", "commit", "-m", subject, "-m", body], work_path)
    if commit_result.returncode != 0:
        record_failure("commit_work")
        return {"status": "failed", "reason": "git-commit-failed", "stderr": commit_result.stderr}

    clear_failure("commit_work")
    commit_hash = current_commit(work_path)
    return {"status": "committed", "commit": commit_hash, "subject": subject, "tests": test_result}


def current_commit(path: Path) -> str:
    result = run_command(["git", "rev-parse", "HEAD"], path)
    return result.stdout.strip() if result.returncode == 0 else ""


def merge_to_main(path: Path | str, branch: str) -> dict[str, Any]:
    work_path = Path(path).resolve()
    test_result = run_tests(work_path)
    if not test_result["passed"]:
        record_failure("merge_to_main")
        return {"status": "blocked", "reason": "tests-failed", "tests": test_result}

    root = main_repo_root(work_path)
    checkout = run_command(["git", "checkout", "main"], root)
    if checkout.returncode != 0:
        record_failure("merge_to_main")
        return {"status": "failed", "reason": "checkout-main-failed", "stderr": checkout.stderr}

    merge = run_command(["git", "merge", "--no-ff", branch], root)
    if merge.returncode != 0:
        record_failure("merge_to_main")
        return {"status": "failed", "reason": "merge-failed", "stderr": merge.stderr}

    clear_failure("merge_to_main")
    return {"status": "merged", "branch": branch, "tests": test_result}


def cleanup_worktree(path: Path | str) -> dict[str, Any]:
    work_path = Path(path).resolve()
    if ".worktrees" not in work_path.parts:
        return {"status": "blocked", "reason": "outside-worktrees", "path": str(work_path)}

    root = main_repo_root(work_path)
    try:
        work_path.relative_to(root / ".worktrees")
    except ValueError:
        return {"status": "blocked", "reason": "outside-acc-worktrees", "path": str(work_path)}

    remove = run_command(["git", "worktree", "remove", str(work_path)], root)
    if remove.returncode != 0:
        record_failure("cleanup_worktree")
        return {"status": "failed", "reason": "worktree-remove-failed", "stderr": remove.stderr}

    prune = run_command(["git", "worktree", "prune"], root)
    if prune.returncode != 0:
        record_failure("cleanup_worktree")
        return {"status": "failed", "reason": "worktree-prune-failed", "stderr": prune.stderr}

    clear_failure("cleanup_worktree")
    return {"status": "removed", "path": str(work_path)}


def push_and_create_pr(branch: str, summary: str, receipt: str) -> dict[str, Any]:
    root = repo_root(Path.cwd())
    if check_circuit_breaker("push_and_create_pr")["blocked"]:
        return {"status": "blocked", "reason": "circuit-breaker-open"}

    push = run_command(["git", "push", "-u", "origin", branch], root)
    if push.returncode != 0:
        record_failure("push_and_create_pr")
        return {"status": "failed", "reason": "push-failed", "stderr": push.stderr}

    body = f"{summary}\n\nReceipt: {receipt}\n"
    pr = run_command(
        ["gh", "pr", "create", "--fill", "--body", body],
        root,
    )
    if pr.returncode != 0:
        record_failure("push_and_create_pr")
        return {"status": "failed", "reason": "pr-create-failed", "stderr": pr.stderr}

    clear_failure("push_and_create_pr")
    pr_url = pr.stdout.strip()
    write_git_receipt(
        "push_and_create_pr",
        {"status": "pushed", "summary": summary},
        branch,
        [],
        pr_url,
        repo_root=root,
    )
    return {"status": "pushed", "branch": branch, "pr_url": pr_url}


def write_git_receipt(
    action: str,
    result: Any,
    branch: str,
    commits: list[str],
    pr_url: str,
    *,
    repo_root: Path | None = None,
) -> str:
    root = repo_root or main_repo_root(Path.cwd())
    receipts = root / RECEIPT_NAMESPACE
    receipts.mkdir(parents=True, exist_ok=True)
    path = receipts / f"{int(time.time())}-{slugify(action)}-{uuid.uuid4().hex[:8]}.json"
    payload = {
        "schema_version": 1,
        "action": action,
        "result": result,
        "branch": branch,
        "commits": commits,
        "pr_url": pr_url,
        "written_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(path)


def record_failure(action: str) -> None:
    FAILURE_COUNTS[action] = FAILURE_COUNTS.get(action, 0) + 1


def clear_failure(action: str) -> None:
    FAILURE_COUNTS.pop(action, None)


def check_circuit_breaker(action: str) -> dict[str, Any]:
    failures = FAILURE_COUNTS.get(action, 0)
    return {
        "action": action,
        "failures": failures,
        "limit": FAILURE_LIMIT,
        "blocked": failures >= FAILURE_LIMIT,
    }


def git_workflow_auto(task_slug: str, summary: str) -> dict[str, Any]:
    created = create_worktree(task_slug)
    if created.get("status") != "created":
        return {"status": "failed", "step": "create_worktree", "result": created}

    path = Path(created["path"])
    branch = created["branch"]
    tests = run_tests(path)
    if not tests["passed"]:
        receipt = write_git_receipt("git_workflow_auto", {"status": "blocked", "tests": tests}, branch, [], "")
        return {"status": "blocked", "step": "run_tests", "receipt": receipt}

    commit = commit_work(path, summary, "feat")
    commits = [commit["commit"]] if commit.get("commit") else []
    if commit.get("status") != "committed":
        receipt = write_git_receipt("git_workflow_auto", commit, branch, commits, "")
        return {"status": "failed", "step": "commit_work", "receipt": receipt}

    merge = merge_to_main(path, branch)
    if merge.get("status") != "merged":
        receipt = write_git_receipt("git_workflow_auto", merge, branch, commits, "")
        return {"status": "failed", "step": "merge_to_main", "receipt": receipt}

    cleanup = cleanup_worktree(path)
    receipt = write_git_receipt(
        "git_workflow_auto",
        {"status": "merged", "summary": summary, "cleanup": cleanup},
        branch,
        commits,
        "",
    )
    return {"status": "merged", "branch": branch, "commits": commits, "receipt": receipt}


def check_ci_status(branch: str, path: Path | str = ".") -> dict[str, Any]:
    """Check CI status for a branch using gh CLI."""
    work_path = Path(path).resolve()
    result = run_command(
        ["gh", "run", "list", "--branch", branch, "--limit", "1", "--json", "status,conclusion"],
        work_path,
    )
    if result.returncode != 0:
        return {"status": "unknown", "reason": "gh not found or error: " + (result.stderr or "")[:80]}
    try:
        runs = json.loads(result.stdout)
        if not runs:
            return {"status": "unknown", "reason": "No CI runs found."}
        run = runs[0]
        conclusion = run.get("conclusion") or ""
        status = run.get("status") or ""
        if conclusion == "success":
            return {"status": "passing"}
        if conclusion in {"failure", "cancelled"}:
            return {"status": "failing", "conclusion": conclusion}
        return {"status": "pending", "run_status": status}
    except Exception as exc:
        return {"status": "unknown", "reason": str(exc)}


def full_git_pipeline(path: Path | str, task_slug: str, summary: str) -> dict[str, Any]:
    """Run tests → commit → push → create PR. Return receipt dict with all step results."""
    work_path = Path(path).resolve()
    steps: dict[str, Any] = {}

    test_result = run_tests(work_path)
    steps["tests"] = test_result
    if not test_result["passed"]:
        return {"status": "blocked", "reason": "tests-failed", "steps": steps}

    commit_result = commit_work(work_path, summary, "feat")
    steps["commit"] = commit_result
    if commit_result.get("status") != "committed":
        return {"status": "blocked", "reason": "commit-failed", "steps": steps}

    branch = str(commit_result.get("branch", task_slug))
    pr_result = push_and_create_pr(branch, summary, "")
    steps["pr"] = pr_result

    return {"status": "done", "steps": steps}


def git_workflow_manual(task_slug: str, summary: str) -> dict[str, Any]:
    created = create_worktree(task_slug)
    result = {
        "status": "approval-needed",
        "mode": "manual",
        "summary": summary,
        "approval_needed_before": ["commit", "merge", "push_and_create_pr"],
        "create_worktree": created,
    }
    branch = str(created.get("branch") or "")
    receipt = write_git_receipt("git_workflow_manual", result, branch, [], "")
    result["receipt"] = receipt
    return result


def main() -> int:
    """CLI entry: report auto/manual mode guidance only (no network)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="ACC git workflow helper (local)")
    parser.add_argument("--mode", choices=["auto", "manual"], default="manual")
    parser.add_argument("--task", default="task")
    parser.add_argument("--summary", default="work")
    parser.add_argument("--dry-run", action="store_true", default=True)
    args = parser.parse_args()
    # Dry-run by default: only describe path, never push.
    print(json.dumps({
        "mode": args.mode,
        "task": args.task,
        "summary": args.summary,
        "dry_run": True,
        "note": "User must approve real git actions. No push from this CLI.",
        "auto_entry": "git_workflow_auto" if args.mode == "auto" else "git_workflow_manual",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
