#!/usr/bin/env python3
"""
Sophia Trace Bridge
Analyze dependency relationships in the codebase.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set


def extract_imports(filepath: Path) -> Set[str]:
    """Extract import statements from a Python file."""
    imports = set()
    
    try:
        content = filepath.read_text()
        
        # Match: from X import Y
        from_imports = re.findall(r'from\s+([\w\.]+)', content)
        imports.update(from_imports)
        
        # Match: import X
        direct_imports = re.findall(r'^\s*import\s+([\w\.]+)', content, re.MULTILINE)
        imports.update(direct_imports)
        
    except Exception:
        pass
    
    return imports


def find_dependencies(workspace: Path, target: str) -> List[str]:
    """Find what the target imports (dependencies)."""
    target_path = workspace / target
    
    if not target_path.exists():
        return []
    
    if target_path.is_file():
        files_to_check = [target_path]
    else:
        files_to_check = list(target_path.rglob("*.py"))
    
    all_imports = set()
    for filepath in files_to_check:
        all_imports.update(extract_imports(filepath))
    
    return sorted(list(all_imports))


def find_dependents(workspace: Path, target: str) -> List[str]:
    """Find what imports the target (dependents)."""
    dependents = []
    src_root = workspace / "src"
    
    if not src_root.exists():
        return dependents
    
    # Normalize target to module path
    if target.startswith("src/"):
        target = target[4:]
    
    target_module = target.replace("/", ".").replace(".py", "")
    
    for py_file in src_root.rglob("*.py"):
        try:
            imports = extract_imports(py_file)
            
            # Check if any import mentions the target
            for imp in imports:
                if target_module in imp or target in imp:
                    rel_path = py_file.relative_to(workspace)
                    dependents.append(str(rel_path))
                    break
        except Exception:
            continue
    
    return sorted(dependents)


def build_import_graph(workspace: Path, target: str) -> Dict[str, List[str]]:
    """Build a graph of imports for the target and its neighbors."""
    graph = {}
    target_path = workspace / target
    
    if not target_path.exists():
        return graph
    
    if target_path.is_file():
        files_to_analyze = [target_path]
    else:
        files_to_analyze = list(target_path.rglob("*.py"))[:20]  # Limit to 20 files
    
    for filepath in files_to_analyze:
        rel_path = str(filepath.relative_to(workspace))
        imports = list(extract_imports(filepath))
        if imports:
            graph[rel_path] = imports[:10]  # Limit imports per file
    
    return graph


def main():
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    target = sys.argv[2]
    trace_type = sys.argv[3]
    
    result = {
        "target": target,
        "dependencies": [],
        "dependents": [],
        "import_graph": {}
    }
    
    if trace_type in ('dependencies', 'both'):
        result["dependencies"] = find_dependencies(workspace_root, target)
    
    if trace_type in ('dependents', 'both'):
        result["dependents"] = find_dependents(workspace_root, target)
    
    if trace_type == 'graph':
        result["import_graph"] = build_import_graph(workspace_root, target)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
