"""Every path a skill mentions must exist after setup or be declared runtime (B7)."""
import re
import tempfile
import unittest
from pathlib import Path
import sys

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
import setup as acc_setup

PATH_RE = re.compile(r"\.codex/anyone-can-code/[A-Za-z0-9_\-./]+")
RUNTIME_FILES = {
    ".codex/anyone-can-code/artifacts/SPEC-DRAFT.md",
    ".codex/anyone-can-code/artifacts/PLAN.md",
    ".codex/anyone-can-code/state/task-queue.md",
    ".codex/anyone-can-code/state/state-current.md",
    ".codex/anyone-can-code/state/receipts/",
    ".codex/anyone-can-code/user-memory/you-brain/",
    ".codex/anyone-can-code/artifacts/SKEPTIC.md",
    ".codex/anyone-can-code/state/checkpoints/",
    ".codex/anyone-can-code/artifacts/BITE_PLAN.md",
}


class SkillPathContract(unittest.TestCase):
    def test_all_skill_paths_are_real(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            acc_setup.ensure_project_layout(root)
            missing = []
            for skill_md in (PLUGIN_ROOT / "skills").rglob("SKILL.md"):
                for ref in PATH_RE.findall(
                        skill_md.read_text(encoding="utf-8")):
                    ref = ref.rstrip(".,)`")
                    if ref in RUNTIME_FILES:
                        continue
                    candidate = root / ref
                    # For directories (ending with /), check if dir exists
                    # For files, check if parent dir exists
                    if ref.endswith("/"):
                        if not candidate.exists():
                            missing.append(f"{skill_md.parent.name}: {ref}")
                    else:
                        if not candidate.parent.exists():
                            missing.append(f"{skill_md.parent.name}: {ref}")
            self.assertEqual(missing, [], "\n".join(missing))


if __name__ == "__main__":
    unittest.main()
