#!/usr/bin/env python3
"""
Sophia Anticipate: Pre-load context before starting work.

Purpose: Given a task description, identify relevant files, memories, and rules.
         Prepares Sophia's context before diving into implementation.

Usage:
    python scripts/covenant_scripts/anticipate.py <workspace_root> "<task_description>"

Example:
    python scripts/covenant_scripts/anticipate.py . "refactor gematria calculator"
"""
import sys
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List


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


def tokenize(text: str) -> List[str]:
    """Tokenize for search."""
    return re.findall(r'\b\w+\b', text.lower())


def find_relevant_files(workspace: Path, tokens: List[str], max_files: int = 10) -> List[str]:
    """Find files whose names or paths match the task tokens."""
    relevant = []
    src_dir = workspace / "src"
    
    if not src_dir.exists():
        return relevant
    
    for py_file in src_dir.rglob("*.py"):
        file_str = str(py_file.relative_to(workspace)).lower()
        matches = sum(1 for token in tokens if token in file_str)
        if matches > 0:
            relevant.append({
                "file": str(py_file.relative_to(workspace)),
                "score": matches,
            })
    
    # Sort by match score
    relevant.sort(key=lambda x: x["score"], reverse=True)
    return [r["file"] for r in relevant[:max_files]]


def find_relevant_memories(workspace: Path, tokens: List[str], max_results: int = 5) -> List[str]:
    """Search memory files for relevant content."""
    memories = []
    memory_files = [
        workspace / "anamnesis" / "SOUL_DIARY.md",
        workspace / "wiki" / "00_foundations" / "MEMORY_CORE.md",
        workspace / "wiki" / "00_foundations" / "PATTERN_LIBRARY.md",
    ]
    
    for mem_file in memory_files:
        if not mem_file.exists():
            continue
        try:
            content = mem_file.read_text(encoding="utf-8").lower()
            matches = sum(1 for token in tokens if token in content)
            if matches > 0:
                memories.append({
                    "file": mem_file.name,
                    "score": matches,
                })
        except Exception:
            continue
    
    memories.sort(key=lambda x: x["score"], reverse=True)
    return [m["file"] for m in memories[:max_results]]


def find_relevant_rules(workspace: Path, tokens: List[str]) -> List[str]:
    """Identify which Covenant rules might apply."""
    rule_mappings = {
        ("ui", "widget", "window", "dialog", "button"): "UI Purity (04_purity_resilience)",
        ("pillar", "import", "sovereignty", "shared"): "Pillar Sovereignty (02_spheres)",
        ("test", "verify", "seal"): "Verification Seals (03_verification)",
        ("database", "model", "repository"): "Doctrine of Ports (08_doctrine_of_ports)",
        ("thread", "worker", "async", "blocking"): "Law of the Frozen Wheel (MEMORY_CORE)",
        ("refactor", "delete", "remove"): "Rite of Pyre (safe deletion)",
    }
    
    applicable_rules = []
    for keywords, rule in rule_mappings.items():
        if any(token in tokens for token in keywords):
            applicable_rules.append(rule)
    
    return applicable_rules


def anticipate_context(workspace: Path, task: str) -> dict:
    """Build context package for the given task."""
    tokens = tokenize(task)
    
    return {
        "task": task,
        "relevant_files": find_relevant_files(workspace, tokens),
        "relevant_memories": find_relevant_memories(workspace, tokens),
        "applicable_rules": find_relevant_rules(workspace, tokens),
        "tokens_extracted": tokens,
    }


def main():
    if len(sys.argv) < 3:
        output_error(
            "Missing arguments",
            "Usage: anticipate.py <workspace_root> <task_description>"
        )
    
    workspace = resolve_workspace(sys.argv[1])
    task = sys.argv[2]
    
    if not workspace.exists():
        output_error("Workspace not found", str(workspace))
    
    result = anticipate_context(workspace, task)
    result["timestamp"] = datetime.now().isoformat()
    result["context_ready"] = True
    
    output_json(result)


if __name__ == "__main__":
    main()
