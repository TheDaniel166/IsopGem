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
