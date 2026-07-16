"""Repeat-failure detection (audit bug B11)."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "hooks" / "scripts"))
import state as hook_state
import audit
import guard


class RepeatFailure(unittest.TestCase):
    def test_two_failures_trip_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cmd = "wsl.exe -- bash -lc 'python3 x.py'"
            hook_state.record_command_result(root, cmd, 1)
            self.assertFalse(hook_state.repeat_failure(root, cmd))
            hook_state.record_command_result(root, cmd, 1)
            self.assertTrue(hook_state.repeat_failure(root, cmd))

    def test_success_resets_nothing_for_other_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hook_state.record_command_result(root, "a", 1)
            hook_state.record_command_result(root, "b", 0)
            self.assertFalse(hook_state.repeat_failure(root, "a"))

    def test_audit_post_tool_use_wires_real_failures_into_guard(self):
        """Proves audit.py's real PostToolUse handler feeds state, not a direct state.py call."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cmd = "npm run build"
            failing_payload = {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": cmd},
                "tool_response": "Error: build failed with exit status 1",
            }
            # Guard must be silent before two failures observed through audit.py.
            self.assertFalse(hook_state.repeat_failure(root, cmd))
            audit.handle_payload(failing_payload, root)
            self.assertFalse(hook_state.repeat_failure(root, cmd))
            audit.handle_payload(failing_payload, root)
            self.assertTrue(hook_state.repeat_failure(root, cmd))

    def test_plain_error_text_does_not_record_failure(self):
        """Important-3: grep-like output with plain 'error'/'failed'/'exception'
        text must NOT record a failure. Only strong signals (nonzero exit
        code phrase, or a real traceback header) count."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cmd = "grep error log.txt"
            payload = {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": cmd},
                "tool_response": (
                    "log.txt:12: error: connection refused\n"
                    "log.txt:40: failed exception retry"
                ),
            }
            audit.handle_payload(payload, root)
            audit.handle_payload(payload, root)
            self.assertFalse(hook_state.repeat_failure(root, cmd))

    def test_audit_post_tool_use_does_not_record_edit_write(self):
        """Edit/Write have no shell exit code; audit.py must not record them as commands."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = {
                "hook_event_name": "PostToolUse",
                "tool_name": "Edit",
                "tool_input": {"file_path": "x.py"},
                "tool_response": "error: something",
            }
            audit.handle_payload(payload, root)
            audit.handle_payload(payload, root)
            self.assertFalse(hook_state.repeat_failure(root, ""))

    def test_deny_wins_over_repeat_failure_warn(self):
        """A command that failed twice AND matches a hard deny rule must DENY,
        not fall into the advisory repeat-failure warn. Warn must never
        preempt deny (final review issue 1)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cmd = "git reset --hard"
            hook_state.record_command_result(root, cmd, 1)
            hook_state.record_command_result(root, cmd, 1)
            self.assertTrue(hook_state.repeat_failure(root, cmd))

            payload = {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": cmd},
            }
            result = guard.handle_payload(payload, root)
            hook_out = result.get("hookSpecificOutput", {})
            self.assertEqual(
                hook_out.get("permissionDecision"),
                "deny",
                f"expected deny, got: {result}",
            )
            self.assertNotIn("systemMessage", result)

    def test_deny_wins_over_repeat_failure_warn_for_deploy(self):
        """Same as above but for the deploy-deny path (USE_MOCK_DB=true)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cmd = "vercel deploy --prod"
            hook_state.record_command_result(root, cmd, 1)
            hook_state.record_command_result(root, cmd, 1)
            self.assertTrue(hook_state.repeat_failure(root, cmd))

            old_env = os.environ.get("USE_MOCK_DB")
            os.environ["USE_MOCK_DB"] = "true"
            try:
                payload = {
                    "hook_event_name": "PreToolUse",
                    "tool_name": "Bash",
                    "tool_input": {"command": cmd},
                }
                result = guard.handle_payload(payload, root)
            finally:
                if old_env is None:
                    os.environ.pop("USE_MOCK_DB", None)
                else:
                    os.environ["USE_MOCK_DB"] = old_env

            hook_out = result.get("hookSpecificOutput", {})
            self.assertEqual(
                hook_out.get("permissionDecision"),
                "deny",
                f"expected deny, got: {result}",
            )
            self.assertNotIn("systemMessage", result)


    def test_tool_used_signals_do_not_evict_failure_window(self):
        """Minor-8: repeat_failure window must filter to command_result
        signals FIRST, then take the last `window` -- tool_used rows must
        never crowd command_result rows out of the window."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cmd = "npm test"
            hook_state.record_command_result(root, cmd, 1)
            hook_state.record_command_result(root, cmd, 1)
            self.assertTrue(hook_state.repeat_failure(root, cmd))
            # 30 tool_used signals (more than the window size of 20) land
            # AFTER the two failures -- they must not push the failures
            # out of the repeat_failure window.
            for i in range(30):
                hook_state.append_jsonl(
                    hook_state.signal_log_path(root),
                    {
                        "timestamp": hook_state.utc_now(),
                        "signal_type": "tool_used",
                        "detail": f"noise {i}",
                    },
                )
            self.assertTrue(hook_state.repeat_failure(root, cmd))

    def test_signal_ledger_rotates_when_it_grows_past_500_lines(self):
        """Minor-9: unbounded signal ledger growth -- rotate on append once
        the file exceeds 500 lines, keeping the newest rows. (The brief's
        illustrative "~201 lines after 600 appends" undercounts because
        rotation resets to 200 and only 99 of the 600 appends land after
        the single rotation point; asserting a hard bound plus
        newest-survives/oldest-evicted is the behaviorally meaningful
        check, so that's what's asserted here.)"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = hook_state.signal_log_path(root)
            for i in range(600):
                hook_state.append_jsonl(path, {"signal_type": "tool_used", "seq": i})
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertLessEqual(len(lines), 500, "ledger must not grow unbounded")
            seqs = [json.loads(line)["seq"] for line in lines if line.strip()]
            self.assertIn(599, seqs, "newest row must survive rotation")
            self.assertNotIn(0, seqs, "oldest row must be evicted by rotation")


if __name__ == "__main__":
    unittest.main()
