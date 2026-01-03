#!/usr/bin/env python3
"""
The Rite of Purification - Automated Vicinity Sweep

Runs static analysis tools to detect entropy in Python files:
- pyflakes: Unused imports/variables
- isort: Import ordering
- pyright: Type checking  
- vulture: Dead code detection

Usage:
    python3 scripts/purify_vicinity.py [file1.py] [file2.py] ...
    python3 scripts/purify_vicinity.py --all  # Scan all src/
"""
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
VENV_BIN = PROJECT_ROOT / ".venv" / "bin"


def get_tool_path(name: str) -> str:
    """Get the path to a tool, preferring venv installation."""
    venv_path = VENV_BIN / name
    if venv_path.exists():
        return str(venv_path)
    return name  # Fallback to PATH


def run_tool(name: str, cmd: List[str], files: List[Path]) -> Tuple[int, str]:
    """Run a tool and capture output."""
    try:
        result = subprocess.run(
            cmd + [str(f) for f in files],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        output = result.stdout + result.stderr
        return result.returncode, output.strip()
    except FileNotFoundError:
        return -1, f"⚠️  {name} not installed. Run: pip install {name.lower()}"


def check_pyflakes(files: List[Path]) -> Tuple[str, int]:
    """Act 1: The Pruning - Detect unused imports and variables."""
    code, output = run_tool("pyflakes", [get_tool_path("pyflakes")], files)
    if code == -1:
        return output, 0
    if not output:
        return "✅ No unused imports or variables detected.", 0
    
    lines = output.strip().split("\n")
    return f"🔍 Pyflakes found {len(lines)} issue(s):\n" + output, len(lines)


def check_isort(files: List[Path]) -> Tuple[str, int]:
    """Act 1 (continued): Check import ordering."""
    code, output = run_tool("isort", [get_tool_path("isort"), "--check-only", "--diff"], files)
    if code == -1:
        return output, 0
    if code == 0:
        return "✅ Imports are correctly ordered.", 0
    
    # Count files that need fixing
    diff_count = output.count("would reformat") + output.count("---")
    return f"🔀 isort found {diff_count} file(s) with misordered imports:\n" + output[:500], diff_count


def check_pyright(files: List[Path]) -> Tuple[str, int]:
    """Act 2: The Illumination - Type checking."""
    # Use pyright in basic mode
    code, output = run_tool("pyright", [get_tool_path("pyright"), "--outputjson"], files)
    if code == -1:
        # Try mypy as fallback
        code, output = run_tool("mypy", [get_tool_path("mypy"), "--ignore-missing-imports"], files)
        if code == -1:
            return "⚠️  Neither pyright nor mypy installed.", 0
    
    if "error" not in output.lower() and code == 0:
        return "✅ No type errors detected.", 0
    
    # Count errors
    error_count = output.lower().count("error")
    summary = output[:1000] if len(output) > 1000 else output
    return f"🔬 Type checker found {error_count} issue(s):\n{summary}", error_count


def check_vulture(files: List[Path]) -> Tuple[str, int]:
    """Act 4: The Exorcism - Dead code detection."""
    code, output = run_tool("vulture", [get_tool_path("vulture"), "--min-confidence", "80"], files)
    if code == -1:
        return output, 0
    if not output:
        return "✅ No dead code detected (confidence > 80%).", 0
    
    lines = output.strip().split("\n")
    return f"💀 Vulture found {len(lines)} potential dead code item(s):\n" + output, len(lines)


def main():
    print("=" * 60)
    print("🧹 THE RITE OF PURIFICATION - Automated Vicinity Sweep")
    print("=" * 60)
    print()
    
    # Determine files to scan
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/purify_vicinity.py [files...] or --all")
        sys.exit(1)
    
    if sys.argv[1] == "--all":
        files = list(SRC_DIR.rglob("*.py"))
        print(f"Scanning all {len(files)} Python files in src/...")
    else:
        files = [Path(f) for f in sys.argv[1:]]
        print(f"Scanning {len(files)} specified file(s)...")
    
    print()
    
    total_issues = 0
    
    # Act 1: The Pruning
    print("─" * 40)
    print("ACT 1: THE PRUNING (Unused Imports)")
    print("─" * 40)
    result, count = check_pyflakes(files)
    print(result)
    total_issues += count
    print()
    
    # Act 1b: Import Ordering
    print("─" * 40)
    print("ACT 1b: IMPORT ORDERING (isort)")
    print("─" * 40)
    result, count = check_isort(files)
    print(result)
    total_issues += count
    print()
    
    # Act 2: The Illumination
    print("─" * 40)
    print("ACT 2: THE ILLUMINATION (Type Hints)")
    print("─" * 40)
    result, count = check_pyright(files)
    print(result)
    total_issues += count
    print()
    
    # Act 4: The Exorcism
    print("─" * 40)
    print("ACT 4: THE EXORCISM (Dead Code)")
    print("─" * 40)
    result, count = check_vulture(files)
    print(result)
    total_issues += count
    print()
    
    # Summary
    print("=" * 60)
    if total_issues == 0:
        print("✅ THE VICINITY IS PURE. No entropy detected.")
        sys.exit(0)
    else:
        print(f"⚠️  TOTAL ENTROPY DETECTED: {total_issues} issue(s)")
        print("   Review and apply cleanups as needed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
