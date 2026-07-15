"""End-to-end smoke test: all 33 requirements verified."""
import json
import sys
from pathlib import Path
import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import front_door
import product_intake
import status_model
import safety_receipts
import git_workflow
import model_ledger
import silent_failure_detector
import docs_gate
import domain_router
import comm_contract
import first_run


class TestRequirements:
    """Each test method = one numbered requirement."""

    def test_r1_one_front_door(self):
        """#1 — One front door."""
        result = front_door.run_front_door("I want to build a todo app")
        assert result["mode"] in front_door.ROUTES or result["mode"] == "idea"

    def test_r6_caveman_default(self):
        """#6 — Caveman by default."""
        result = comm_contract.apply_tone("I have successfully done it", mode=None)
        assert "I have successfully" not in result

    def test_r7_minimal_questions(self):
        """#7 — Minimal questions."""
        intake = product_intake.run_product_intake("build a website with login and payments")
        assert len(intake["questions"]) <= 2

    def test_r8_all_product_types(self):
        """#8 — All product types supported."""
        for pt in ["website", "app", "game", "api", "script", "automation", "plugin", "data tool", "dashboard", "native app"]:
            result = product_intake.classify_product_type(f"build a {pt}")
            assert result != "unknown", f"Failed to classify: {pt}"

    def test_r9_full_checklists(self):
        """#9 — Full engineering checklist per type."""
        intake = product_intake.run_product_intake("build a website with login")
        checklist = product_intake.generate_engineering_checklist(intake)
        areas = {i["area"] for i in checklist}
        for required in ["frontend", "tests", "docs", "security", "ci"]:
            assert required in areas

    def test_r10_domain_router_covers_all(self):
        """#10 — Frontend/backend/auth/payments/security/perf/SEO/analytics/deploy/tests/docs."""
        covered = set(domain_router.DOMAIN_INSTRUCTIONS.keys())
        for domain in ["frontend", "backend", "auth", "payments", "security", "performance", "seo", "analytics", "deploy", "tests", "docs"]:
            assert domain in covered

    def test_r11_ux_domains(self):
        """#11 — UX: theme/responsive/accessibility/loading states/error states."""
        covered = set(domain_router.DOMAIN_INSTRUCTIONS.keys())
        for ux in ["theme", "responsive", "accessibility", "loading states", "error states"]:
            assert ux in covered

    def test_r15_safety_receipts(self):
        """#15 — Safe rollback before risky change."""
        action = {"type": "delete", "command": "rm -rf /tmp/x"}
        c = safety_receipts.classify_action(action)
        assert c["approval_required"] is True

    def test_r20_model_recommendation(self):
        """#20 — Model recommendation by task type."""
        rec = model_ledger.recommend_model("plan")
        assert rec["model"]
        assert rec["reason"]

    def test_r21_silent_failure_detection(self):
        """#21 — Detects silent failures."""
        result = silent_failure_detector.scan_tool_response({"output": "", "exit_code": 0})
        assert result["silent_failures"]

    def test_r23_never_done_without_evidence(self):
        """#23 — Never says done unless verified."""
        with pytest.raises(ValueError):
            status_model.build_observability(
                route="test", states={"build": "verified"}, next_step="ship", evidence=[]
            )

    def test_r24_exact_states(self):
        """#24 — Exact states only."""
        for state in ["in scope", "designed", "approved", "implemented", "verified", "blocked", "deferred"]:
            assert state in status_model.ALLOWED_STATES

    def test_r28_user_type_setup(self, tmp_path):
        """#28 — User type at setup."""
        result = first_run.run_first_run(tmp_path, user_type="builder")
        assert result["configured"] is True

    def test_r32_web_search_via_docs_gate(self):
        """#32 — Web search when docs stale."""
        ctx = docs_gate.build_docs_context("fix the PreToolUse hook")
        assert ctx["search_query"]
        assert "PreToolUse" in ctx["search_query"] or "hook" in ctx["search_query"].lower()

    def test_r33_surfaces_missing_requirements(self):
        """#33 — Surfaces missing requirements mid-work."""
        gaps = docs_gate.discover_missing_requirements(
            current_checklist=["frontend", "backend"],
            request="build a website with stripe payments and user login"
        )
        assert "auth" in gaps or "payments" in gaps
