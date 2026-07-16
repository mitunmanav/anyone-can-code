"""NEW items 36–47 (no ACC self-audit)."""
from __future__ import annotations

import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import new_pack as np
import task_coordination as tc
import first_run


def test_mode_knobs_three_modes():
    nt = np.mode_knobs("non-tech")
    mid = np.mode_knobs("middle")
    dev = np.mode_knobs("developer")
    assert nt["plain"] == 3 and nt["teach"] == 3 and nt["tech_shown"] == 0
    assert mid["teach"] == 1
    assert dev["teach"] == 0 and dev["tech_shown"] == 3
    assert np.normalize_mode("builder") == "non-tech"
    assert np.normalize_mode("mixed") == "middle"


def test_teach_off_for_developer():
    assert np.teach_line("plan", "developer") == ""
    assert np.teach_for_request("make a plan", "developer") == []
    lines = np.teach_for_request("make a plan", "non-tech")
    assert lines and "plan" in lines[0].lower()


def test_story_log_plain_life():
    story = np.story_from_receipt({"type": "deploy", "status": "blocked", "needs_user": True})
    assert "wall" in story["life"].lower() or "choice" in story["life"].lower()
    assert story["ask_user"] is True
    assert "yes" in story["approval_plain"].lower() or "no" in story["approval_plain"].lower()


def test_secret_guard_catches_password():
    bad = np.scan_secrets('password = "hunter2xx"\napi_key = "sk-abcdefghijklmnop"')
    assert bad["ok"] is False
    assert bad["hits"]
    good = np.scan_secrets("print('hello')\n")
    assert good["ok"] is True


def test_bad_code_sniff():
    bad = np.sniff_code("os.system('rm -rf /')\nALLOW_PUBLIC_REGISTRATION = true\n")
    assert bad["ok"] is False
    good = np.sniff_code("def add(a, b):\n    return a + b\n")
    assert good["ok"] is True


def test_passive_profile_and_vocab():
    prefs: dict = {}
    prefs = np.update_passive_profile(prefs, signals={"last_user_message": "why is this broken?"})
    assert prefs["passive_profile"].get("wants_teach") is True
    prefs = np.add_vocab(prefs, ["middleware=in-between step", "deploy=put live"])
    assert "middleware=in-between step" in np.vocab_list(prefs)
    out = np.apply_vocab("Add middleware then deploy", prefs)
    assert "in-between" in out.lower()
    assert "put live" in out.lower()


def test_contradiction_guard_db():
    r = np.find_contradictions(["use sqlite", "use postgres"])
    assert r["ok"] is False
    assert r["conflicts"]
    ok = np.find_contradictions(["use sqlite", "keep tests short"])
    assert ok["ok"] is True


def test_plan_lock():
    locked = np.plan_lock_state(plan_approved=True, user_requests_change=False)
    assert locked["locked"] is True
    unlocked = np.plan_lock_state(plan_approved=True, user_requests_change=True)
    assert unlocked["locked"] is False


def test_unclaim_frees_dead_helper(tmp_path):
    tc.set_task_queue(tmp_path, [{"id": "build", "name": "Build", "status": "todo"}])
    claimed = tc.claim_task(tmp_path, "build", owner="helper-a", claim_id="c1")
    assert claimed["task_claims"]["build"]["claim_id"] == "c1"
    # another worker cannot claim
    try:
        tc.claim_task(tmp_path, "build", owner="helper-b", claim_id="c2")
        assert False, "should have raised"
    except tc.TaskCoordinationError:
        pass
    # force unclaim (helper dead, claim id unknown)
    freed = tc.unclaim_task(tmp_path, "build", force=True, reason="helper-dead")
    by_id = {t["id"]: t for t in freed["tasks"]}
    assert by_id["build"]["status"] == "todo"
    assert by_id["build"]["claim_id"] == ""
    assert "build" not in freed.get("task_claims", {})
    # now another can claim
    again = tc.claim_task(tmp_path, "build", owner="helper-b", claim_id="c3")
    assert again["task_claims"]["build"]["owner"] == "helper-b"


def test_unclaim_with_matching_claim_id(tmp_path):
    tc.set_task_queue(tmp_path, [{"id": "x", "name": "X"}])
    tc.claim_task(tmp_path, "x", owner="a", claim_id="cid")
    out = tc.unclaim_task(tmp_path, "x", claim_id="cid")
    assert {t["id"]: t for t in out["tasks"]}["x"]["status"] == "todo"


def test_automations_opt_in_default_off():
    prompt = np.automation_setup_prompt({})
    assert prompt["enabled"] is False
    assert prompt["default"] is False
    prefs = np.set_automations_opt_in({}, False)
    assert prefs["automations_opt_in"] is False
    yes = np.set_automations_opt_in({}, True)
    assert yes["automations_opt_in"] is True


def test_first_run_has_knobs_and_automations_off(tmp_path):
    r = first_run.run_first_run(tmp_path, "non-tech")
    assert r["configured"] is True
    import json

    prefs = json.loads(
        (tmp_path / ".codex/anyone-can-code/settings/preferences.json").read_text(encoding="utf-8")
    )
    assert prefs.get("automations_opt_in") is False
    assert prefs.get("knobs", {}).get("teach") == 3


def test_install_howto_marketplace():
    h = np.install_howto()
    assert "marketplace" in h["user_line"].lower()
    steps = " ".join(h["setup_steps"]).lower()
    assert "paste" in steps or "url" in steps
    assert "$setup" in steps or "setup" in steps


def test_menu_covers_new_ids():
    ids = {f["id"] for f in np.all_features()}
    for need in (
        "modes",
        "teach",
        "story_log",
        "secret_guard",
        "bad_code_sniff",
        "passive_profile",
        "vocabulary",
        "contradiction",
        "plan_lock",
        "automations_opt_in",
        "marketplace_install",
    ):
        assert need in ids
    assert "acc_audits_acc" not in ids
