#!/usr/bin/env python3
"""
Sophia Seal Bridge
Run verification rituals (Seals) on the codebase.
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List


def run_sovereignty_check(workspace: Path) -> Dict[str, Any]:
    """Run pillar sovereignty verification."""
    script_path = workspace / "scripts" / "covenant_scripts" / "rite_of_sovereignty.py"
    
    if not script_path.exists():
        return {
            "passed": False,
            "violations": [],
            "details": "rite_of_sovereignty.py script not found"
        }
    
    try:
        venv_python = workspace / ".venv" / "bin" / "python"
        if not venv_python.exists():
            venv_python = "python3"
        
        result = subprocess.run(
            [str(venv_python), str(script_path)],
            capture_output=True,
            text=True,
            cwd=workspace
        )
        
        violations = []
        if "VIOLATION" in result.stdout or "import" in result.stdout.lower():
            for line in result.stdout.split('\n'):
                if 'pillars/' in line and 'import' in line.lower():
                    violations.append(line.strip())
        
        passed = len(violations) == 0 and result.returncode == 0
        
        return {
            "passed": passed,
            "violations": violations,
            "details": result.stdout[:500] if result.stdout else "Check completed"
        }
    except Exception as e:
        return {
            "passed": False,
            "violations": [],
            "details": f"Error running sovereignty check: {str(e)}"
        }


def run_ui_purity_check(workspace: Path) -> Dict[str, Any]:
    """Check UI files don't import heavy libraries."""
    violations = []
    ui_dirs = list((workspace / "src" / "pillars").rglob("ui"))
    
    forbidden_imports = ['sqlalchemy', 'pandas', 'requests', 'httpx', 'sqlite3']
    
    for ui_dir in ui_dirs:
        if not ui_dir.exists():
            continue
        
        for py_file in ui_dir.rglob("*.py"):
            try:
                content = py_file.read_text()
                for forbidden in forbidden_imports:
                    if f"import {forbidden}" in content or f"from {forbidden}" in content:
                        rel_path = py_file.relative_to(workspace)
                        violations.append(f"{rel_path}: imports {forbidden}")
            except Exception:
                continue
    
    return {
        "passed": len(violations) == 0,
        "violations": violations,
        "details": f"Checked {len(list((workspace / 'src' / 'pillars').rglob('ui/*.py')))} UI files"
    }


def run_dual_inscription_check(workspace: Path) -> Dict[str, Any]:
    """Verify covenant scrolls are in sync."""
    canonical = workspace / "wiki" / "00_foundations" / "covenant"
    mirror = workspace / ".github" / "instructions" / "covenant"
    
    if not canonical.exists():
        return {
            "passed": False,
            "violations": ["Canonical covenant directory not found"],
            "details": "wiki/00_foundations/covenant/ does not exist"
        }
    
    if not mirror.exists():
        return {
            "passed": False,
            "violations": ["Mirror covenant directory not found"],
            "details": ".github/instructions/covenant/ does not exist"
        }
    
    violations = []
    canonical_files = {f.name for f in canonical.glob("*.md")}
    mirror_files = {f.name for f in mirror.glob("*.md")}
    
    missing_in_mirror = canonical_files - mirror_files
    missing_in_canonical = mirror_files - canonical_files
    
    for filename in missing_in_mirror:
        violations.append(f"Missing in mirror: {filename}")
    
    for filename in missing_in_canonical:
        violations.append(f"Missing in canonical: {filename}")
    
    return {
        "passed": len(violations) == 0,
        "violations": violations,
        "details": f"Compared {len(canonical_files)} canonical files with mirror"
    }


def run_all_seals(workspace: Path) -> Dict[str, Any]:
    """Run all verification seals."""
    results = {
        "sovereignty": run_sovereignty_check(workspace),
        "ui_purity": run_ui_purity_check(workspace),
        "dual_inscription": run_dual_inscription_check(workspace)
    }
    
    all_passed = all(r["passed"] for r in results.values())
    all_violations = []
    for seal, result in results.items():
        for violation in result["violations"]:
            all_violations.append(f"[{seal}] {violation}")
    
    return {
        "passed": all_passed,
        "violations": all_violations,
        "details": json.dumps(results, indent=2)
    }


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    seal_name = sys.argv[2]
    
    seal_map = {
        "sovereignty": run_sovereignty_check,
        "ui_purity": run_ui_purity_check,
        "dual_inscription": run_dual_inscription_check,
        "all": run_all_seals
    }
    
    if seal_name not in seal_map:
        result = {
            "seal": seal_name,
            "passed": False,
            "violations": [f"Unknown seal: {seal_name}"],
            "details": f"Valid seals: {', '.join(seal_map.keys())}"
        }
    else:
        check_result = seal_map[seal_name](workspace_root)
        result = {
            "seal": seal_name,
            **check_result
        }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
