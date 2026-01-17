#!/usr/bin/env python3
"""
Sophia Consult: Query covenant rules and architectural decisions.

Purpose: Search covenant scrolls and wiki for relevant rules before making changes.

Usage:
    python scripts/covenant_scripts/consult.py <workspace_root> "<query>" [scope]

Scopes:
    covenant    - wiki/00_foundations/covenant/
    foundations - wiki/00_foundations/
    blueprints  - wiki/01_blueprints/
    pillars     - wiki/02_pillars/
    all         - Entire wiki/

Example:
    python scripts/covenant_scripts/consult.py . "pillar sovereignty" covenant
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


def get_scope_paths(workspace: Path, scope: str) -> List[Path]:
    """Get paths to search based on scope."""
    wiki = workspace / "wiki"
    
    scope_map = {
        "covenant": [wiki / "00_foundations" / "covenant"],
        "foundations": [wiki / "00_foundations"],
        "blueprints": [wiki / "01_blueprints"],
        "pillars": [wiki / "02_pillars"],
        "all": [wiki],
    }
    
    return scope_map.get(scope, scope_map["all"])


def tokenize(text: str) -> List[str]:
    """Tokenize text for search."""
    return re.findall(r'\b\w+\b', text.lower())


def calculate_relevance(query_tokens: List[str], content: str) -> float:
    """Calculate relevance score."""
    content_lower = content.lower()
    matches = sum(1 for token in query_tokens if token in content_lower)
    return matches / max(len(query_tokens), 1)


def extract_sections(content: str, source: str) -> List[dict]:
    """Extract markdown sections."""
    sections = []
    header_pattern = r'(##\s+[^\n]+\n.*?(?=##\s+|\Z))'
    
    matches = re.findall(header_pattern, content, re.DOTALL)
    for match in matches:
        # Extract section title
        title_match = re.match(r'##\s+(.+)\n', match)
        title = title_match.group(1).strip() if title_match else "Untitled"
        sections.append({
            "source": source,
            "section": title,
            "content": match.strip()[:500],
            "full_content": match.strip(),
        })
    
    if not sections and content.strip():
        sections.append({
            "source": source,
            "section": "Full Document",
            "content": content.strip()[:500],
            "full_content": content.strip(),
        })
    
    return sections


def search_wiki(workspace: Path, query: str, scope: str, max_results: int = 10) -> List[dict]:
    """Search wiki files for the query."""
    query_tokens = tokenize(query)
    all_results = []
    
    for base_path in get_scope_paths(workspace, scope):
        if not base_path.exists():
            continue
        
        for md_file in base_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue
            
            source = md_file.stem
            sections = extract_sections(content, source)
            
            for section in sections:
                relevance = calculate_relevance(query_tokens, section["full_content"])
                if relevance > 0:
                    all_results.append({
                        "source": section["source"],
                        "section": section["section"],
                        "content": section["content"],
                        "relevance": round(relevance, 2),
                    })
    
    all_results.sort(key=lambda x: x["relevance"], reverse=True)
    return all_results[:max_results]


def main():
    if len(sys.argv) < 3:
        output_error(
            "Missing arguments",
            "Usage: consult.py <workspace_root> <query> [scope]"
        )
    
    workspace = resolve_workspace(sys.argv[1])
    query = sys.argv[2]
    scope = sys.argv[3] if len(sys.argv) > 3 else "all"
    
    if not workspace.exists():
        output_error("Workspace not found", str(workspace))
    
    results = search_wiki(workspace, query, scope)
    
    output_json({
        "query": query,
        "scope": scope,
        "results": results,
        "total_found": len(results),
        "timestamp": datetime.now().isoformat(),
    })


if __name__ == "__main__":
    main()
