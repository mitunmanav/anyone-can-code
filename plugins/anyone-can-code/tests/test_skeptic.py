"""$skeptic — read-only adversarial review (not a $verify replacement).

Codex skills docs: explicit-only via allow_implicit_invocation: false;
display_name in agents/openai.yaml; progressive SKILL.md load.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILLS = PLUGIN_ROOT / "skills"
SKILL_MD = SKILLS / "skeptic" / "SKILL.md"
YAML_PATH = SKILLS / "skeptic" / "agents" / "openai.yaml"
BUDGET = 4000


def load_script(name: str):
    path = PLUGIN_ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"acc_{name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResult:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class ListChangedFilesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skeptic = load_script("skeptic")

    def test_named_paths_win_without_git(self) -> None:
        run = mock.Mock()
        out = self.skeptic.list_changed_files(
            ".",
            named_paths=["a.py", "b/c.py", ""],
            run_command=run,
        )
        self.assertEqual(out, ["a.py", "b/c.py"])
        run.assert_not_called()

    def test_git_status_porcelain_lists_working_tree(self) -> None:
        def fake_run(command, cwd):
            self.assertEqual(command[:2], ["git", "status"])
            return FakeResult(
                stdout=" M plugins/x.py\n?? new.md\nA  staged.py\n"
            )

        out = self.skeptic.list_changed_files(
            "/tmp/repo",
            run_command=fake_run,
        )
        self.assertEqual(out, ["plugins/x.py", "new.md", "staged.py"])

    def test_base_ref_uses_git_diff_name_only(self) -> None:
        calls: list[list[str]] = []

        def fake_run(command, cwd):
            calls.append(list(command))
            return FakeResult(stdout="src/a.py\nsrc/b.py\n")

        out = self.skeptic.list_changed_files(
            "/tmp/repo",
            base="main",
            run_command=fake_run,
        )
        self.assertEqual(out, ["src/a.py", "src/b.py"])
        self.assertTrue(calls)
        self.assertEqual(calls[0][:3], ["git", "diff", "--name-only"])
        self.assertIn("main", calls[0])

    def test_git_failure_returns_empty_list(self) -> None:
        def fake_run(command, cwd):
            return FakeResult(returncode=128, stderr="not a git repo")

        out = self.skeptic.list_changed_files(".", run_command=fake_run)
        self.assertEqual(out, [])

    def test_format_skeptic_md_sections(self) -> None:
        text = self.skeptic.format_skeptic_md(
            scope=["a.py"],
            findings=[
                {
                    "severity": "high",
                    "view": "safety",
                    "file": "a.py",
                    "note": "shell=True",
                }
            ],
            summary="1 high finding",
        )
        self.assertIn("# Skeptic review", text)
        self.assertIn("a.py", text)
        self.assertIn("safety", text)
        self.assertIn("shell=True", text)
        self.assertIn("1 high finding", text)
        self.assertIn("does not replace $verify", text.lower())


class SkepticSkillContractTests(unittest.TestCase):
    def test_skill_files_exist(self) -> None:
        self.assertTrue(SKILL_MD.is_file(), "missing skills/skeptic/SKILL.md")
        self.assertTrue(YAML_PATH.is_file(), "missing agents/openai.yaml")

    def test_frontmatter_name_and_description(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("name: skeptic", text)
        low = text.lower()
        self.assertIn("read-only", low)
        self.assertTrue("diff" in low or "git" in low)
        self.assertIn("correctness", low)
        self.assertIn("safety", low)
        self.assertTrue("honesty" in low or "omission" in low)

    def test_does_not_replace_verify(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8").lower()
        self.assertIn("$verify", text)
        self.assertTrue(
            "does not replace" in text
            or "not a substitute" in text
            or "not replace" in text
            or "ship gate still" in text
        )

    def test_save_only_if_user_asks(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("SKEPTIC.md", text)
        low = text.lower()
        self.assertTrue(
            "only if" in low or "if user asks" in low or "when user asks" in low
        )

    def test_read_only_no_tree_writes(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8").lower()
        self.assertTrue(
            "read-only" in text or "do not edit" in text or "no write" in text
        )
        # Must not claim to implement/fix code
        self.assertNotIn("rewrite the tree", text)

    def test_explicit_only_yaml(self) -> None:
        import yaml

        data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
        self.assertEqual(data["interface"]["display_name"], "ACC skeptic")
        self.assertFalse(data["policy"]["allow_implicit_invocation"])

    def test_inside_token_budget(self) -> None:
        size = len(SKILL_MD.read_text(encoding="utf-8"))
        self.assertLessEqual(size, BUDGET, f"skeptic over budget: {size}")

    def test_mentions_helper_script(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("scripts/skeptic.py", text)


if __name__ == "__main__":
    unittest.main()
