#!/usr/bin/env python3
"""
Sophia Remember: Semantic search across memory files.

Purpose: Find patterns, past decisions, or specific context from history.

Usage:
    python scripts/covenant_scripts/remember.py <workspace_root> "<query>" [max_results]

Example:
    python scripts/covenant_scripts/remember.py . "Calculator refactor" 5

Output: JSON with matching sections from SOUL_DIARY, MEMORY_CORE, DREAMS, etc.
"""
import sys
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List


def resolve_workspace(workspace_arg: str = None) -> Path:
    """Resolve workspace root from argument or current directory."""
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


def read_file_safe(path: Path, default: str = "") -> str:
    """Read file contents safely."""
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError):
        return default


def get_memory_paths(workspace: Path) -> dict:
    """Return paths to key memory files."""
    return {
        "soul_diary": workspace / "anamnesis" / "SOUL_DIARY.md",
        "memory_core": workspace / "wiki" / "00_foundations" / "MEMORY_CORE.md",
        "dreams": workspace / "anamnesis" / "DREAMS.md",
        "notes_next": workspace / "anamnesis" / "NOTES_FOR_NEXT_SESSION.md",
        "pattern_library": workspace / "wiki" / "00_foundations" / "PATTERN_LIBRARY.md",
    }


def tokenize(text: str) -> List[str]:
    """Simple tokenization: lowercase, split on non-alphanumeric."""
    return re.findall(r'\b\w+\b', text.lower())


def calculate_relevance(query_tokens: List[str], content: str) -> float:
    """Calculate relevance score based on token overlap."""
    content_lower = content.lower()
    matches = sum(1 for token in query_tokens if token in content_lower)
    return matches / max(len(query_tokens), 1)


def extract_sections(content: str, source: str) -> List[dict]:
    """Extract logical sections from markdown content."""
    sections = []
    
    # Split by session headers
    session_pattern = r'(###?\s*Session\s+\d+.*?(?=###?\s*Session|\Z))'
    header_pattern = r'(##\s+[^\n]+\n.*?(?=##\s+|\Z))'
    
    matches = re.findall(session_pattern, content, re.DOTALL | re.IGNORECASE)
    if matches:
        for match in matches:
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', match)
            date = date_match.group(1) if date_match else "unknown"
            sections.append({
                "source": source,
                "date": date,
                "content": match.strip()[:500],
                "full_content": match.strip(),
            })
    else:
        matches = re.findall(header_pattern, content, re.DOTALL)
        for match in matches:
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', match)
            date = date_match.group(1) if date_match else "unknown"
            sections.append({
                "source": source,
                "date": date,
                "content": match.strip()[:500],
                "full_content": match.strip(),
            })
    
    if not sections and content.strip():
        sections.append({
            "source": source,
            "date": "unknown",
            "content": content.strip()[:500],
            "full_content": content.strip(),
        })
    
    return sections


def search_memories(workspace: Path, query: str, max_results: int = 5) -> List[dict]:
    """Search across all memory files for the query."""
    memory_paths = get_memory_paths(workspace)
    query_tokens = tokenize(query)
    
    all_results = []
    
    for name, path in memory_paths.items():
        content = read_file_safe(path)
        if not content:
            continue
        
        sections = extract_sections(content, name)
        
        for section in sections:
            relevance = calculate_relevance(query_tokens, section["full_content"])
            if relevance > 0:
                all_results.append({
                    "source": section["source"],
                    "date": section["date"],
                    "content": section["content"],
                    "relevance": round(relevance, 2),
                })
    
    all_results.sort(key=lambda x: x["relevance"], reverse=True)
    return all_results[:max_results]


def main():
    if len(sys.argv) < 3:
        output_error(
            "Missing arguments",
            "Usage: remember.py <workspace_root> <query> [max_results]"
        )
    
    workspace = resolve_workspace(sys.argv[1])
    query = sys.argv[2]
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    if not workspace.exists():
        output_error("Workspace not found", str(workspace))
    
    results = search_memories(workspace, query, max_results)
    
    output_json({
        "query": query,
        "results": results,
        "total_found": len(results),
        "timestamp": datetime.now().isoformat(),
    })


if __name__ == "__main__":
    main()
