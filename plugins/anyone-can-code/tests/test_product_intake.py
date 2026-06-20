from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = PLUGIN_ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"acc_{name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


product_intake = load_script("product_intake")
doctor = load_script("doctor")


class ProductIntakeTests(unittest.TestCase):
    def test_vague_website_request_asks_only_missing_blocking_questions(self) -> None:
        intake = product_intake.run_product_intake("I want to build a website")

        self.assertEqual(intake["product_type"], "website")
        self.assertLessEqual(len(intake["questions"]), 5)
        self.assertEqual(
            [question["field"] for question in intake["questions"]],
            ["goal", "target_user", "must_haves", "repo_mode", "deadline"],
        )
        self.assertEqual(intake["repo_mode"], "unknown")

    def test_intake_skips_answers_already_supplied_by_context(self) -> None:
        intake = product_intake.run_product_intake(
            "Build a dashboard for store owners with sales charts in an existing repo by Friday",
            {"must_haves": ["sales charts"], "repo_mode": "existing"},
        )

        self.assertEqual(intake["product_type"], "dashboard")
        self.assertEqual(intake["repo_mode"], "existing")
        self.assertIn("sales charts", intake["must_haves"])
        self.assertNotIn("must_haves", [question["field"] for question in intake["questions"]])
        self.assertNotIn("repo_mode", [question["field"] for question in intake["questions"]])

    def test_classifier_covers_required_product_types_and_repo_modes(self) -> None:
        cases = {
            "marketing website": "website",
            "mobile app": "app",
            "browser game": "game",
            "REST API": "api",
            "cleanup script": "script",
            "email automation": "automation",
            "Codex plugin": "plugin",
            "CSV data tool": "data tool",
            "analytics dashboard": "dashboard",
            "Windows desktop native app": "native app",
            "existing repo bug fix": "existing repo",
            "production repo hotfix": "production repo",
            "something unusual": "unknown",
        }

        for request, expected in cases.items():
            with self.subTest(request=request):
                self.assertEqual(product_intake.classify_product_type(request), expected)

    def test_checklist_adapts_and_marks_decisions(self) -> None:
        intake = product_intake.run_product_intake(
            "I want to build a website with login, SEO, deploy, and payments later"
        )
        checklist = product_intake.generate_engineering_checklist(intake)
        by_area = {item["area"]: item for item in checklist}

        self.assertEqual(by_area["frontend"]["decision"], "include")
        self.assertEqual(by_area["auth"]["decision"], "include")
        self.assertEqual(by_area["seo"]["decision"], "include")
        self.assertEqual(by_area["deploy"]["decision"], "include")
        self.assertEqual(by_area["payments"]["decision"], "defer")
        self.assertEqual(by_area["theme"]["decision"], "unknown")
        self.assertEqual(by_area["responsive"]["decision"], "include")
        self.assertEqual(by_area["loading states"]["decision"], "include")
        self.assertLess(len(checklist), 22)
        self.assertTrue({item["decision"] for item in checklist} <= product_intake.ALLOWED_DECISIONS)

    def test_plan_line_is_concise_builder_readable(self) -> None:
        intake = product_intake.run_product_intake(
            "I want to build a website with login, deployment, and payments later"
        )
        checklist = product_intake.generate_engineering_checklist(intake)

        self.assertEqual(
            product_intake.render_plan_line(intake, checklist),
            "Plan: website + auth + deploy. Payments later.",
        )

    def test_doctor_reports_product_intake_smoke_check(self) -> None:
        report = doctor.Doctor(json_mode=True).run_all()
        by_check = {item["check"]: item for item in report["results"]}

        self.assertEqual(by_check["product_intake_smoke"]["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
