"""Repo map: ranked paths + symbols sample (Aider-inspired, pure Python, no AI)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))
sys.path.insert(0, str(PLUGIN / "hooks" / "scripts"))

import load_session  # noqa: E402
import repo_map  # noqa: E402


def _sample_tree(root: Path) -> None:
    """Tiny multi-file tree for ranking."""
    (root / "pkg").mkdir()
    (root / "pkg" / "core.py").write_text(
        "class Engine:\n"
        "    def run(self):\n"
        "        return Helper.ping()\n"
        "\n"
        "def bootstrap():\n"
        "    return Engine()\n",
        encoding="utf-8",
    )
    (root / "pkg" / "util.py").write_text(
        "class Helper:\n"
        "    @staticmethod\n"
        "    def ping():\n"
        "        return 'ok'\n"
        "\n"
        "def unused_helper():\n"
        "    return 1\n",
        encoding="utf-8",
    )
    (root / "app.js").write_text(
        "export function main() { return bootstrap(); }\n"
        "export class App { start() { return Engine; } }\n",
        encoding="utf-8",
    )
    # noise that must be skipped
    (root / "node_modules").mkdir()
    (root / "node_modules" / "noise.py").write_text(
        "class ShouldSkip:\n    pass\n", encoding="utf-8"
    )
    (root / ".git").mkdir()
    (root / ".git" / "config").write_text("x\n", encoding="utf-8")


def test_scan_skips_junk_and_finds_sources(tmp_path: Path) -> None:
    _sample_tree(tmp_path)
    files = repo_map.list_source_files(tmp_path)
    rels = {p.relative_to(tmp_path).as_posix() for p in files}
    assert "pkg/core.py" in rels
    assert "pkg/util.py" in rels
    assert "app.js" in rels
    assert not any("node_modules" in r for r in rels)
    assert not any(r.startswith(".git") for r in rels)


def test_extract_python_and_js_symbols(tmp_path: Path) -> None:
    _sample_tree(tmp_path)
    py = (tmp_path / "pkg" / "core.py").read_text(encoding="utf-8")
    names = {s.name for s in repo_map.extract_symbols(py, ".py")}
    assert "Engine" in names
    assert "bootstrap" in names
    # methods indented under class are not top-level defs

    js = (tmp_path / "app.js").read_text(encoding="utf-8")
    jnames = {s.name for s in repo_map.extract_symbols(js, ".js")}
    assert "main" in jnames
    assert "App" in jnames


def test_rank_prefers_referenced_symbols(tmp_path: Path) -> None:
    _sample_tree(tmp_path)
    ranked = repo_map.rank_map(tmp_path, max_files=10, max_symbols=6)
    assert ranked, "expected ranked entries"
    # Engine / Helper / bootstrap should appear (cross-file refs)
    blob = json.dumps(ranked)
    assert "Engine" in blob or "Helper" in blob or "bootstrap" in blob
    # paths are relative posix
    assert all("/" not in e["path"] or not e["path"].startswith("/") for e in ranked)
    assert all(not e["path"].startswith("node_modules") for e in ranked)


def test_render_and_write_artifact(tmp_path: Path) -> None:
    _sample_tree(tmp_path)
    text = repo_map.render(tmp_path, max_files=5, max_symbols=4, max_chars=4000)
    assert "Repo map" in text or "repo map" in text.lower()
    assert "pkg/core.py" in text or "core.py" in text
    path = repo_map.write(tmp_path)
    assert path == repo_map.map_path(tmp_path)
    assert path.is_file()
    assert path.read_text(encoding="utf-8")


def test_inject_empty_when_no_file(tmp_path: Path) -> None:
    assert repo_map.inject_snippet(tmp_path) == ""


def test_inject_capped_when_file_exists(tmp_path: Path) -> None:
    _sample_tree(tmp_path)
    repo_map.write(tmp_path, max_files=20, max_symbols=8, max_chars=50_000)
    # Force huge file content beyond inject cap
    path = repo_map.map_path(tmp_path)
    path.write_text("# Repo map\n" + ("x" * 5000) + "\n", encoding="utf-8")
    snippet = repo_map.inject_snippet(tmp_path)
    assert snippet
    assert len(snippet) <= repo_map.INJECT_MAX_CHARS
    assert "Repo map" in snippet or "repo map" in snippet.lower()


def test_load_session_injects_only_when_map_exists(tmp_path: Path) -> None:
    _sample_tree(tmp_path)
    ctx_absent = load_session.build_context(tmp_path, "startup")
    assert "Repo map:" not in ctx_absent

    repo_map.write(tmp_path, max_files=8, max_symbols=4, max_chars=2000)
    ctx = load_session.build_context(tmp_path, "startup")
    assert "Repo map:" in ctx
    # must not dump multi-k map into session
    idx = ctx.index("Repo map:")
    tail = ctx[idx : idx + repo_map.INJECT_MAX_CHARS + 80]
    assert len(tail) <= repo_map.INJECT_MAX_CHARS + 100


def test_load_session_respects_pref_opt_out(tmp_path: Path) -> None:
    import state as _state

    _sample_tree(tmp_path)
    repo_map.write(tmp_path)
    _state.write_preferences(tmp_path, {"repo_map_inject": False})
    ctx = load_session.build_context(tmp_path, "startup")
    assert "Repo map:" not in ctx


def test_cli_build_and_inject(tmp_path: Path, capsys) -> None:
    _sample_tree(tmp_path)
    code = repo_map.main(["--project", str(tmp_path), "build"])
    assert code == 0
    assert repo_map.map_path(tmp_path).is_file()
    code = repo_map.main(["--project", str(tmp_path), "inject"])
    assert code == 0
    out = capsys.readouterr().out
    assert out.strip()
    assert len(out) <= repo_map.INJECT_MAX_CHARS + 20


def test_cli_json_rank(tmp_path: Path, capsys) -> None:
    _sample_tree(tmp_path)
    code = repo_map.main(["--project", str(tmp_path), "rank", "--json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert data and "path" in data[0] and "symbols" in data[0]


def test_skill_packaging() -> None:
    skill = PLUGIN / "skills" / "repo-map"
    assert (skill / "SKILL.md").is_file()
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert "name: repo-map" in text
    assert len(text) <= 4000
    yaml_path = skill / "agents" / "openai.yaml"
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    assert data["interface"]["display_name"] == "ACC repo map"
    assert data.get("policy", {}).get("allow_implicit_invocation") is False


def test_expected_and_explicit_maps() -> None:
    display = (PLUGIN / "tests" / "test_skill_display_names.py").read_text(
        encoding="utf-8"
    )
    discovery = (PLUGIN / "tests" / "test_skill_discovery.py").read_text(
        encoding="utf-8"
    )
    assert '"repo-map": "ACC repo map"' in display
    assert "repo-map" in discovery
    assert 'EXPLICIT_ONLY' in discovery
    assert '"repo-map"' in discovery or "'repo-map'" in discovery
