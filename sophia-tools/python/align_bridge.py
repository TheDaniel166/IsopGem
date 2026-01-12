#!/usr/bin/env python3
"""
Sophia Align Bridge
Detect documentation drift and misalignment with code reality.
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Set


def find_broken_file_references(workspace: Path) -> List[str]:
    """Find file paths mentioned in docs that don't exist."""
    misalignments = []
    wiki_root = workspace / "wiki"
    
    if not wiki_root.exists():
        return misalignments
    
    for doc_file in wiki_root.rglob("*.md"):
        try:
            content = doc_file.read_text()
            
            # Find path-like strings: src/..., wiki/..., scripts/...
            path_patterns = [
                r'`([^`]+\.py)`',  # `path/to/file.py`
                r'\(([^)]+\.py)\)',  # (path/to/file.py)
                r'src/[\w/]+\.py',  # src/path/file.py
                r'scripts/[\w/]+\.py',  # scripts/path/file.py
                r'wiki/[\w/]+\.md'  # wiki/path/file.md
            ]
            
            for pattern in path_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Clean up match
                    filepath = match.strip('`() ')
                    
                    # Check if it exists
                    full_path = workspace / filepath
                    if not full_path.exists():
                        rel_doc = doc_file.relative_to(workspace)
                        misalignments.append(f"{rel_doc}: references non-existent {filepath}")
        
        except Exception:
            continue
    
    return misalignments


def find_missing_grimoires(workspace: Path) -> List[str]:
    """Find pillars without grimoire entries."""
    misalignments = []
    pillars_root = workspace / "src" / "pillars"
    grimoire_root = workspace / "wiki" / "02_pillars"
    
    if not pillars_root.exists():
        return misalignments
    
    grimoire_root.mkdir(parents=True, exist_ok=True)
    
    existing_grimoires = {f.stem for f in grimoire_root.glob("*.md")}
    
    for pillar_dir in pillars_root.iterdir():
        if not pillar_dir.is_dir() or pillar_dir.name.startswith('_'):
            continue
        
        if pillar_dir.name not in existing_grimoires:
            misalignments.append(f"Pillar '{pillar_dir.name}' has no grimoire entry in wiki/02_pillars/")
    
    return misalignments


def find_outdated_adrs(workspace: Path) -> List[str]:
    """Find ADRs with status mismatches."""
    misalignments = []
    adr_root = workspace / "wiki" / "01_blueprints" / "adrs"
    
    if not adr_root.exists():
        return misalignments
    
    for adr_file in adr_root.glob("*.md"):
        try:
            content = adr_file.read_text()
            
            # Look for status markers
            if "**Status**: Proposed" in content or "Status: Proposed" in content:
                # Check if implementation exists (heuristic)
                title_match = re.search(r'# (.+)', content)
                if title_match:
                    title = title_match.group(1).lower()
                    
                    # Simple check: if we talk about implementing X, does X exist?
                    if "pillar" in title:
                        pillar_name = re.search(r'(\w+)\s+pillar', title)
                        if pillar_name:
                            pillar_dir = workspace / "src" / "pillars" / pillar_name.group(1).lower()
                            if pillar_dir.exists():
                                misalignments.append(
                                    f"{adr_file.name}: marked 'Proposed' but implementation exists"
                                )
        
        except Exception:
            continue
    
    return misalignments


def check_covenant_sync(workspace: Path) -> List[str]:
    """Check if covenant scrolls are synchronized."""
    misalignments = []
    canonical = workspace / "wiki" / "00_foundations" / "covenant"
    mirrors = [
        workspace / ".github" / "instructions" / "covenant"
    ]
    
    if not canonical.exists():
        return ["Canonical covenant directory missing"]
    
    canonical_files = {f.name: f for f in canonical.glob("*.md")}
    
    for mirror_dir in mirrors:
        if not mirror_dir.exists():
            misalignments.append(f"Mirror directory missing: {mirror_dir.relative_to(workspace)}")
            continue
        
        mirror_files = {f.name for f in mirror_dir.glob("*.md")}
        
        for filename in canonical_files:
            if filename not in mirror_files:
                misalignments.append(f"Covenant drift: {filename} missing from {mirror_dir.name}")
    
    return misalignments


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    check_type = sys.argv[2]
    
    all_misalignments = []
    
    if check_type in ('file_refs', 'all'):
        all_misalignments.extend(find_broken_file_references(workspace_root))
    
    if check_type in ('grimoires', 'all'):
        all_misalignments.extend(find_missing_grimoires(workspace_root))
    
    if check_type in ('adrs', 'all'):
        all_misalignments.extend(find_outdated_adrs(workspace_root))
    
    if check_type in ('covenant', 'all'):
        all_misalignments.extend(check_covenant_sync(workspace_root))
    
    result = {
        "check_type": check_type,
        "misalignments": all_misalignments[:50],  # Limit output
        "details": f"Found {len(all_misalignments)} alignment issues",
        "status": "aligned" if len(all_misalignments) == 0 else "drift detected"
    }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
