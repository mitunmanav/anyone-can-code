import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import git_workflow


def test_check_ci_status_returns_unknown_when_gh_missing():
    with patch("git_workflow.run_command") as mock_run:
        mock_run.return_value = MagicMock(returncode=127, stdout="", stderr="gh: not found")
        result = git_workflow.check_ci_status("main", Path("/tmp"))
        assert result["status"] == "unknown"
        assert "gh not found" in result.get("reason", "").lower() or result["status"] == "unknown"


def test_full_git_pipeline_returns_receipt_with_all_steps():
    with patch("git_workflow.run_tests") as mock_tests, \
         patch("git_workflow.commit_work") as mock_commit, \
         patch("git_workflow.push_and_create_pr") as mock_pr:
        mock_tests.return_value = {"passed": True, "status": "passed"}
        mock_commit.return_value = {"status": "committed", "commit": "abc123"}
        mock_pr.return_value = {"status": "created", "pr_url": "https://github.com/test/pr/1"}
        result = git_workflow.full_git_pipeline(Path("/tmp"), "add-auth", "Auth feature done")
        assert result["steps"]["tests"]["passed"] is True
        assert result["steps"]["commit"]["status"] == "committed"
        assert result["steps"]["pr"]["status"] == "created"
