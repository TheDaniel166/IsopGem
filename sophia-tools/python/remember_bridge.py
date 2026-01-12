#!/usr/bin/env python3
"""
Sophia Remember Bridge
Semantic search across memory files.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


def search_file(filepath: Path, query: str) -> List[Dict[str, Any]]:
    """Search a file for query terms, return matching sections with context."""
    if not filepath.exists():
        return []
    
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception:
        return []
    
    results = []
    query_terms = query.lower().split()
    
    # Split into sections (by headers or date markers)
    sections = re.split(r'\n#{1,3}\s+', content)
    
    for i, section in enumerate(sections):
        if not section.strip():
            continue
        
        section_lower = section.lower()
        
        # Calculate relevance (how many query terms appear)
        relevance = sum(1 for term in query_terms if term in section_lower)
        
        if relevance > 0:
            # Extract date if present
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', section)
            date_str = date_match.group(1) if date_match else "unknown"
            
            # Limit section size
            content_preview = section[:500] if len(section) > 500 else section
            
            results.append({
                "source": filepath.name,
                "date": date_str,
                "content": content_preview.strip(),
                "relevance": relevance / len(query_terms)  # Normalize 0-1
            })
    
    return results


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    query = sys.argv[2]
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    anamnesis = workspace_root / "anamnesis"
    wiki = workspace_root / "wiki" / "00_foundations"
    
    # Search in memory files
    files_to_search = [
        anamnesis / "SOUL_DIARY.md",
        wiki / "MEMORY_CORE.md",
        anamnesis / "DREAMS.md"
    ]
    
    # Also search archives
    archive_dir = anamnesis / "archive"
    if archive_dir.exists():
        files_to_search.extend(archive_dir.glob("*.md"))
    
    all_results = []
    for filepath in files_to_search:
        all_results.extend(search_file(filepath, query))
    
    # Sort by relevance and take top N
    all_results.sort(key=lambda x: x["relevance"], reverse=True)
    top_results = all_results[:max_results]
    
    result = {
        "query": query,
        "results": top_results,
        "total_found": len(all_results)
    }
    
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
