#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileSummary:
    path: str
    errors: int
    warnings: int


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_pyright_cmd(repo_root: Path) -> list[str]:
    local = repo_root / ".venv" / "bin" / "pyright"
    if local.exists():
        return [str(local)]
    return ["pyright"]


def _count_for_file(pyright_cmd: list[str], file_path: Path, repo_root: Path) -> tuple[int, int]:
    result = subprocess.run(
        [*pyright_cmd, str(file_path), "--outputjson"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    stdout = result.stdout.strip()
    if not stdout:
        # Treat empty output as a failure; surface it as one error.
        return (1, 0)

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return (1, 0)

    diags = data.get("generalDiagnostics", [])
    errors = sum(1 for d in diags if str(d.get("severity", "")).lower() == "error")
    warnings = sum(1 for d in diags if str(d.get("severity", "")).lower() == "warning")
    return (errors, warnings)


def _iter_py_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]

    files: list[Path] = []
    for p in target.rglob("*.py"):
        if p.name == "__init__.py":
            continue
        files.append(p)
    return sorted(files)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Scan a directory of python files with pyright and summarize error counts.")
    parser.add_argument("path", help="Directory (or file) to scan")
    parser.add_argument("--limit", type=int, default=50, help="Max rows to print")
    args = parser.parse_args(argv[1:])

    repo_root = _repo_root()
    target = (repo_root / args.path).resolve() if not os.path.isabs(args.path) else Path(args.path).resolve()

    pyright_cmd = _default_pyright_cmd(repo_root)

    files = _iter_py_files(target)
    if not files:
        print(f"No python files found under: {target}", file=sys.stderr)
        return 2

    summaries: list[FileSummary] = []
    for f in files:
        errors, warnings = _count_for_file(pyright_cmd, f, repo_root)
        rel = f.relative_to(repo_root) if f.is_relative_to(repo_root) else f
        summaries.append(FileSummary(str(rel), errors, warnings))

    # Sort by errors desc, then warnings desc.
    summaries.sort(key=lambda s: (s.errors, s.warnings, s.path), reverse=True)

    total_errors = sum(s.errors for s in summaries)
    total_warnings = sum(s.warnings for s in summaries)

    print(f"Scanned {len(summaries)} files")
    print(f"Total errors: {total_errors}  Total warnings: {total_warnings}")
    print("")

    rows = summaries[: max(args.limit, 0)]
    for s in rows:
        print(f"{s.errors:4d}E {s.warnings:4d}W  {s.path}")

    out_dir = repo_root / "data" / "temp" / "pyright_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "dir_summary.json"
    out_path.write_text(json.dumps([s.__dict__ for s in summaries], indent=2) + "\n", encoding="utf-8")
    print("")
    print(f"Wrote: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
