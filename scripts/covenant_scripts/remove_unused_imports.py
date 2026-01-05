#!/usr/bin/env python3
"""
Remove unused imports using pyflakes detection
"""
import subprocess
import re
from pathlib import Path
from typing import Set
import json
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"


def get_unused_imports(file_path: Path) -> dict[int, set[str]]:
    """Run pyright and return dict of line_num -> set of unused names."""
    try:
        # Run pyright on the specific file
        # Using npx -y pyright to ensure we use the project version
        result = subprocess.run(
            ["npx", "-y", "pyright", "--outputjson", str(file_path)],
            capture_output=True,
            text=True
        )
        
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Pyright might verify clean and return empty or non-json if failed
            return {}
            
        diagnostics = output.get("generalDiagnostics", [])
        unused = defaultdict(set)
        
        for diag in diagnostics:
            if diag.get("rule") == "reportUnusedImport":
                # Line numbers in Pyright are 0-indexed
                line_num = diag["range"]["start"]["line"] + 1
                message = diag.get("message", "")
                
                # Message format: "Import 'X' is not accessed"
                match = re.search(r"Import '([^']+)' is not accessed", message)
                if match:
                    name = match.group(1)
                    unused[line_num].add(name)
        
        return unused
    except Exception as e:
        print(f"Error running pyright on {file_path}: {e}")
        return {}


def remove_unused_imports_from_file(file_path: Path, dry_run: bool = True) -> int:
    """Remove unused import lines from a file."""
    unused = get_unused_imports(file_path)
    
    if not unused:
        return 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    removed = 0
    new_lines = []
    
    for line in lines:
        # Check if this line imports any unused names
        should_remove = False
        
        for unused_name in unused:
            # Match: from X import Y, Z
            # Match: import X
            # Match: import X as Y
            patterns = [
                rf"^from .+ import .+\b{re.escape(unused_name)}\b",
                rf"^import {re.escape(unused_name)}\b",
                rf"^import .+ as {re.escape(unused_name)}\b",
            ]
            
            if any(re.search(pat, line.strip()) for pat in patterns):
                # Check if this is the ONLY import on the line
                # If it's "from X import A, B" and only A is unused, keep the line
                if re.search(r"^from .+ import ", line.strip()):
                    imports_on_line = re.search(r"import (.+)", line).group(1)
                    import_names = [n.strip().split()[0] for n in imports_on_line.split(',')]
                    
                    if len(import_names) == 1 and import_names[0] in unused:
                        should_remove = True
                        break
                else:
                    # Single import statement
                    should_remove = True
                    break
        
        if should_remove:
            removed += 1
            print(f"  - Removing: {line.rstrip()}")
        else:
            new_lines.append(line)
    
    if removed > 0 and not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    
    return removed


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Remove unused imports")
    parser.add_argument("--commit", action="store_true", help="Apply changes")
    parser.add_argument("--pillar", type=str, help="Target specific pillar")
    
    args = parser.parse_args()
    
    if args.pillar:
        target = SRC_DIR / "pillars" / args.pillar
    else:
        target = SRC_DIR
    
    total_removed = 0
    
    for py_file in target.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        removed = remove_unused_imports_from_file(py_file, dry_run=not args.commit)
        
        if removed > 0:
            rel_path = py_file.relative_to(REPO_ROOT)
            print(f"{'✅' if args.commit else '📝'} {rel_path}: {removed} imports")
            total_removed += removed
    
    print(f"\n{'✅ Removed' if args.commit else '📝 Would remove'} {total_removed} unused imports")


if __name__ == "__main__":
    main()
