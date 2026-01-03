#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Finding:
    file: str
    line: int
    column: int
    severity: str
    rule: str | None
    message: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_pyright_cmd(repo_root: Path) -> list[str]:
    local = repo_root / ".venv" / "bin" / "pyright"
    if local.exists():
        return [str(local)]
    return ["pyright"]


def _run_pyright(pyright_cmd: list[str], file_path: Path, repo_root: Path) -> dict[str, Any]:
    # Force outputjson for stable parsing.
    result = subprocess.run(
        [*pyright_cmd, str(file_path), "--outputjson"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )

    stdout = result.stdout.strip()
    if not stdout:
        # When pyright fails early, it may emit only stderr.
        raise RuntimeError(result.stderr.strip() or "pyright produced no output")

    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse pyright JSON: {exc}\n--- stdout ---\n{stdout[:2000]}\n--- stderr ---\n{result.stderr[:2000]}")


def _extract_findings(data: dict[str, Any]) -> list[Finding]:
    diags = data.get("generalDiagnostics", [])
    findings: list[Finding] = []

    for d in diags:
        rng = d.get("range") or {}
        start = rng.get("start") or {}
        # Pyright uses 0-based line/character.
        line = int(start.get("line", 0)) + 1
        col = int(start.get("character", 0)) + 1

        findings.append(
            Finding(
                file=str(d.get("file", "")),
                line=line,
                column=col,
                severity=str(d.get("severity", "")),
                rule=d.get("rule"),
                message=str(d.get("message", "")).strip(),
            )
        )

    return findings


def _write_reports(repo_root: Path, target_file: Path, findings: list[Finding]) -> tuple[Path, Path]:
    out_dir = repo_root / "data" / "temp" / "pyright_reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    rel = target_file.resolve().relative_to(repo_root)
    safe_stem = str(rel).replace(os.sep, "__")

    json_path = out_dir / f"{safe_stem}.json"
    txt_path = out_dir / f"{safe_stem}.txt"

    json_path.write_text(
        json.dumps([f.__dict__ for f in findings], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Compact human-readable report.
    lines: list[str] = []
    errors = [f for f in findings if f.severity.lower() == "error"]
    warns = [f for f in findings if f.severity.lower() == "warning"]

    lines.append(f"File: {rel}")
    lines.append(f"Errors: {len(errors)}  Warnings: {len(warns)}  Total: {len(findings)}")
    lines.append("")

    for f in errors[:200]:
        rule = f" [{f.rule}]" if f.rule else ""
        lines.append(f"E {f.line}:{f.column}{rule} {f.message}")

    if len(errors) > 200:
        lines.append(f"... truncated {len(errors) - 200} more errors")

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: pyright_scan_file.py path/to/file.py", file=sys.stderr)
        return 2

    repo_root = _repo_root()
    file_path = Path(argv[1]).resolve()

    if not file_path.exists():
        print(f"File not found: {file_path}", file=sys.stderr)
        return 2

    pyright_cmd = _default_pyright_cmd(repo_root)

    data = _run_pyright(pyright_cmd, file_path, repo_root)
    findings = _extract_findings(data)
    json_path, txt_path = _write_reports(repo_root, file_path, findings)

    # Print a short summary for the task output.
    errors = sum(1 for f in findings if f.severity.lower() == "error")
    warnings = sum(1 for f in findings if f.severity.lower() == "warning")
    rel = file_path.relative_to(repo_root) if file_path.is_relative_to(repo_root) else file_path
    print(f"pyright: {rel}  errors={errors} warnings={warnings}")
    print(f"report: {txt_path}")
    print(f"json:    {json_path}")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
