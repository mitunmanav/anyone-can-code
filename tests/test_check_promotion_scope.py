import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check-promotion-scope.ps1"


class PromotionScopeGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="acc-promotion-scope-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))
        self.run_git("init")
        self.run_git("config", "user.email", "test@example.com")
        self.run_git("config", "user.name", "ACC Test")
        self.write("README.md", "base\n")
        self.run_git("add", ".")
        self.run_git("commit", "-m", "base")
        self.base = self.git_stdout("rev-parse", "HEAD")

    def run_git(self, *args):
        subprocess.run(["git", *args], cwd=self.tmp, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def git_stdout(self, *args):
        result = subprocess.run(["git", *args], cwd=self.tmp, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()

    def write(self, relative_path, content):
        path = self.tmp / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def commit_candidate(self, files):
        for relative_path, content in files.items():
            self.write(relative_path, content)
        self.run_git("add", ".")
        self.run_git("commit", "-m", "candidate")
        return self.git_stdout("rev-parse", "HEAD")

    def run_guard(self, candidate, policy="reliability"):
        return subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(SCRIPT),
                "-Base",
                self.base,
                "-Candidate",
                candidate,
                "-Policy",
                policy,
            ],
            cwd=self.tmp,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    def test_reliability_policy_allows_only_flow_reliability_and_workflow_docs(self):
        candidate = self.commit_candidate(
            {
                ".flow/specs/fn-2-harden-acc-development-system.md": "spec\n",
                ".flow/tasks/fn-2-harden-acc-development-system.1.md": "task\n",
                "AGENTS.md": "agents\n",
                "DEVELOPMENT-WORKFLOW.md": "workflow\n",
            }
        )

        result = self.run_guard(candidate)

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("PASS", result.stdout)

    def test_reliability_policy_allows_flow_usage_docs(self):
        candidate = self.commit_candidate(
            {
                ".flow/usage.md": "windows flowctl note\n",
            }
        )

        result = self.run_guard(candidate)

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("PASS", result.stdout)

    def test_reliability_policy_blocks_plugin_product_files(self):
        candidate = self.commit_candidate(
            {
                ".flow/specs/fn-2-harden-acc-development-system.md": "spec\n",
                "plugins/anyone-can-code/skills/plan/SKILL.md": "product drift\n",
            }
        )

        result = self.run_guard(candidate)

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("FAIL", result.stdout)
        self.assertIn("plugins/anyone-can-code/skills/plan/SKILL.md", result.stdout)

    def test_development_system_policy_allows_guard_script_tests_and_flow(self):
        candidate = self.commit_candidate(
            {
                ".flow/specs/fn-3-automate-safe-local-promotion.md": "spec\n",
                ".flow/tasks/fn-3-automate-safe-local-promotion.1.md": "task\n",
                "scripts/check-promotion-scope.ps1": "script\n",
                "tests/test_check_promotion_scope.py": "test\n",
                "AGENTS.md": "agents\n",
                "DEVELOPMENT-WORKFLOW.md": "workflow\n",
            }
        )

        result = self.run_guard(candidate, policy="development-system")

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
