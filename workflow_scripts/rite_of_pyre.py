#!/usr/bin/env python3
"""
The Rite of the Pyre - Orphan Detection Script

Searches the wiki/ directory for references to deleted/renamed artifacts.
Reports all locations that need to be burned or updated.

Usage:
    python3 scripts/rite_of_pyre.py <artifact_name> [additional_names...]
    
Examples:
    python3 scripts/rite_of_pyre.py old_calculator.py OldCalculator
    python3 scripts/rite_of_pyre.py legacy_function --check-code
"""
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Set

PROJECT_ROOT = Path(__file__).parent.parent
WIKI_DIR = PROJECT_ROOT / "wiki"
SRC_DIR = PROJECT_ROOT / "src"


def search_wiki(pattern: str) -> List[Tuple[Path, int, str]]:
    """Search wiki/ for a pattern. Returns list of (file, line_num, content)."""
    results = []
    
    for wiki_file in WIKI_DIR.rglob("*.md"):
        try:
            lines = wiki_file.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(lines, 1):
                if pattern.lower() in line.lower():
                    results.append((wiki_file.relative_to(PROJECT_ROOT), i, line.strip()[:80]))
        except Exception:
            pass
    
    return results


def search_code(pattern: str) -> List[Tuple[Path, int, str]]:
    """Search src/ for a pattern (to find remaining code references)."""
    results = []
    
    for py_file in SRC_DIR.rglob("*.py"):
        try:
            lines = py_file.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(lines, 1):
                if pattern in line:  # Case-sensitive for code
                    results.append((py_file.relative_to(PROJECT_ROOT), i, line.strip()[:80]))
        except Exception:
            pass
    
    return results


def check_file_exists(filepath: str) -> bool:
    """Check if a referenced file still exists."""
    # Handle various path formats
    if filepath.startswith("src/"):
        full_path = PROJECT_ROOT / filepath
    elif filepath.startswith("file:///"):
        full_path = Path(filepath.replace("file:///", "/"))
    else:
        full_path = PROJECT_ROOT / "src" / filepath
    
    return full_path.exists()


def detect_orphaned_links() -> List[Tuple[Path, int, str, str]]:
    """Scan wiki for file links pointing to non-existent files."""
    import re
    orphans = []
    
    # Match both file:/// links and plain path links
    # [text](file:///path) or [text](/path) or [text](path)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+\.py(?:#[^)]+)?)\)')
    
    for wiki_file in WIKI_DIR.rglob("*.md"):
        try:
            content = wiki_file.read_text(encoding="utf-8")
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                for match in link_pattern.finditer(line):
                    link_text = match.group(1)
                    raw_path = match.group(2)
                    
                    # Strip line anchors like #L123-L145
                    file_path = raw_path.split('#')[0]
                    
                    # Normalize the path
                    if file_path.startswith('file:///'):
                        resolved = Path(file_path.replace('file:///', '/'))
                    elif file_path.startswith('/'):
                        resolved = Path(file_path)
                    elif file_path.startswith('home/'):
                        # Missing leading slash
                        resolved = Path('/' + file_path)
                    elif file_path.startswith('src/'):
                        # Relative to project root
                        resolved = PROJECT_ROOT / file_path
                    else:
                        # Assume relative to project root
                        resolved = PROJECT_ROOT / file_path
                    
                    if not resolved.exists():
                        orphans.append((
                            wiki_file.relative_to(PROJECT_ROOT),
                            i,
                            link_text,
                            file_path
                        ))
        except Exception:
            pass
    
    return orphans


def main():
    print("=" * 60)
    print("🔥 THE RITE OF THE PYRE - Orphan Detection")
    print("=" * 60)
    print()
    
    check_code = "--check-code" in sys.argv
    patterns = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    
    if not patterns:
        print("Usage: python3 scripts/rite_of_pyre.py <artifact_name> [names...]")
        print("       --check-code  Also search src/ for remaining references")
        print()
        print("Checking for orphaned file links in wiki/...")
        print()
        
        orphans = detect_orphaned_links()
        if orphans:
            print(f"💀 Found {len(orphans)} orphaned link(s):")
            for wiki_file, line_num, link_text, file_path in orphans:
                print(f"   {wiki_file}:{line_num}")
                print(f"      [{link_text}] → {file_path}")
            sys.exit(1)
        else:
            print("✅ No orphaned file links detected.")
            sys.exit(0)
    
    total_ghosts = 0
    
    for pattern in patterns:
        print(f"─" * 40)
        print(f"Searching for: '{pattern}'")
        print(f"─" * 40)
        
        # Search wiki
        wiki_hits = search_wiki(pattern)
        if wiki_hits:
            print(f"\n📜 Wiki References ({len(wiki_hits)} found):")
            for file_path, line_num, content in wiki_hits:
                print(f"   {file_path}:{line_num}")
                print(f"      {content}...")
            total_ghosts += len(wiki_hits)
        else:
            print(f"\n✅ No wiki references found.")
        
        # Optionally search code
        if check_code:
            code_hits = search_code(pattern)
            if code_hits:
                print(f"\n💻 Code References ({len(code_hits)} found):")
                for file_path, line_num, content in code_hits:
                    print(f"   {file_path}:{line_num}")
                    print(f"      {content}...")
                total_ghosts += len(code_hits)
            else:
                print(f"\n✅ No code references found.")
        
        print()
    
    # Also check for orphaned links
    print(f"─" * 40)
    print("Checking for orphaned file links...")
    print(f"─" * 40)
    orphans = detect_orphaned_links()
    if orphans:
        print(f"\n💀 Orphaned Links ({len(orphans)} found):")
        for wiki_file, line_num, link_text, file_path in orphans:
            print(f"   {wiki_file}:{line_num}")
            print(f"      [{link_text}] → (missing)")
        total_ghosts += len(orphans)
    else:
        print("\n✅ No orphaned file links.")
    
    print()
    print("=" * 60)
    if total_ghosts == 0:
        print("✅ THE LIBRARY IS CLEAN. No ghosts detected.")
        sys.exit(0)
    else:
        print(f"🔥 GHOSTS DETECTED: {total_ghosts} reference(s) require burning.")
        print("   Review and remove/update each reference.")
        sys.exit(1)


if __name__ == "__main__":
    main()
