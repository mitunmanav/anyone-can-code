"""ACC checkpoints — save/list/restore file list+hash (pattern only, not shadow-git)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import checkpoints  # noqa: E402


def _seed_project(root: Path) -> None:
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("print('v1')\n", encoding="utf-8")
    (root / "README.md").write_text("# demo\n", encoding="utf-8")
    # noise that must never be snapshotted as product files
    (root / ".git").mkdir()
    (root / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (root / "node_modules").mkdir()
    (root / "node_modules" / "x.js").write_text("nope\n", encoding="utf-8")


def test_save_writes_under_state_checkpoints(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    meta = checkpoints.save(tmp_path, label="before-edit")
    assert meta["id"]
    assert meta["label"] == "before-edit"
    assert meta["file_count"] >= 2
    cp_root = tmp_path / ".codex" / "anyone-can-code" / "state" / "checkpoints"
    assert cp_root.is_dir()
    entry = cp_root / meta["id"]
    assert (entry / "meta.json").is_file()
    assert (entry / "files.json").is_file()
    files = json.loads((entry / "files.json").read_text(encoding="utf-8"))
    paths = {f["path"] for f in files}
    assert "src/app.py" in paths
    assert "README.md" in paths
    assert all(f.get("sha256") for f in files)
    # never snapshot VCS or node_modules
    assert not any(p.startswith(".git") for p in paths)
    assert not any("node_modules" in p for p in paths)


def test_list_returns_newest_first(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    a = checkpoints.save(tmp_path, label="a")
    b = checkpoints.save(tmp_path, label="b")
    items = checkpoints.list_checkpoints(tmp_path)
    assert len(items) >= 2
    ids = [i["id"] for i in items]
    assert b["id"] in ids and a["id"] in ids
    # newest first by created_at then id
    assert items[0]["id"] == b["id"]


def test_restore_rewinds_file_content(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    meta = checkpoints.save(tmp_path, label="good")
    app = tmp_path / "src" / "app.py"
    app.write_text("print('broken')\n", encoding="utf-8")
    assert "broken" in app.read_text(encoding="utf-8")
    result = checkpoints.restore(tmp_path, meta["id"])
    assert result["restored"] >= 1
    assert app.read_text(encoding="utf-8") == "print('v1')\n"
    assert "broken" not in app.read_text(encoding="utf-8")


def test_restore_unknown_id_errors(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    try:
        checkpoints.restore(tmp_path, "cp-does-not-exist")
        assert False, "expected CheckpointError"
    except checkpoints.CheckpointError as exc:
        assert "not found" in str(exc).lower() or "unknown" in str(exc).lower()


def test_hash_stable_for_same_bytes(tmp_path: Path) -> None:
    p = tmp_path / "f.txt"
    p.write_text("same\n", encoding="utf-8")
    assert checkpoints.sha256_file(p) == checkpoints.sha256_file(p)
    assert len(checkpoints.sha256_file(p)) == 64


def test_save_skips_checkpoint_store_itself(tmp_path: Path) -> None:
    _seed_project(tmp_path)
    checkpoints.save(tmp_path, label="one")
    meta2 = checkpoints.save(tmp_path, label="two")
    files = json.loads(
        (
            tmp_path
            / ".codex"
            / "anyone-can-code"
            / "state"
            / "checkpoints"
            / meta2["id"]
            / "files.json"
        ).read_text(encoding="utf-8")
    )
    paths = {f["path"] for f in files}
    assert not any(p.startswith(".codex/") for p in paths)


def test_cli_save_list_restore_json(tmp_path: Path, capsys) -> None:
    _seed_project(tmp_path)
    code = checkpoints.main(
        ["--project", str(tmp_path), "save", "--label", "cli", "--json"]
    )
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    cp_id = out["id"]
    (tmp_path / "README.md").write_text("# ruined\n", encoding="utf-8")
    code = checkpoints.main(["--project", str(tmp_path), "list", "--json"])
    assert code == 0
    listed = json.loads(capsys.readouterr().out)
    assert any(item["id"] == cp_id for item in listed)
    code = checkpoints.main(
        ["--project", str(tmp_path), "restore", cp_id, "--json"]
    )
    assert code == 0
    restored = json.loads(capsys.readouterr().out)
    assert restored["restored"] >= 1
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "# demo\n"


def test_skill_frontmatter_and_display_name() -> None:
    skill_md = (PLUGIN / "skills" / "checkpoint" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "name: checkpoint" in skill_md
    assert "restore" in skill_md.lower()
    assert "save" in skill_md.lower()
    assert "list" in skill_md.lower()
    yaml_text = (
        PLUGIN / "skills" / "checkpoint" / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert 'display_name: "ACC checkpoint"' in yaml_text
    assert "allow_implicit_invocation: false" in yaml_text


def test_skill_under_budget() -> None:
    size = len(
        (PLUGIN / "skills" / "checkpoint" / "SKILL.md").read_text(encoding="utf-8")
    )
    assert size <= 4000, f"SKILL.md {size} chars > 4000"
