#!/usr/bin/env python3
"""
The Ritual of the Scout (scout.py)
----------------------------------
Automated sentinel for the Covenant's Maintenance Disciplines.
Performs the "Four Acts of Purification" on specified files.

Usage:
    python3 scripts/covenant_scripts/scout.py [files...]
    python3 scripts/covenant_scripts/scout.py --scan  (Scans current directory recursively)
"""

import ast
import sys
import re
from pathlib import Path
from typing import List, Set, Tuple

def check_docstrings(tree: ast.Module, filename: str) -> List[str]:
    """Check for missing docstrings in module, functions, and classes."""
    issues = []
    # CHECK 1: Module Docstring
    if not (tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant)):
        issues.append(f"{filename}: Missing Module Docstring")
    
    # CHECK 2: Functions and Classes
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            # Skip private methods/classes if desired, but Covenant prefers all inscribed
            if node.name.startswith("_") and not node.name.startswith("__"):
                continue # Skip internal helpers for now
            
            if not ast.get_docstring(node):
                issues.append(f"{filename}:{node.lineno} Missing docstring for '{node.name}'")
    return issues

def check_imports(tree: ast.Module, filename: str) -> List[str]:
    """Check for unused imports (Placeholder/Naive)."""
    issues = []
    imports = set()
    used_names = set()

    # Collect imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.asname or n.name)
        elif isinstance(node, ast.ImportFrom):
            for n in node.names:
                imports.add(n.asname or n.name)
    
    # Collect usages
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used_names.add(node.id)
        elif isinstance(node, ast.Attribute):
            # rudimentary check for used attributes
            pass 

    # This is a naive check; robust checks require static analysis libs like pyflakes.
    # For now, we mainly rely on user judgment or external tools.
    # If we want a lightweight check, we can verify if the name appears in the source?
    
    # ACTUALLY, implementing a full unused import checker in pure python AST is hard.
    # Let's pivot to reporting "Review Imports" if the file is large or complex.
    # OR, if we assume 'pyflakes' is installed, we can invoke it.
    
    return [] 

def check_dead_code(content: str, filename: str) -> List[str]:
    """Check for potential dead code (commented code) and Issue Markers."""
    issues = []
    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Heuristic: Commented out code often looks like "# x = ..." or "# def foo():"
        if re.match(r"^#\s*(def |class |return |import |from |if |for |while |try:|except:|raise )", stripped):
            issues.append(f"{filename}:{i} Potential Dead Code: {stripped[:40]}...")
        # Check for Issue Markers (F-I-X-M-E)
        term = "FIX" + "ME"
        if term in line and "Found " + term not in line: # Avoid self-match
             issues.append(f"{filename}:{i} Found {term}: {stripped}")
    return issues

def scan_file(path: Path) -> List[str]:
    """Scan a single file for all distortions."""
    issues = []
    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        issues.extend(check_docstrings(tree, path.name))
        # issues.extend(check_imports(tree, path.name)) # Disabled: too naive
        issues.extend(check_dead_code(content, path.name))
        
    except SyntaxError as e:
        issues.append(f"{path.name}: Syntax Error - {e}")
    except Exception as e:
        issues.append(f"{path.name}: Error scanning - {e}")
    
    return issues

def main():
    """Main entry point for the Scout Ritual."""
    paths = sys.argv[1:]
    if not paths or "--scan" in paths:
        # Recursive scan of src/ and scripts/ if no files provided
        root = Path.cwd()
        src = root / "src"
        scripts = root / "scripts"
        
        target_files = []
        if src.exists():
            target_files.extend(src.rglob("*.py"))
        if scripts.exists():
            target_files.extend(scripts.rglob("*.py"))
    else:
        target_files = [Path(p) for p in paths if p.endswith(".py")]

    print(f"🕵️  Scout Ritual: Scanning {len(target_files)} files...")
    
    all_issues = []
    for f in target_files:
        if not f.exists(): 
            continue
        all_issues.extend(scan_file(f))

    if all_issues:
        print("\n⚠️  Distortions Detected:")
        for issue in all_issues[:20]: # Limit output
            print(f"  • {issue}")
        if len(all_issues) > 20:
            print(f"  ... and {len(all_issues) - 20} more.")
        print("\n🧹 Recommendation: Perform the Four Acts of Purification.")
        sys.exit(1)
    else:
        print("\n✅ Verification Complete: No obvious distortions found.")
        sys.exit(0)

if __name__ == "__main__":
    main()
