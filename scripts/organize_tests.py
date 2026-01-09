#!/usr/bin/env python3
"""
Reorganize tests into subdirectories for auto-marking.

Best practice structure:
    tests/
    ├── unit/              # Fast tests, no I/O (auto-marked @pytest.mark.unit)
    ├── integration/       # Tests with database/filesystem (auto-marked)
    ├── ui/                # PyQt6 tests (auto-marked @pytest.mark.ui)
    └── manual/            # Manual verification tests

This uses pytest's auto-marking hook in conftest.py.
"""
import shutil
from pathlib import Path
from typing import Dict, List, Set

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = PROJECT_ROOT / "tests"


def analyze_test_file(file_path: Path) -> str:
    """Determine which category a test belongs to."""
    content = file_path.read_text()
    name = file_path.name

    # Manual/verification tests
    if "verify_" in name or "rite_of_" in name or file_path.parent.name in ["rituals", "verification", "manual"]:
        return "manual"

    # UI tests (PyQt6)
    if any(keyword in content for keyword in ["PyQt6", "QApplication", "QWidget", "QMainWindow"]):
        return "ui"

    # Integration tests (database, filesystem)
    if any(keyword in content for keyword in [
        "sqlalchemy", "SessionLocal", "create_engine",
        "tmp_path", "isolated_database",
        "DocumentService", "ChartStorageService"
    ]):
        return "integration"

    # Unit tests (pure logic, math)
    if file_path.parent.name == "geometry":
        return "unit"

    # Default based on imports/content
    if "import pytest" in content and not any(keyword in content for keyword in ["database", "session", "Qt"]):
        return "unit"

    return "integration"


def get_reorganization_plan() -> Dict[str, List[Path]]:
    """Create a plan for moving test files."""
    plan = {
        "unit": [],
        "integration": [],
        "ui": [],
        "manual": []
    }

    # Find all test files (excluding examples and _legacy)
    test_files = []
    for pattern in ["test_*.py", "verify_*.py", "rite_*.py"]:
        test_files.extend(TESTS_DIR.rglob(pattern))

    # Filter out special directories
    test_files = [
        f for f in test_files
        if "__pycache__" not in str(f)
        and "examples" not in str(f)
        and "_legacy" not in str(f)
    ]

    for file_path in test_files:
        # Skip if already in target directory structure
        rel_path = file_path.relative_to(TESTS_DIR)
        if rel_path.parts[0] in ["unit", "integration", "ui", "manual"]:
            continue

        category = analyze_test_file(file_path)
        plan[category].append(file_path)

    return plan


def print_plan(plan: Dict[str, List[Path]]):
    """Print the reorganization plan."""
    print("Test Reorganization Plan")
    print("=" * 60)
    print()

    for category, files in sorted(plan.items()):
        print(f"{category.upper()}/  ({len(files)} files)")
        print("-" * 60)

        # Group by current subdirectory
        by_subdir = {}
        for f in files:
            rel_path = f.relative_to(TESTS_DIR)
            if len(rel_path.parts) > 1:
                subdir = rel_path.parts[0]
            else:
                subdir = "(root)"
            by_subdir.setdefault(subdir, []).append(f)

        for subdir, subfiles in sorted(by_subdir.items()):
            if subdir != "(root)":
                print(f"  From {subdir}/:")
            for sf in sorted(subfiles):
                print(f"    → {sf.name}")
        print()


def apply_plan(plan: Dict[str, List[Path]], dry_run: bool = True):
    """Apply the reorganization plan."""

    if dry_run:
        print("DRY RUN - No files will be moved")
        print()
        print_plan(plan)
        return

    print("Applying reorganization...")
    print()

    moved_count = 0

    for category, files in plan.items():
        target_dir = TESTS_DIR / category

        # Create target directory
        target_dir.mkdir(exist_ok=True)

        # Create subdirectories if needed
        subdirs = set()
        for f in files:
            rel_path = f.relative_to(TESTS_DIR)
            if len(rel_path.parts) > 1:
                # Preserve subdirectory structure
                subdirs.add(rel_path.parts[0])

        for subdir in subdirs:
            (target_dir / subdir).mkdir(exist_ok=True)

        # Move files
        for file_path in files:
            rel_path = file_path.relative_to(TESTS_DIR)

            if len(rel_path.parts) > 1:
                # Keep subdirectory
                target = target_dir / rel_path.parts[0] / file_path.name
            else:
                target = target_dir / file_path.name

            # Ensure target directory exists
            target.parent.mkdir(parents=True, exist_ok=True)

            try:
                shutil.move(str(file_path), str(target))
                print(f"✓ {rel_path} → {target.relative_to(TESTS_DIR)}")
                moved_count += 1
            except Exception as e:
                print(f"✗ Failed to move {rel_path}: {e}")

    print()
    print(f"Moved {moved_count} files")
    print()
    print("Updated structure:")
    print("  tests/")
    print("  ├── unit/          # Auto-marked @pytest.mark.unit")
    print("  ├── integration/   # Auto-marked @pytest.mark.integration")
    print("  ├── ui/            # Auto-marked @pytest.mark.ui")
    print("  └── manual/        # Manual verification tests")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Reorganize test files")
    parser.add_argument("--apply", action="store_true",
                       help="Actually move files (default is dry-run)")
    args = parser.parse_args()

    plan = get_reorganization_plan()
    apply_plan(plan, dry_run=not args.apply)


if __name__ == "__main__":
    main()
