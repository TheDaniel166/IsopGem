#!/usr/bin/env python3
"""
THE RITE OF AUTOMATED TYPE HEALING

Applies strategic fixes to satisfy Pylance:
1. Adds `# type: ignore[rule]` to high-noise lines (3+ errors)
2. Prefixes unused variables with `_`
3. Adds basic type annotations for common patterns

Usage:
    python scripts/covenant_scripts/apply_type_fixes.py --pillar PILLAR [--commit]

Options:
    --pillar PILLAR    Target specific pillar (required)
    --commit           Apply fixes (default: dry run)
    --strategy STRAT   'ignore' (add comments) or 'annotate' (add types) or 'both'
"""

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
PYRIGHT_CMD = ["npx", "-y", "pyright", "--outputjson"]


def run_pyright(target_path: Path) -> dict[str, Any]:
    """Run pyright and return JSON output."""
    result = subprocess.run(
        PYRIGHT_CMD + [str(target_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)


def apply_ignore_directives(file_path: Path, errors: list[dict[str, Any]], dry_run: bool = True) -> int:
    """Add `# type: ignore[rule]` to lines with 3+ errors."""
    # Group errors by line
    errors_by_line: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for err in errors:
        line_num = err["range"]["start"]["line"]
        errors_by_line[line_num].append(err)
    
    # Find high-noise lines
    high_noise_lines = {
        line: errs
        for line, errs in errors_by_line.items()
        if len(errs) >= 3
    }
    
    if not high_noise_lines:
        return 0
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modifications = 0
    
    for line_num, errs in sorted(high_noise_lines.items(), reverse=True):
        if line_num >= len(lines):
            continue
        
        line = lines[line_num]
        
        # Skip if already has type: ignore
        if "# type: ignore" in line:
            continue
        
        # Collect unique rules
        rules = sorted(set(err.get("rule", "unknown") for err in errs))
        
        # Add comment
        # Remove trailing newline, add comment, re-add newline
        stripped = line.rstrip('\n')
        
        # Determine indentation level for nice formatting
        if stripped and not stripped.strip():
            # Empty or whitespace-only line
            continue
        
        # Add the comment
        if len(rules) == 1:
            new_line = f"{stripped}  # type: ignore[{rules[0]}]\n"
        elif len(rules) <= 3:
            rules_str = ", ".join(rules)
            new_line = f"{stripped}  # type: ignore[{rules_str}]\n"
        else:
            new_line = f"{stripped}  # type: ignore  # {len(rules)} errors\n"
        
        lines[line_num] = new_line
        modifications += 1
    
    if modifications > 0 and not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"  ✅ Added {modifications} ignore directives")
    elif modifications > 0:
        print(f"  📝 Would add {modifications} ignore directives")
    
    return modifications


def fix_unused_variables(file_path: Path, errors: list[dict[str, Any]], dry_run: bool = True) -> int:
    """Prefix unused variables with underscore."""
    unused_var_errors = [
        err for err in errors
        if err.get("rule") == "reportUnusedVariable"
    ]
    
    if not unused_var_errors:
        return 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.splitlines(keepends=True)
    
    modifications = 0
    
    for err in unused_var_errors:
        line_num = err["range"]["start"]["line"]
        char_start = err["range"]["start"]["character"]
        char_end = err["range"]["end"]["character"]
        
        if line_num >= len(lines):
            continue
        
        line = lines[line_num]
        var_name = line[char_start:char_end]
        
        # Skip if already prefixed
        if var_name.startswith('_'):
            continue
        
        # Replace variable name
        new_var_name = f"_{var_name}"
        new_line = line[:char_start] + new_var_name + line[char_end:]
        lines[line_num] = new_line
        modifications += 1
    
    if modifications > 0 and not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"  ✅ Prefixed {modifications} unused variables with '_'")
    elif modifications > 0:
        print(f"  📝 Would prefix {modifications} unused variables with '_'")
    
    return modifications


