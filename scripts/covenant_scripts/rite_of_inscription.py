#!/usr/bin/env python3
"""
The Rite of Inscription - Docstring Audit

Scans Python files for missing, empty, or banal docstrings.
Public functions and classes must explain their Intent.

Usage:
    python3 scripts/rite_of_inscription.py [file_or_dir]
    python3 scripts/rite_of_inscription.py --all
"""
import ast
import sys
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"

# Banal phrases that indicate lazy documentation
BANAL_PHRASES = [
    "returns the value",
    "returns the result",
    "calculates the value",
    "calculates the result",
    "does the thing",
    "standard boilerplate",
    "standard method",
    "none detected",
    "todo",
    "fixme",
    "placeholder",
]


def extract_docstrings(filepath: Path) -> List[Tuple[str, int, str, str]]:
    """
    Extract all public functions/classes and their docstrings.
    Returns: [(name, line, kind, docstring), ...]
    """
    items = []
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = node.name
                line = node.lineno
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                
                # Skip private/magic methods
                if name.startswith("_"):
                    continue
                
                # Get docstring
                docstring = ast.get_docstring(node) or ""
                items.append((name, line, kind, docstring))
                
    except Exception:
        pass
    
    return items


def check_docstring_quality(docstring: str) -> Tuple[str, bool]:
    """
    Check if a docstring is present and meaningful.
    Returns: (issue, is_valid)
    """
    if not docstring:
        return "Missing", False
    
    if len(docstring.strip()) < 10:
        return "Too short", False
    
    docstring_lower = docstring.lower()
    for phrase in BANAL_PHRASES:
        if phrase in docstring_lower:
            return f"Banal ('{phrase}')", False
    
    return "OK", True


def main():
    print("=" * 60)
    print("📜 THE RITE OF INSCRIPTION - Docstring Audit")
    print("=" * 60)
    print()
    
    # Determine files to scan
    if len(sys.argv) < 2 or sys.argv[1] == "--all":
        files = list(SRC_DIR.rglob("*.py"))
        print(f"Scanning all {len(files)} Python files in src/...")
    else:
        target = Path(sys.argv[1]).resolve()
        if target.is_dir():
            files = list(target.rglob("*.py"))
        else:
            files = [target]
        print(f"Scanning {len(files)} file(s)...")
    
    print()
    
    total_items = 0
    missing_count = 0
    short_count = 0
    banal_count = 0
    issues = []
    
    for filepath in files:
        items = extract_docstrings(filepath)
        
        for name, line, kind, docstring in items:
            total_items += 1
            issue, is_valid = check_docstring_quality(docstring)
            
            if not is_valid:
                rel_path = filepath.relative_to(PROJECT_ROOT)
                issues.append((rel_path, line, kind, name, issue))
                
                if issue == "Missing":
                    missing_count += 1
                elif issue == "Too short":
                    short_count += 1
                else:
                    banal_count += 1
    
    if issues:
        print("─" * 40)
        print("⚠️  UNINSCRIBED ITEMS DETECTED")
        print("─" * 40)
        
        for filepath, line, kind, name, issue in issues[:50]:  # Limit output
            print(f"\n   {filepath}:{line}")
            print(f"   └─ {kind} '{name}': {issue}")
        
        if len(issues) > 50:
            print(f"\n   ... and {len(issues) - 50} more")
    
    print()
    print("=" * 60)
    total_issues = missing_count + short_count + banal_count
    
    if total_issues == 0:
        print("✅ ALL INSCRIPTIONS ARE WORTHY")
        print(f"   Scanned: {total_items} public items")
        sys.exit(0)
    else:
        print(f"📜 INSCRIPTION AUDIT RESULTS")
        print(f"   Scanned: {len(files)} files, {total_items} public items")
        print(f"   Missing: {missing_count}")
        print(f"   Too Short: {short_count}")
        print(f"   Banal: {banal_count}")
        print()
        print("   Inscribe intent into the uninscribed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
