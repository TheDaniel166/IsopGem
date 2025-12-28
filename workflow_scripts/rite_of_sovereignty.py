#!/usr/bin/env python3
"""
The Rite of Sovereignty - Cross-Pillar Import Detector

Scans src/pillars/ for illegal imports between pillars.
Pillars must remain sovereign - no direct imports allowed.

Usage:
    python3 scripts/rite_of_sovereignty.py
"""
import ast
import sys
from pathlib import Path
from typing import List, Tuple, Set

PROJECT_ROOT = Path(__file__).parent.parent
PILLARS_DIR = PROJECT_ROOT / "src" / "pillars"

# These are the sovereign territories
PILLAR_NAMES: Set[str] = set()


def discover_pillars() -> Set[str]:
    """Discover all pillar names dynamically."""
    pillars = set()
    if PILLARS_DIR.exists():
        for item in PILLARS_DIR.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                pillars.add(item.name)
    return pillars


def extract_imports(filepath: Path) -> List[str]:
    """Extract all import statements from a Python file."""
    imports = []
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except Exception:
        pass
    
    return imports


def get_pillar_of_file(filepath: Path) -> str:
    """Determine which pillar a file belongs to."""
    try:
        rel_path = filepath.relative_to(PILLARS_DIR)
        return rel_path.parts[0]
    except ValueError:
        return ""


def check_sovereignty(filepath: Path, home_pillar: str) -> List[Tuple[str, str]]:
    """Check if a file violates sovereignty by importing from other pillars."""
    violations = []
    imports = extract_imports(filepath)
    
    for imp in imports:
        # Check if import references another pillar
        # Pattern: pillars.OTHER_PILLAR or src.pillars.OTHER_PILLAR
        for pillar in PILLAR_NAMES:
            if pillar == home_pillar:
                continue
            
            patterns = [
                f"pillars.{pillar}",
                f"src.pillars.{pillar}",
                f"..{pillar}.",  # Relative imports
            ]
            
            for pattern in patterns:
                if pattern in imp or imp.startswith(f"pillars.{pillar}"):
                    violations.append((imp, pillar))
                    break
    
    return violations


def main():
    global PILLAR_NAMES
    PILLAR_NAMES = discover_pillars()
    
    print("=" * 60)
    print("🏛️  THE RITE OF SOVEREIGNTY - Pillar Guard")
    print("=" * 60)
    print()
    print(f"Discovered {len(PILLAR_NAMES)} sovereign pillars: {', '.join(sorted(PILLAR_NAMES))}")
    print()
    
    total_files = 0
    total_violations = 0
    violation_details = []
    
    for pillar in sorted(PILLAR_NAMES):
        pillar_dir = PILLARS_DIR / pillar
        
        for py_file in pillar_dir.rglob("*.py"):
            total_files += 1
            violations = check_sovereignty(py_file, pillar)
            
            if violations:
                for imp, foreign_pillar in violations:
                    total_violations += 1
                    rel_path = py_file.relative_to(PROJECT_ROOT)
                    violation_details.append((rel_path, pillar, foreign_pillar, imp))
    
    if violation_details:
        print("─" * 40)
        print("⚠️  SOVEREIGNTY VIOLATIONS DETECTED")
        print("─" * 40)
        
        for filepath, home, foreign, imp in violation_details:
            print(f"\n   {filepath}")
            print(f"   └─ Pillar '{home}' imports from '{foreign}'")
            print(f"      Import: {imp}")
    
    print()
    print("=" * 60)
    if total_violations == 0:
        print(f"✅ THE PILLARS STAND SOVEREIGN")
        print(f"   Scanned: {total_files} files")
        print(f"   Violations: 0")
        sys.exit(0)
    else:
        print(f"🔴 ENTANGLEMENT DETECTED: {total_violations} violation(s)")
        print(f"   Scanned: {total_files} files")
        print("   Resolve by using shared/ services or Signal Bus.")
        sys.exit(1)


if __name__ == "__main__":
    main()
