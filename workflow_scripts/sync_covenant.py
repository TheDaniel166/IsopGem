from __future__ import annotations

import datetime
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DIR = REPO_ROOT / "wiki/00_foundations/covenant"
VSCODE_MIRROR_DIR = REPO_ROOT / ".github/instructions/covenant"
GEMINI_DIR = Path.home() / ".gemini/covenant"
SOPHIA_DIR = Path.home() / ".sophia/covenant"
POINTER_PATH = REPO_ROOT / ".github/instructions/Sophia.instructions.md"


def copy_scrolls(src: Path, destinations: Iterable[Path]) -> None:
    names = sorted(p.name for p in src.glob("*.md"))
    for dest in destinations:
        dest.mkdir(parents=True, exist_ok=True)
    for name in names:
        data = (src / name).read_text(encoding="utf-8")
        for dest in destinations:
            (dest / name).write_text(data, encoding="utf-8")


def build_pointer(last_verified: str) -> str:
    return """---
applyTo: '**'
---
# Covenant Pointer (mirror)

<!-- Last Verified: {date} -->

This file is a pointer to the Covenant instructions to avoid token bloat and drift. Do not edit here; update the canonical scrolls instead.

* Canonical source: [wiki/00_foundations/covenant/](wiki/00_foundations/covenant/)
* VS Code mirror: [.github/instructions/covenant/](.github/instructions/covenant/)
* Gemini copy: `~/.gemini/covenant/`
* Sophia home copy: `~/.sophia/covenant/`

Regenerate mirrors and this pointer with `.venv/bin/python workflow_scripts/sync_covenant.py`. Changes made here without updating the canon will be overwritten.
""".format(date=last_verified)


def write_pointer(path: Path, last_verified: str) -> None:
    content = build_pointer(last_verified)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    today = datetime.date.today().isoformat()
    if not CANONICAL_DIR.exists():
        raise SystemExit(f"Canonical covenant directory missing: {CANONICAL_DIR}")

    copy_scrolls(CANONICAL_DIR, [VSCODE_MIRROR_DIR, GEMINI_DIR, SOPHIA_DIR])
    write_pointer(POINTER_PATH, today)


if __name__ == "__main__":
    main()
