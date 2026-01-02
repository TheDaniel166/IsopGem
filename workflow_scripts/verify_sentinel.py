#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import workflow_scripts.sync_covenant as sync_covenant


CANON_DIR = PROJECT_ROOT / "wiki/00_foundations/covenant"
VSCODE_MIRROR_DIR = PROJECT_ROOT / ".github/instructions/covenant"
GEMINI_DIR = Path.home() / ".gemini/covenant"
SOPHIA_DIR = Path.home() / ".sophia/covenant"
POINTER_PATH = PROJECT_ROOT / ".github/instructions/Sophia.instructions.md"


def normalize_text(content: str) -> str:
    """Normalize text for comparison (strip trailing space, drop Last Verified markers)."""
    cleaned = []
    for line in content.splitlines():
        stripped = line.rstrip()
        if stripped.startswith("<!-- Last Verified:") and stripped.endswith("-->"):
            continue
        cleaned.append(stripped)
    return "\n".join(cleaned) + "\n"


def collect_md_files(directory: Path) -> set[str]:
    return {p.name for p in directory.glob("*.md")}


def compare_file(a: Path, b: Path, label_a: str, label_b: str, errors: list[str]) -> None:
    a_text = normalize_text(a.read_text(encoding="utf-8"))
    b_text = normalize_text(b.read_text(encoding="utf-8"))
    if a_text != b_text:
        errors.append(f"Divergence: {label_a} vs {label_b} ({a} vs {b})")


def verify_directory_mirror(src: Path, dest: Path, label: str, errors: list[str]) -> None:
    if not dest.exists():
        errors.append(f"Missing {label} directory: {dest}")
        return

    src_names = collect_md_files(src)
    dest_names = collect_md_files(dest)

    missing = src_names - dest_names
    extra = dest_names - src_names
    if missing:
        errors.append(f"{label} missing files: {sorted(missing)}")
    if extra:
        errors.append(f"{label} has extra files not in canon: {sorted(extra)}")

    for name in sorted(src_names & dest_names):
        compare_file(src / name, dest / name, "canon", label, errors)


def extract_last_verified(content: str) -> str | None:
    m = re.search(r"<!-- Last Verified: ([0-9]{4}-[0-9]{2}-[0-9]{2}) -->", content)
    return m.group(1) if m else None


def verify_pointer(pointer_path: Path, errors: list[str]) -> None:
    if not pointer_path.exists():
        errors.append(f"Missing pointer file: {pointer_path}")
        return

    raw = pointer_path.read_text(encoding="utf-8")
    date = extract_last_verified(raw)
    if not date:
        errors.append("Pointer missing Last Verified stamp")
        return

    expected = sync_covenant.build_pointer(date)
    if normalize_text(raw) != normalize_text(expected):
        errors.append("Pointer content diverges from template; run sync_covenant.py")


def main() -> None:
    errors: list[str] = []

    if not CANON_DIR.exists():
        errors.append(f"Missing canonical covenant directory: {CANON_DIR}")

    if not errors:
        verify_directory_mirror(CANON_DIR, GEMINI_DIR, "Gemini mirror", errors)
        verify_directory_mirror(CANON_DIR, SOPHIA_DIR, "Sophia mirror", errors)
        verify_directory_mirror(CANON_DIR, VSCODE_MIRROR_DIR, "VSCode mirror", errors)
        verify_pointer(POINTER_PATH, errors)

    if errors:
        print("🔴 Covenant divergence detected:")
        for e in errors:
            print(f" - {e}")
        print("\nResolve by running .venv/bin/python workflow_scripts/sync_covenant.py and re-run this sentinel.")
        sys.exit(1)

    print("✅ Covenant harmony: canon, Gemini, VS Code mirror, and pointer are aligned.")
    sys.exit(0)


if __name__ == "__main__":
    main()
