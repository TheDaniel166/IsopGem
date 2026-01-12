#!/usr/bin/env python3
"""
Sophia Verify Bridge
Check architectural rules and constraints.
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any


# Pillar names
PILLARS = ["astrology", "etymos", "exegesis", "gematria", "kamea"]

# Heavy imports that shouldn't be in UI
HEAVY_IMPORTS = [
    "sqlalchemy", "pandas", "numpy", "requests",
    "aiohttp", "scipy", "sklearn", "torch"
]


def check_pillar_sovereignty(workspace: Path, target: str) -> List[Dict[str, Any]]:
    """Check for cross-pillar imports (pillar A importing from pillar B)."""
    violations = []
    src_dir = workspace / "src" / "pillars"
    
    if not src_dir.exists():
        return violations
    
    # Determine which files to check
    if target:
        target_path = workspace / target
        if target_path.is_file():
            files_to_check = [target_path]
        else:
            files_to_check = list(target_path.rglob("*.py"))
    else:
        files_to_check = list(src_dir.rglob("*.py"))
    
    for filepath in files_to_check:
        # Determine which pillar this file belongs to
        relative = filepath.relative_to(src_dir)
        parts = relative.parts
        if not parts or parts[0] not in PILLARS:
            continue
        
        current_pillar = parts[0]
        
        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception:
            continue
        
        # Check for imports from other pillars
        import_pattern = r'^(?:from|import)\s+(?:src\.)?pillars\.(\w+)'
        for line_num, line in enumerate(content.split('\n'), 1):
            match = re.match(import_pattern, line.strip())
            if match:
                imported_pillar = match.group(1)
                if imported_pillar in PILLARS and imported_pillar != current_pillar:
                    violations.append({
                        "file": str(filepath.relative_to(workspace)),
                        "line": line_num,
                        "rule": "pillar_sovereignty",
                        "description": f"Pillar '{current_pillar}' importing from pillar '{imported_pillar}'. Use shared substrate instead.",
                        "severity": "error"
                    })
    
    return violations


def check_ui_purity(workspace: Path, target: str) -> List[Dict[str, Any]]:
    """Check that UI code doesn't import heavy libraries."""
    violations = []
    
    # Find UI directories
    ui_dirs = []
    if target:
        target_path = workspace / target
        if "ui" in str(target_path):
            ui_dirs.append(target_path if target_path.is_dir() else target_path.parent)
    else:
        src_dir = workspace / "src"
        if src_dir.exists():
            ui_dirs.extend(src_dir.rglob("ui"))
    
    for ui_dir in ui_dirs:
        if not ui_dir.is_dir():
            continue
        
        for filepath in ui_dir.rglob("*.py"):
            try:
                content = filepath.read_text(encoding='utf-8')
            except Exception:
                continue
            
            # Check for heavy imports
            for line_num, line in enumerate(content.split('\n'), 1):
                line_stripped = line.strip()
                if not (line_stripped.startswith('import ') or line_stripped.startswith('from ')):
                    continue
                
                for heavy_lib in HEAVY_IMPORTS:
                    if heavy_lib in line_stripped:
                        violations.append({
                            "file": str(filepath.relative_to(workspace)),
                            "line": line_num,
                            "rule": "ui_purity",
                            "description": f"UI code importing '{heavy_lib}'. Use Services layer instead.",
                            "severity": "error"
                        })
                        break
    
    return violations


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    check_type = sys.argv[2]
    target_path = sys.argv[3] if len(sys.argv) > 3 else ""
    
    violations = []
    
    if check_type in ["pillar_sovereignty", "all"]:
        violations.extend(check_pillar_sovereignty(workspace_root, target_path))
    
    if check_type in ["ui_purity", "all"]:
        violations.extend(check_ui_purity(workspace_root, target_path))
    
    passed = len(violations) == 0
    
    summary = f"Found {len(violations)} violation(s)"
    if passed:
        summary = "All checks passed ✓"
    
    result = {
        "check_type": check_type,
        "target": target_path or "entire workspace",
        "violations": violations,
        "passed": passed,
        "summary": summary
    }
    
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
