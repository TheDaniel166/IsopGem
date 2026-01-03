#!/usr/bin/env python3
"""
The Rite of Contamination - UI Purity Detector

Scans ui/ directories for imports of forbidden libraries.
UI files must remain "hollow" - no heavy logic imports.

Usage:
    python3 scripts/covenant_scripts/rite_of_contamination.py
"""
import ast
import sys
from pathlib import Path
from typing import List, Tuple, Set

# This file lives at: <repo>/scripts/covenant_scripts/rite_of_contamination.py
# so repo root is two levels up from this file's parent.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

# Forbidden imports in UI files
FORBIDDEN_LIBRARIES = {
    "sqlalchemy": "Direct database access",
    "pandas": "Heavy data processing",
    "numpy": "Computation logic",
    "requests": "Network I/O",
    "urllib": "Network I/O",
    "httpx": "Network I/O",
    "aiohttp": "Network I/O",
    "lxml": "Parsing logic",
    "bs4": "HTML parsing",
    "beautifulsoup4": "HTML parsing",
}


def extract_imports(filepath: Path) -> List[str]:
    """Extract all import statements from a Python file."""
    imports = []
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split(".")[0])
    except Exception:
        pass
    
    return imports


def is_ui_file(filepath: Path) -> bool:
    """Check if a file is in a ui/ directory."""
    parts = filepath.parts
    return "ui" in parts


def check_contamination(filepath: Path) -> List[Tuple[str, str]]:
    """Check if a UI file imports forbidden libraries."""
    contaminations = []
    imports = extract_imports(filepath)
    
    for imp in imports:
        if imp in FORBIDDEN_LIBRARIES:
            reason = FORBIDDEN_LIBRARIES[imp]
            contaminations.append((imp, reason))
    
    return contaminations


def main():
    print("=" * 60)
    print("🧪 THE RITE OF CONTAMINATION - Purity Guard")
    print("=" * 60)
    print()
    print("Scanning UI files for forbidden imports...")
    print(f"Forbidden: {', '.join(sorted(FORBIDDEN_LIBRARIES.keys()))}")
    print()
    
    total_files = 0
    total_contaminations = 0
    contamination_details = []
    
    # Find all ui/ directories and scan their Python files
    for py_file in SRC_DIR.rglob("*.py"):
        if is_ui_file(py_file):
            total_files += 1
            contaminations = check_contamination(py_file)
            
            if contaminations:
                for lib, reason in contaminations:
                    total_contaminations += 1
                    rel_path = py_file.relative_to(PROJECT_ROOT)
                    contamination_details.append((rel_path, lib, reason))
    
    if contamination_details:
        print("─" * 40)
        print("⚠️  CONTAMINATIONS DETECTED")
        print("─" * 40)
        
        for filepath, lib, reason in contamination_details:
            print(f"\n   {filepath}")
            print(f"   └─ Forbidden import: {lib}")
            print(f"      Reason: {reason}")
    
    print()
    print("=" * 60)
    if total_contaminations == 0:
        print(f"✅ THE VIEW REMAINS PURE")
        print(f"   Scanned: {total_files} UI files")
        print(f"   Contaminations: 0")
        sys.exit(0)
    else:
        print(f"🔴 CONTAMINATION DETECTED: {total_contaminations} violation(s)")
        print(f"   Scanned: {total_files} UI files")
        print("   Extract logic to a Service layer.")
        sys.exit(1)


if __name__ == "__main__":
    main()
