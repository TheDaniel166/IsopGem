#!/usr/bin/env python3
"""
Sophia Consult Bridge
Query covenant scrolls and wiki documentation.
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any


def search_markdown_file(filepath: Path, query: str) -> List[Dict[str, Any]]:
    """Search a markdown file for query terms, return matching sections."""
    if not filepath.exists():
        return []
    
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception:
        return []
    
    results = []
    query_terms = query.lower().split()
    
    # Split by headers
    sections = re.split(r'\n(#{1,4}\s+.*?)\n', content)
    
    current_header = "Introduction"
    for i in range(0, len(sections), 2):
        if i + 1 < len(sections):
            current_header = sections[i + 1].strip('#').strip()
            section_content = sections[i + 2] if i + 2 < len(sections) else ""
        else:
            section_content = sections[i]
        
        if not section_content.strip():
            continue
        
        section_lower = (current_header + section_content).lower()
        
        # Calculate relevance
        relevance = sum(1 for term in query_terms if term in section_lower)
        
        if relevance > 0:
            # Limit content size
            content_preview = section_content[:600] if len(section_content) > 600 else section_content
            
            results.append({
                "source": filepath.stem,
                "section": current_header,
                "content": content_preview.strip(),
                "relevance": relevance / len(query_terms)
            })
    
    return results


def get_scope_paths(workspace: Path, scope: str) -> List[Path]:
    """Get file paths based on scope."""
    wiki = workspace / "wiki"
    
    if scope == "covenant":
        return list((wiki / "00_foundations" / "covenant").glob("*.md"))
    elif scope == "foundations":
        return list((wiki / "00_foundations").glob("*.md"))
    elif scope == "blueprints":
        return list((wiki / "01_blueprints").rglob("*.md"))
    elif scope == "pillars":
        return list((wiki / "02_pillars").rglob("*.md"))
    else:  # all
        return list(wiki.rglob("*.md"))


def main():
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    query = sys.argv[2]
    scope = sys.argv[3]
    
    # Get files to search based on scope
    files_to_search = get_scope_paths(workspace_root, scope)
    
    all_results = []
    for filepath in files_to_search:
        all_results.extend(search_markdown_file(filepath, query))
    
    # Sort by relevance
    all_results.sort(key=lambda x: x["relevance"], reverse=True)
    
    # Take top 10 results
    top_results = all_results[:10]
    
    result = {
        "query": query,
        "scope": scope,
        "results": top_results,
        "total_found": len(all_results)
    }
    
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