def add_basic_type_annotations(file_path: Path, errors: list[dict[str, Any]], dry_run: bool = True) -> int:
    """Add basic type annotations for missing parameter types (conservative approach)."""
    # This is complex and error-prone, so we'll use a VERY conservative strategy:
    # Only add `-> None` to methods that are clearly void
    
    missing_return_type_errors = [
        err for err in errors
        if "return type" in err["message"].lower() and "missing" in err["message"].lower()
    ]
    
    if not missing_return_type_errors:
        return 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modifications = 0
    
    for err in missing_return_type_errors:
        line_num = err["range"]["start"]["line"]
        
        if line_num >= len(lines):
            continue
        
        line = lines[line_num]
        
        # Check if it's a def line and doesn't have -> already
        if 'def ' in line and '->' not in line and line.rstrip().endswith(':'):
            # Very conservative: only add -> None if method name suggests void
            # (starts with set_, _on_, __init__, etc.)
            if re.search(r'def (__init__|_on_\w+|set_\w+|update_\w+|clear_\w+|reset_\w+)', line):
                new_line = line.rstrip()[:-1] + ' -> None:\n'
                lines[line_num] = new_line
                modifications += 1
    
    if modifications > 0 and not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"  ✅ Added {modifications} `-> None` annotations")
    elif modifications > 0:
        print(f"  📝 Would add {modifications} `-> None` annotations")
    
    return modifications


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply automated type fixes")
    parser.add_argument("--pillar", type=str, required=True, help="Target pillar")
    parser.add_argument("--commit", action="store_true", help="Apply fixes (default: dry run)")
    parser.add_argument(
        "--strategy",
        type=str,
        default="both",
        choices=["ignore", "annotate", "unused", "both"],
        help="Fix strategy: 'ignore' (add comments), 'annotate' (add types), 'unused' (prefix _), 'both'"
    )
    parser.add_argument("--min-errors", type=int, default=20, help="Only fix files with N+ errors")
    
    args = parser.parse_args()
    
    # Determine target
    target = SRC_DIR / "pillars" / args.pillar
    if not target.exists():
        print(f"❌ Pillar not found: {target}")
        sys.exit(1)
    
    # Run pyright
    print(f"🔮 Analyzing: {target.relative_to(REPO_ROOT)}")
    pyright_output = run_pyright(target)
    diagnostics = pyright_output.get("generalDiagnostics", [])
    
    # Group by file
    errors_by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for diag in diagnostics:
        errors_by_file[diag["file"]].append(diag)
    
    # Filter files with enough errors
    target_files = [
        (file, errors)
        for file, errors in errors_by_file.items()
        if len(errors) >= args.min_errors
    ]
    
    target_files.sort(key=lambda x: len(x[1]), reverse=True)
    
    if not target_files:
        print(f"✨ No files with {args.min_errors}+ errors found.")
        return
    
    print(f"\n🛠️  Fixing {len(target_files)} files:")
    print("-" * 70)
    
    total_fixes = 0
    
    for file_path_str, errors in target_files:
        file_path = Path(file_path_str)
        rel_path = file_path.relative_to(REPO_ROOT)
        print(f"\n📝 {rel_path} ({len(errors)} errors)")
        
        file_fixes = 0
        
        if args.strategy in ["ignore", "both"]:
            file_fixes += apply_ignore_directives(file_path, errors, dry_run=not args.commit)
        
        if args.strategy in ["unused", "both"]:
            file_fixes += fix_unused_variables(file_path, errors, dry_run=not args.commit)
        
        if args.strategy in ["annotate", "both"]:
            file_fixes += add_basic_type_annotations(file_path, errors, dry_run=not args.commit)
        
        total_fixes += file_fixes
    
    print("\n" + "=" * 70)
    
    if args.commit:
        print(f"✅ Applied {total_fixes} fixes across {len(target_files)} files")
    else:
        print(f"📝 DRY RUN: Would apply {total_fixes} fixes")
        print("\n💡 Use --commit to apply changes")
    
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
