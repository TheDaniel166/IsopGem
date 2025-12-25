from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure() -> None:
    """Ensure `src/` is importable during tests.

    Some tests import modules as `pillars.*` / `shared.*`, which live under
    `<repo>/src`. When pytest runs from the repo root, that directory is not
    automatically on `sys.path`.
    """

    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
collect_ignore = ['_legacy']
