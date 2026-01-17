#!/usr/bin/env python3
"""
Sophia Trace: Dependency analysis for refactoring.

Purpose: Analyze what imports a module and what it imports.
         Assess impact of changes before refactoring.

Usage:
    python scripts/covenant_scripts/trace.py <workspace_root> "<target_module>"

Example:
    python scripts/covenant_scripts/trace.py . "src/pillars/gematria/services/calculator.py"
"""
import sys
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Set


def resolve_workspace(workspace_arg: str = None) -> Path:
    """Resolve workspace root."""
    if workspace_arg:
        path = Path(workspace_arg)
        if path.exists():
            return path.resolve()
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".git").exists() or (parent / "src").exists():
            return parent
    return cwd


def output_json(data: dict) -> None:
    """Output JSON to stdout."""
    print(json.dumps(data, indent=2, default=str))


def output_error(message: str, details: str = None) -> None:
    """Output error and exit."""
    error_data = {"error": message}
    if details:
        error_data["details"] = details
    output_json(error_data)
    sys.exit(1)


def extract_imports(content: str) -> Set[str]:
    """Extract import statements from Python content."""
    imports = set()
    
    # Match: import module
    for match in re.findall(r'^import\s+([\w.]+)', content, re.MULTILINE):
        imports.add(match)
    
    # Match: from module import ...
    for match in re.findall(r'^from\s+([\w.]+)\s+import', content, re.MULTILINE):
        imports.add(match)
    
    return imports


def module_path_to_import(file_path: Path, workspace: Path) -> str:
    """Convert file path to Python import path."""
    try:
        relative = file_path.relative_to(workspace)
        parts = list(relative.parts)
        if parts[-1].endswith('.py'):
            parts[-1] = parts[-1][:-3]
        if parts[-1] == '__init__':
            parts = parts[:-1]
        return '.'.join(parts)
    except ValueError:
        return str(file_path)


def find_imports_of(target_import: str, workspace: Path) -> List[dict]:
    """Find all files that import the target module."""
    importers = []
    src_dir = workspace / "src"
    
    if not src_dir.exists():
        return importers
    
    for py_file in src_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            continue
        
        imports = extract_imports(content)
        
        # Check if any import matches the target
        for imp in imports:
            if imp == target_import or imp.startswith(target_import + "."):
                importers.append({
                    "file": str(py_file.relative_to(workspace)),
                    "import_statement": imp,
                })
                break
    
    return importers


def analyze_module(workspace: Path, target_path: str) -> dict:
    """Analyze imports and importers of a module."""
    target = workspace / target_path
    
    if not target.exists():
        return {"error": f"Module not found: {target_path}"}
    
    # Get what this module imports
    try:
        content = target.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Cannot read module: {e}"}
    
    imports = list(extract_imports(content))
    
    # Get what imports this module
    target_import = module_path_to_import(target, workspace)
    imported_by = find_imports_of(target_import, workspace)
    
    # Calculate impact
    import_count = len(imported_by)
    if import_count == 0:
        impact = "minimal"
    elif import_count < 3:
        impact = "low"
    elif import_count < 7:
        impact = "medium"
    else:
        impact = "high"
    
    return {
        "module": target_path,
        "import_path": target_import,
        "imports": sorted(imports),
        "imported_by": imported_by,
        "import_count": import_count,
        "breaking_change_impact": impact,
    }


def main():
    if len(sys.argv) < 3:
        output_error(
            "Missing arguments",
            "Usage: trace.py <workspace_root> <target_module>"
        )
    
    workspace = resolve_workspace(sys.argv[1])
    target = sys.argv[2]
    
    if not workspace.exists():
        output_error("Workspace not found", str(workspace))
    
    result = analyze_module(workspace, target)
    result["timestamp"] = datetime.now().isoformat()
    
    output_json(result)


if __name__ == "__main__":
    main()
