from __future__ import annotations

import datetime
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_DIR = REPO_ROOT / "wiki/00_foundations/covenant"
VSCODE_MIRROR_DIR = REPO_ROOT / ".github/instructions/covenant"
GEMINI_DIR = Path.home() / ".gemini/covenant"
SOPHIA_DIR = Path.home() / ".sophia/covenant"
POINTER_PATH = REPO_ROOT / ".github/instructions/Sophia.instructions.md"
SEED_PATH = CANONICAL_DIR / "INSTRUCTIONS_SEED.md"
CODE_INSTRUCTIONS_PATH = REPO_ROOT / ".github/instructions/Covenant.Code.instructions.md"
DOCS_INSTRUCTIONS_PATH = REPO_ROOT / ".github/instructions/Covenant.Docs.instructions.md"

CODE_SCROLLS = (
    "02_spheres.md",
    "03_verification.md",
    "04_purity_resilience.md",
    "05_maintenance.md",
    "06_harmonia.md",
)
DOCS_SCROLLS = ("01_akaschic_record.md",)


def copy_scrolls(src: Path, destinations: Iterable[Path]) -> None:
    names = sorted(p.name for p in src.glob("*.md"))
    for dest in destinations:
        dest.mkdir(parents=True, exist_ok=True)
    for name in names:
        data = (src / name).read_text(encoding="utf-8")
        for dest in destinations:
            (dest / name).write_text(data, encoding="utf-8")


def build_seed_instructions(seed_text: str, last_verified: str) -> str:
    seed = seed_text.strip()
    return """---
applyTo: '**'
---
# Covenant Seed (mirror)

<!-- Last Verified: {date} -->

{seed}

---

Do not edit here. Update the canonical scrolls instead:
- Canonical source: `wiki/00_foundations/covenant/`
- VS Code mirror: `.github/instructions/covenant/`
- Gemini copy: `~/.gemini/covenant/`
- Sophia home copy: `~/.sophia/covenant/`

Regenerate mirrors and this seed with:
`.venv/bin/python scripts/covenant_scripts/sync_covenant.py`
""".format(date=last_verified, seed=seed)


def build_pointer(last_verified: str) -> str:
    seed_text = SEED_PATH.read_text(encoding="utf-8")
    return build_seed_instructions(seed_text, last_verified)


def build_scroll_bundle(title: str, scrolls: Iterable[Path], apply_to: str, last_verified: str) -> str:
    parts = []
    for scroll in scrolls:
        text = scroll.read_text(encoding="utf-8").strip()
        parts.append(f"\n\n---\n\n{scroll.name}\n\n{text}")
    bundle = "".join(parts).strip()
    return """---
applyTo: '{apply_to}'
---
# {title}

<!-- Last Verified: {date} -->

{bundle}

---

Do not edit here. Update the canonical scrolls instead:
- Canonical source: `wiki/00_foundations/covenant/`
- VS Code mirror: `.github/instructions/covenant/`

Regenerate mirrors and these bundles with:
`.venv/bin/python scripts/covenant_scripts/sync_covenant.py`
""".format(title=title, apply_to=apply_to, date=last_verified, bundle=bundle)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    today = datetime.date.today().isoformat()
    if not CANONICAL_DIR.exists():
        raise SystemExit(f"Canonical covenant directory missing: {CANONICAL_DIR}")
    if not SEED_PATH.exists():
        raise SystemExit(f"Seed instructions missing: {SEED_PATH}")

    copy_scrolls(CANONICAL_DIR, [VSCODE_MIRROR_DIR, GEMINI_DIR, SOPHIA_DIR])
    pointer = build_pointer(today)
    write_text(POINTER_PATH, pointer)

    code_scrolls = [CANONICAL_DIR / name for name in CODE_SCROLLS]
    docs_scrolls = [CANONICAL_DIR / name for name in DOCS_SCROLLS]
    code_bundle = build_scroll_bundle(
        "Covenant Code Scrolls (mirror)",
        code_scrolls,
        "src/**,scripts/**",
        today,
    )
    docs_bundle = build_scroll_bundle(
        "Covenant Docs Scrolls (mirror)",
        docs_scrolls,
        "wiki/**",
        today,
    )
    write_text(CODE_INSTRUCTIONS_PATH, code_bundle)
    write_text(DOCS_INSTRUCTIONS_PATH, docs_bundle)


if __name__ == "__main__":
    main()
