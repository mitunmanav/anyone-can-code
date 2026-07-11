from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = PLUGIN_ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"acc_{name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


git_workflow = load_script("git_workflow")


class FakeResult:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class Chdir:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.previous = Path.cwd()

    def __enter__(self) -> None:
        os.chdir(self.path)

    def __exit__(self, exc_type, exc, tb) -> None:
        os.chdir(self.previous)


class GitWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        git_workflow.FAILURE_COUNTS.clear()

    def test_create_worktree_uses_acc_worktree_path_and_branch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            calls = []

            def fake_run(command, cwd):
                calls.append((command, Path(cwd)))
                if command[:3] == ["git", "rev-parse", "--show-toplevel"]:
                    return FakeResult(stdout=str(root) + "\n")
                return FakeResult()

            with Chdir(root), mock.patch.object(git_workflow, "today", return_value="20260619"), mock.patch.object(
                git_workflow,
                "run_command",
                side_effect=fake_run,
            ):
                result = git_workflow.create_worktree("Add Login!")

        self.assertEqual(result["status"], "created")
        self.assertEqual(result["branch"], "acc/add-login-20260619")
        self.assertEqual(Path(result["path"]), root / ".worktrees" / "acc" / "add-login-20260619")
        self.assertIn(
            ["git", "worktree", "add", "-b", "acc/add-login-20260619", str(Path(result["path"]))],
            [call[0] for call in calls],
        )

    def test_run_tests_reports_pass_and_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            with mock.patch.object(git_workflow, "run_command", return_value=FakeResult()):
                passed = git_workflow.run_tests(path)
            with mock.patch.object(git_workflow, "run_command", return_value=FakeResult(returncode=1, stderr="fail")):
                failed = git_workflow.run_tests(path)

        self.assertTrue(passed["passed"])
        self.assertFalse(failed["passed"])
        self.assertEqual(failed["status"], "failed")

    def test_commit_work_blocks_when_tests_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(
            git_workflow,
            "run_tests",
            return_value={"passed": False, "status": "failed"},
        ):
            result = git_workflow.commit_work(temp_dir, "implement thing", "feat")

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "tests-failed")
        self.assertEqual(git_workflow.FAILURE_COUNTS["commit_work"], 1)

    def test_commit_work_makes_conventional_commit_with_ai_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            calls = []

            def fake_run(command, cwd):
                calls.append(command)
                if command == ["git", "rev-parse", "HEAD"]:
                    return FakeResult(stdout="abc123\n")
                return FakeResult()

            with mock.patch.object(git_workflow, "run_tests", return_value={"passed": True}), mock.patch.object(
                git_workflow,
                "run_command",
                side_effect=fake_run,
            ):
                result = git_workflow.commit_work(temp_dir, "add workflow", "feature")

        commit_calls = [call for call in calls if call[:2] == ["git", "commit"]]
        self.assertEqual(result["status"], "committed")
        self.assertEqual(result["subject"], "chore: add workflow")
        self.assertEqual(result["commit"], "abc123")
        self.assertIn("-m", commit_calls[0])
        self.assertTrue(any("AI context:" in item for item in commit_calls[0]))

    def test_merge_to_main_tests_before_checkout_and_merge(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            worktree = Path(temp_dir) / ".worktrees" / "acc" / "task-20260619"
            worktree.mkdir(parents=True)
            calls = []

            def fake_run(command, cwd):
                calls.append(command)
                return FakeResult()

            with mock.patch.object(git_workflow, "run_tests", return_value={"passed": True}), mock.patch.object(
                git_workflow,
                "run_command",
                side_effect=fake_run,
            ):
                result = git_workflow.merge_to_main(worktree, "acc/task-20260619")

        self.assertEqual(result["status"], "merged")
        self.assertEqual(calls, [["git", "checkout", "main"], ["git", "merge", "--no-ff", "acc/task-20260619"]])

    def test_cleanup_worktree_blocks_paths_outside_worktrees(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = git_workflow.cleanup_worktree(Path(temp_dir) / "repo")

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "outside-worktrees")

    def test_receipt_written_and_circuit_breaker_blocks_after_two_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            receipt = git_workflow.write_git_receipt(
                "merge_to_main",
                {"status": "merged"},
                "acc/task",
                ["abc123"],
                "",
                repo_root=root,
            )
            git_workflow.record_failure("merge_to_main")
            git_workflow.record_failure("merge_to_main")
            breaker = git_workflow.check_circuit_breaker("merge_to_main")
            payload = json.loads(Path(receipt).read_text(encoding="utf-8"))

        self.assertEqual(payload["action"], "merge_to_main")
        self.assertEqual(payload["commits"], ["abc123"])
        self.assertTrue(breaker["blocked"])


if __name__ == "__main__":
    unittest.main()
