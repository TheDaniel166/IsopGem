#!/usr/bin/env python3
"""
Sophia Scout Bridge
Perform structural inventory (Scout Ritual) on the codebase.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any


def find_pillars(workspace: Path) -> List[str]:
    """Find all pillar directories."""
    pillars_root = workspace / "src" / "pillars"
    if not pillars_root.exists():
        return []
    
    return [p.name for p in pillars_root.iterdir() if p.is_dir() and not p.name.startswith('_')]


def find_missing_inits(workspace: Path) -> List[str]:
    """Find Python packages missing __init__.py files."""
    missing = []
    src_root = workspace / "src"
    
    if not src_root.exists():
        return missing
    
    for dirpath in src_root.rglob('*'):
        if not dirpath.is_dir():
            continue
        
        # Skip __pycache__ and hidden dirs
        if dirpath.name.startswith('__') or dirpath.name.startswith('.'):
            continue
        
        # Check if it has Python files but no __init__.py
        py_files = list(dirpath.glob('*.py'))
        init_file = dirpath / '__init__.py'
        
        if py_files and not init_file.exists():
            rel_path = dirpath.relative_to(workspace)
            missing.append(str(rel_path))
    
    return missing


def find_orphaned_files(workspace: Path) -> List[str]:
    """Find files that might be orphaned (old test files, etc.)."""
    orphaned = []
    patterns = ['test_*.py', '*_test.py', '*.pyc', '*.pyo', '.DS_Store']
    
    src_root = workspace / "src"
    if not src_root.exists():
        return orphaned
    
    for pattern in patterns:
        for filepath in src_root.rglob(pattern):
            # Skip valid test directories
            if 'tests' in filepath.parts or 'test' in filepath.parts:
                continue
            
            rel_path = filepath.relative_to(workspace)
            orphaned.append(str(rel_path))
    
    return orphaned


def check_structure_issues(workspace: Path) -> List[str]:
    """Check for structural issues in pillar organization."""
    issues = []
    pillars_root = workspace / "src" / "pillars"
    
    if not pillars_root.exists():
        return ["Pillars directory not found at src/pillars"]
    
    expected_subdirs = ['models', 'repositories', 'services', 'ui', 'utils']
    
    for pillar_dir in pillars_root.iterdir():
        if not pillar_dir.is_dir() or pillar_dir.name.startswith('_'):
            continue
        
        # Check for expected structure
        for subdir in expected_subdirs:
            expected_path = pillar_dir / subdir
            if not expected_path.exists():
                issues.append(f"{pillar_dir.name}: missing {subdir}/ directory")
    
    return issues


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    scope = sys.argv[2]
    
    result = {
        "pillars": [],
        "missing_inits": [],
        "orphaned_files": [],
        "structure_issues": []
    }
    
    if scope in ('pillars', 'all'):
        result["pillars"] = find_pillars(workspace_root)
    
    if scope in ('structure', 'all'):
        result["missing_inits"] = find_missing_inits(workspace_root)
        result["orphaned_files"] = find_orphaned_files(workspace_root)
        result["structure_issues"] = check_structure_issues(workspace_root)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
