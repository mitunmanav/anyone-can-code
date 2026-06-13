import json
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import status_model


class StatusModelTests(unittest.TestCase):
    def test_allowed_states_are_closed(self):
        self.assertEqual(
            status_model.ALLOWED_STATES,
            (
                "in scope",
                "designed",
                "approved",
                "implemented",
                "verified",
                "blocked",
                "deferred",
            ),
        )

    def test_render_status_line_uses_exact_states(self):
        line = status_model.render_status_line(
            {"build": "implemented", "tests": "verified", "deploy": "blocked"}
        )
        self.assertEqual(line, "Status: build implemented, tests verified, deploy blocked")

    def test_invalid_state_is_rejected(self):
        with self.assertRaises(ValueError):
            status_model.render_status_line({"build": "done"})

    def test_observability_keeps_failure_and_unverified_truth(self):
        result = status_model.build_observability(
            route="fix -> verify",
            states={"build": "implemented", "tests": "blocked"},
            next_step="Repair test setup.",
            evidence=["Code file exists."],
            failures=["Tests exited 1."],
            silent_failures=["Plugin returned no result."],
            uncertainty=["Windows launch path not checked."],
        )
        self.assertEqual(result["route"], "fix -> verify")
        self.assertEqual(result["status_line"], "Status: build implemented, tests blocked")
        self.assertEqual(result["failures"], ["Tests exited 1."])
        self.assertEqual(result["silent_failures"], ["Plugin returned no result."])
        self.assertEqual(result["unverified"], ["build"])
        self.assertEqual(result["next_step"], "Repair test setup.")

    def test_verified_state_requires_evidence(self):
        with self.assertRaises(ValueError):
            status_model.build_observability(
                route="verify",
                states={"tests": "verified"},
                next_step="Ship.",
            )

    def test_verification_record_has_result_evidence_and_uncertainty(self):
        record = status_model.build_verification_record(
            checked=["Unit tests"],
            passed=["22 tests passed"],
            failed=[],
            evidence=["python -m unittest: OK"],
            uncertainty=["Codex CLI review did not run"],
        )
        self.assertEqual(record["result"], "pass with uncertainty")
        self.assertEqual(record["evidence"], ["python -m unittest: OK"])
        self.assertEqual(record["uncertainty"], ["Codex CLI review did not run"])

    def test_workflow_file_shape_is_explainable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "workflow.json"
            payload = status_model.update_workflow_file(
                path,
                route="plan -> execute -> verify",
                states={"build": "implemented", "tests": "in scope"},
                next_step="Run tests.",
                evidence=["Files changed."],
            )
            saved = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload, saved)
        self.assertEqual(saved["work_state"], "implemented")
        self.assertEqual(saved["verification_state"], "in scope")
        self.assertEqual(saved["unverified"], ["build", "tests"])
        self.assertEqual(saved["next_step"], "Run tests.")


if __name__ == "__main__":
    unittest.main()
