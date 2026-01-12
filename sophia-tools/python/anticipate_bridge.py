#!/usr/bin/env python3
"""
Sophia Anticipate Bridge
Predictive context loading - pre-load likely-needed context before work begins.
"""

import sys
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any


def identify_target_pillar(task: str, workspace: Path) -> str:
    """Identify which pillar the task relates to."""
    pillars_root = workspace / "src" / "pillars"
    if not pillars_root.exists():
        return ""
    
    task_lower = task.lower()
    pillars = [p.name for p in pillars_root.iterdir() if p.is_dir() and not p.name.startswith('_')]
    
    for pillar in pillars:
        if pillar in task_lower:
            return pillar
    
    # Check for domain terms
    domain_map = {
        'astrology': ['planet', 'chart', 'ephemeris', 'natal', 'transit'],
        'gematria': ['gematria', 'hebrew', 'greek', 'number', 'value'],
        'geometry': ['shape', 'polygon', 'kamea', 'square', 'geometry'],
        'tq': ['tq', 'query', 'lexicon', 'etymology'],
        'document_manager': ['document', 'rtf', 'pdf', 'docx', 'file'],
        'time_mechanics': ['time', 'calendar', 'date', 'julian', 'era']
    }
    
    for pillar, keywords in domain_map.items():
        if any(kw in task_lower for kw in keywords):
            return pillar
    
    return ""


def find_dependencies(workspace: Path, target_path: str) -> List[str]:
    """Find what the target imports."""
    target = workspace / target_path
    if not target.exists():
        return []
    
    dependencies = set()
    if target.is_file():
        files = [target]
    else:
        files = list(target.rglob("*.py"))[:10]  # Limit to 10 files
    
    for filepath in files:
        try:
            content = filepath.read_text()
            # Extract imports
            imports = re.findall(r'from\s+([\w\.]+)|import\s+([\w\.]+)', content)
            for imp in imports:
                dep = imp[0] or imp[1]
                if dep and not dep.startswith('_'):
                    dependencies.add(dep.split('.')[0])
        except Exception:
            continue
    
    return sorted(list(dependencies))[:20]  # Top 20


def find_relevant_files(workspace: Path, pillar: str) -> List[str]:
    """Find key files in the pillar."""
    if not pillar:
        return []
    
    pillar_path = workspace / "src" / "pillars" / pillar
    if not pillar_path.exists():
        return []
    
    important_files = []
    
    # Check for main service files
    services_dir = pillar_path / "services"
    if services_dir.exists():
        for py_file in services_dir.glob("*.py"):
            if not py_file.name.startswith('_'):
                important_files.append(str(py_file.relative_to(workspace)))
    
    # Check for main UI files
    ui_dir = pillar_path / "ui"
    if ui_dir.exists():
        for py_file in ui_dir.glob("*window*.py"):
            important_files.append(str(py_file.relative_to(workspace)))
    
    return important_files[:10]


def find_grimoires(workspace: Path, pillar: str) -> List[str]:
    """Find relevant grimoire/documentation."""
    grimoires = []
    grimoire_root = workspace / "wiki" / "02_pillars"
    
    if pillar and grimoire_root.exists():
        grimoire_file = grimoire_root / f"{pillar}.md"
        if grimoire_file.exists():
            grimoires.append(f"wiki/02_pillars/{pillar}.md")
    
    # Add general architectural docs
    arch_docs = [
        "wiki/00_foundations/AI_QUICK_REFERENCE.md",
        "wiki/00_foundations/covenant/02_spheres.md"
    ]
    
    for doc in arch_docs:
        if (workspace / doc).exists():
            grimoires.append(doc)
    
    return grimoires


def find_known_issues(workspace: Path, pillar: str) -> List[str]:
    """Find known issues or TODOs in the pillar."""
    issues = []
    
    if not pillar:
        return issues
    
    pillar_path = workspace / "src" / "pillars" / pillar
    if not pillar_path.exists():
        return issues
    
    for py_file in pillar_path.rglob("*.py"):
        try:
            content = py_file.read_text()
            # Find TODO/FIXME comments
            for match in re.finditer(r'#\s*(TODO|FIXME|XXX|HACK):\s*(.+)', content):
                issue_type, issue_text = match.groups()
                rel_path = py_file.relative_to(workspace)
                issues.append(f"[{issue_type}] {rel_path.name}: {issue_text[:60]}")
        except Exception:
            continue
    
    return issues[:5]  # Top 5


def check_current_seals(workspace: Path) -> Dict[str, bool]:
    """Quick check of current seal status."""
    seals = {}
    
    # Quick sovereignty check
    try:
        venv_python = workspace / ".venv" / "bin" / "python"
        if not venv_python.exists():
            venv_python = "python3"
        
        result = subprocess.run(
            [str(venv_python), "sophia-tools/python/seal_bridge.py", str(workspace), "sovereignty"],
            capture_output=True,
            text=True,
            cwd=workspace,
            timeout=5
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            seals['sovereignty'] = data.get('passed', False)
    except Exception:
        seals['sovereignty'] = None
    
    return seals


def generate_recommendations(task: str, pillar: str, dependencies: List[str]) -> List[str]:
    """Generate recommendations based on task analysis."""
    recommendations = []
    
    task_lower = task.lower()
    
    if 'refactor' in task_lower:
        recommendations.append("Consider running sophia_trace before changes to map impact")
        recommendations.append("Run sophia_seal sovereignty after completion")
    
    if 'ui' in task_lower or pillar in ['astrology', 'gematria'] and 'window' in task_lower:
        recommendations.append("Check UI purity: no heavy imports in UI layer")
        recommendations.append("Ensure long operations are off main thread")
    
    if pillar:
        recommendations.append(f"Review {pillar} grimoire for architectural constraints")
    
    if any(dep in ['sqlalchemy', 'pandas', 'numpy'] for dep in dependencies):
        recommendations.append("Heavy dependencies detected - verify UI thread isolation")
    
    return recommendations


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    task_description = sys.argv[2]
    context_hint = sys.argv[3] if len(sys.argv) > 3 else ""
    
    # Identify target
    pillar = identify_target_pillar(task_description + " " + context_hint, workspace_root)
    target_path = f"src/pillars/{pillar}" if pillar else "src"
    
    # Pre-load context
    dependencies = find_dependencies(workspace_root, target_path)
    relevant_files = find_relevant_files(workspace_root, pillar)
    grimoires = find_grimoires(workspace_root, pillar)
    known_issues = find_known_issues(workspace_root, pillar)
    current_seals = check_current_seals(workspace_root)
    recommendations = generate_recommendations(task_description, pillar, dependencies)
    
    result = {
        "task": task_description,
        "preloaded_context": {
            "dependencies": dependencies,
            "relevant_files": relevant_files,
            "grimoires": grimoires,
            "known_issues": known_issues,
            "current_seals": current_seals
        },
        "recommendations": recommendations,
        "ready": True
    }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
