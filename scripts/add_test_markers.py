#!/usr/bin/env python3
"""
Script to automatically add pytest markers to existing test files.

This analyzes test files and adds appropriate markers based on:
- File location (tests/geometry/ → likely unit tests)
- Imports (PyQt6 → ui tests, database → integration)
- File patterns (verify_*, rite_of_* → manual/experimental)
- Content analysis (fixture usage, etc.)

Usage:
    python scripts/add_test_markers.py --dry-run    # Preview changes
    python scripts/add_test_markers.py              # Apply changes
"""
import re
import sys
from pathlib import Path
from typing import List, Set
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = PROJECT_ROOT / "tests"


def analyze_test_file(file_path: Path) -> Set[str]:
    """Analyze a test file and suggest markers."""
    markers = set()
    content = file_path.read_text()

    # Check file location patterns
    rel_path = file_path.relative_to(TESTS_DIR)

    # Geometry tests - usually pure math (unit tests)
    if "geometry/" in str(rel_path):
        markers.add("unit")

    # Gematria tests - check if they use database
    if "gematria/" in str(rel_path):
        if "database" in content.lower() or "session" in content.lower():
            markers.add("integration")
        else:
            markers.add("unit")

    # Document tests - usually integration (database)
    if "document/" in str(rel_path):
        markers.add("integration")

    # Astrology tests - check for ephemeris files
    if "astrology/" in str(rel_path):
        if "ephemeris" in content.lower():
            markers.add("requires_data")
        markers.add("integration")

    # Manual verification/ritual tests
    if "ritual" in file_path.name or "verify_" in file_path.name:
        markers.add("experimental")
        if "3d" in file_path.name or "ui" in content.lower():
            markers.add("ui")

    # Check imports for clues
    imports = re.findall(r'^import (\w+)|^from ([\w.]+) import', content, re.MULTILINE)
    flat_imports = [i[0] or i[1] for i in imports]

    # PyQt6 imports → UI test
    if any("PyQt6" in imp or "Qt" in imp for imp in flat_imports):
        markers.add("ui")

    # Database imports → integration test
    if any(db in content.lower() for db in ["sqlalchemy", "sessionmaker", "database.py", "create_engine"]):
        markers.add("integration")

    # Network imports → network test
    if any(net in content.lower() for net in ["requests", "urllib", "http", "sefaria", "wiktionary"]):
        markers.add("network")

    # Check for fixtures that indicate integration
    if "tmp_path" in content or "isolated_database" in content:
        markers.add("integration")

    # Check for time.sleep() → slow test
    if "time.sleep" in content or re.search(r'sleep\(\s*\d+', content):
        markers.add("slow")

    # Check for large data loads
    if any(word in content for word in ["load_all", "enrich_all", "process_all"]):
        markers.add("slow")
        markers.add("memory_intensive")

    # Legacy tests
    if "_legacy" in str(rel_path):
        markers.add("experimental")

    # If no specific marker, default based on name
    if not markers:
        # Pure calculation/logic tests are usually unit tests
        if any(word in file_path.name for word in ["test_calculation", "test_metrics", "test_formula"]):
            markers.add("unit")
        else:
            # Default to integration if unclear
            markers.add("integration")

    return markers


def has_markers(content: str) -> bool:
    """Check if file already has pytest markers."""
    return bool(re.search(r'@pytest\.mark\.\w+', content))


def add_markers_to_file(file_path: Path, markers: Set[str], dry_run: bool = True) -> bool:
    """Add markers to test functions in a file."""
    content = file_path.read_text()

    # Skip if already has markers
    if has_markers(content):
        return False

    # Skip conftest.py and __init__.py
    if file_path.name in ["conftest.py", "__init__.py"]:
        return False

    lines = content.split('\n')
    new_lines = []
    modified = False

    # Ensure pytest is imported
    has_pytest_import = any(re.match(r'^import pytest|^from pytest', line) for line in lines)

    i = 0
    while i < len(lines):
        line = lines[i]

        # Add pytest import after other imports if missing
        if not has_pytest_import and line.strip() and not line.startswith('#'):
            if line.startswith('import ') or line.startswith('from '):
                # Found imports section
                new_lines.append(line)
                # Look ahead for end of imports
                j = i + 1
                while j < len(lines) and (lines[j].startswith('import ') or
                                         lines[j].startswith('from ') or
                                         not lines[j].strip()):
                    new_lines.append(lines[j])
                    j += 1

                # Add pytest import
                new_lines.append("import pytest")
                new_lines.append("")
                has_pytest_import = True
                modified = True
                i = j
                continue

        # Check if this is a test function
        if re.match(r'^def test_\w+', line):
            # Add markers before the function
            for marker in sorted(markers):
                new_lines.append(f"@pytest.mark.{marker}")
                modified = True
            new_lines.append(line)
        else:
            new_lines.append(line)

        i += 1

    if modified:
        if not dry_run:
            file_path.write_text('\n'.join(new_lines))
        return True

    return False


def main(dry_run: bool = True):
    """Main script to add markers to all test files."""

    # Find all test files
    test_files = list(TESTS_DIR.rglob("test_*.py"))
    test_files = [f for f in test_files if "__pycache__" not in str(f)]

    print(f"Found {len(test_files)} test files")
    print()

    # Categorize by markers
    marker_stats = defaultdict(list)
    files_to_modify = []
    files_with_markers = []

    for file_path in sorted(test_files):
        markers = analyze_test_file(file_path)
        content = file_path.read_text()

        if has_markers(content):
            files_with_markers.append(file_path)
            continue

        files_to_modify.append((file_path, markers))

        for marker in markers:
            marker_stats[marker].append(file_path)

    # Print statistics
    print(f"Files already marked: {len(files_with_markers)}")
    print(f"Files to modify: {len(files_to_modify)}")
    print()

    print("Marker Distribution:")
    for marker, files in sorted(marker_stats.items()):
        print(f"  {marker:20} → {len(files):3} files")
    print()

    if dry_run:
        print("DRY RUN - Showing first 10 files that would be modified:")
        print()

        for file_path, markers in files_to_modify[:10]:
            rel_path = file_path.relative_to(PROJECT_ROOT)
            print(f"{rel_path}")
            print(f"  Markers: {', '.join(sorted(markers))}")
            print()

        if len(files_to_modify) > 10:
            print(f"... and {len(files_to_modify) - 10} more files")

        print()
        print("Run without --dry-run to apply changes")
    else:
        print("Applying markers...")
        modified_count = 0

        for file_path, markers in files_to_modify:
            if add_markers_to_file(file_path, markers, dry_run=False):
                modified_count += 1
                rel_path = file_path.relative_to(PROJECT_ROOT)
                print(f"✓ {rel_path}")

        print()
        print(f"Modified {modified_count} files")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add pytest markers to test files")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Preview changes without modifying files (default)")
    parser.add_argument("--apply", action="store_true",
                       help="Actually modify files")

    args = parser.parse_args()

    main(dry_run=not args.apply)
