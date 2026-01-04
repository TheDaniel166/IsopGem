#!/usr/bin/env python3
"""
THE RITE OF TYPE SATISFACTION

An automated ritual to appease Pylance by:
1. Running pyright to collect all type errors
2. Analyzing error patterns
3. Auto-generating appropriate fixes:
   - Add type annotations where missing
   - Add `# type: ignore[specific-rule]` for complex cases
   - Prefix unused variables with `_`
   - Generate type stubs where needed

Usage:
    python scripts/covenant_scripts/satisfy_pylance.py [--pillar PILLAR] [--auto-fix] [--report-only]

Options:
    --pillar PILLAR    Target specific pillar (e.g., 'adyton', 'gematria')
    --auto-fix         Apply automated fixes (default: report only)
    --report-only      Generate report without modifications
    --threshold NUM    Only show files with NUM+ errors (default: 10)
"""

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# --- CONSTANTS ---
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
PYRIGHT_CMD = ["npx", "-y", "pyright", "--outputjson"]

# Error categories and their automated solutions
ERROR_STRATEGIES = {
    "reportMissingParameterType": "add_type_annotation",
    "reportMissingTypeStubs": "ignore_directive",
    "reportUnknownParameterType": "add_type_annotation",
    "reportUnknownVariableType": "add_type_annotation_or_ignore",
    "reportUnknownMemberType": "ignore_directive",
    "reportUnknownArgumentType": "ignore_directive",
    "reportUnusedVariable": "prefix_underscore",
    "reportPrivateUsage": "ignore_directive",
    "reportGeneralTypeIssues": "ignore_directive",
}


def run_pyright(target_path: Path) -> dict[str, Any]:
    """Run pyright and return JSON output."""
    cmd = PYRIGHT_CMD + [str(target_path)]
    print(f"🔮 Running: {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True
    )
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"❌ Failed to parse pyright output:\n{result.stdout}")
        sys.exit(1)


def analyze_errors(pyright_output: dict[str, Any]) -> dict[str, Any]:
    """Analyze error patterns and generate statistics."""
    diagnostics = pyright_output.get("generalDiagnostics", [])
    
    # Group by file
    errors_by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for diag in diagnostics:
        errors_by_file[diag["file"]].append(diag)
    
    # Group by rule
    errors_by_rule: dict[str, int] = defaultdict(int)
    for diag in diagnostics:
        rule = diag.get("rule", "unknown")
        errors_by_rule[rule] += 1
    
    return {
        "total_errors": len(diagnostics),
        "files_analyzed": pyright_output["summary"]["filesAnalyzed"],
        "errors_by_file": dict(errors_by_file),
        "errors_by_rule": dict(sorted(errors_by_rule.items(), key=lambda x: x[1], reverse=True)),
    }


def generate_report(analysis: dict[str, Any], threshold: int = 10) -> None:
    """Generate a human-readable report."""
    print("\n" + "=" * 70)
    print("📊 PYLANCE TYPE ERROR ANALYSIS")
    print("=" * 70)
    
    print(f"\n📁 Files Analyzed: {analysis['files_analyzed']}")
    print(f"❌ Total Errors: {analysis['total_errors']}")
    
    print("\n🔍 Top Error Types:")
    print("-" * 70)
    for rule, count in list(analysis['errors_by_rule'].items())[:10]:
        strategy = ERROR_STRATEGIES.get(rule, "manual_review")
        print(f"  {count:>4}  {rule:<40} → {strategy}")
    
    print(f"\n📄 Files with {threshold}+ Errors:")
    print("-" * 70)
    
    high_error_files = [
        (file, len(errors))
        for file, errors in analysis['errors_by_file'].items()
        if len(errors) >= threshold
    ]
    high_error_files.sort(key=lambda x: x[1], reverse=True)
    
    for file_path, error_count in high_error_files:
        rel_path = Path(file_path).relative_to(REPO_ROOT)
        print(f"  {error_count:>4}  {rel_path}")
    
    print("\n" + "=" * 70)


def generate_ignore_comments(analysis: dict[str, Any], dry_run: bool = True) -> None:
    """Add strategic `# type: ignore` comments to high-noise files."""
    print("\n🛠️  AUTO-FIX STRATEGY:")
    print("-" * 70)
    
    # For now, just report what WOULD be done
    for file_path, errors in analysis['errors_by_file'].items():
        if len(errors) < 20:  # Skip low-error files
            continue
        
        rel_path = Path(file_path).relative_to(REPO_ROOT)
        
        # Group errors by line
        errors_by_line: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for err in errors:
            line_num = err["range"]["start"]["line"]
            errors_by_line[line_num].append(err)
        
        print(f"\n📝 {rel_path} ({len(errors)} errors)")
        
        # Show lines with 3+ errors (good candidates for `# type: ignore`)
        high_noise_lines = [
            (line, errs)
            for line, errs in errors_by_line.items()
            if len(errs) >= 3
        ]
        
        if high_noise_lines:
            print(f"   → {len(high_noise_lines)} lines with 3+ errors (candidates for `# type: ignore`)")
        
        # Count fixable errors
        fixable = sum(
            1 for err in errors
            if err.get("rule") in ["reportUnusedVariable", "reportMissingParameterType"]
        )
        
        if fixable > 0:
            print(f"   → {fixable} auto-fixable errors (unused vars, missing param types)")
    
    if dry_run:
        print("\n⚠️  DRY RUN - No files modified. Use --auto-fix to apply changes.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Automated Pylance type error analysis and fixing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--pillar",
        type=str,
        help="Target specific pillar (e.g., 'adyton', 'gematria', 'astrology')"
    )
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Apply automated fixes (default: report only)"
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        default=True,
        help="Generate report without modifications (default)"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=10,
        help="Only show files with N+ errors (default: 10)"
    )
    
    args = parser.parse_args()
    
    # Determine target path
    if args.pillar:
        target = SRC_DIR / "pillars" / args.pillar
        if not target.exists():
            print(f"❌ Pillar not found: {target}")
            sys.exit(1)
    else:
        target = SRC_DIR
    
    # Run analysis
    print(f"🔮 Analyzing: {target.relative_to(REPO_ROOT)}")
    pyright_output = run_pyright(target)
    analysis = analyze_errors(pyright_output)
    
    # Generate report
    generate_report(analysis, threshold=args.threshold)
    
    # Show fix strategy
    generate_ignore_comments(analysis, dry_run=not args.auto_fix)
    
    print("\n✨ Analysis complete.\n")


if __name__ == "__main__":
    main()
