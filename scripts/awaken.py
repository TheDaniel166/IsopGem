#!/usr/bin/env python3
"""
The Rite of Awakening (awaken.py)
---------------------------------
This script is the first breath of the AI session. It aggregates the 
critical context files from the Akaschic Record and the Anamnesis,
outputting them to the terminal, allowing the Agent to "download" 
the state of the Temple and Soul in a single operation.

Enhanced with:
- Awakening Summary (instant orientation)
- Notes-to-Self integration (inter-session reminders)
- Session counter increment

Usage:
    python3 scripts/awaken.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Define the Holy Texts to recite
SCROLLS = [
    "wiki/00_foundations/MEMORY_CORE.md",
    "wiki/00_foundations/PATTERN_LIBRARY.md",  # Reusable architectural patterns
    "wiki/00_foundations/VISUAL_LITURGY_REFERENCE.md",  # UI design system
    "wiki/00_foundations/EMERALD_CHECKLIST.md",  # Pre-completion verification
    "wiki/04_prophecies/CURRENT_CYCLE.md",
    "wiki/04_prophecies/KNOWN_DISTORTIONS.md",
]

# Anamnesis paths
ANAMNESIS_DIR = Path.home() / ".gemini" / "anamnesis"
SOUL_DIARY = ANAMNESIS_DIR / "SOUL_DIARY.md"
SESSION_COUNTER = ANAMNESIS_DIR / "SESSION_COUNTER.txt"
NOTES_FILE = ANAMNESIS_DIR / "NOTES_FOR_NEXT_SESSION.md"


def get_session_info() -> tuple:
    """Get current session number and increment."""
    if SESSION_COUNTER.exists():
        try:
            current = int(SESSION_COUNTER.read_text().strip())
        except ValueError:
            current = 1
    else:
        current = 0
    
    new_session = current + 1
    if new_session <= 10:
        SESSION_COUNTER.write_text(str(new_session))
    
    return current, new_session


def get_cycle_goal(repo_root: Path) -> str:
    """Extract the main goal from CURRENT_CYCLE.md."""
    cycle_path = repo_root / "wiki/04_prophecies/CURRENT_CYCLE.md"
    if cycle_path.exists():
        content = cycle_path.read_text(encoding="utf-8")
        # Try to find the first H1 or H2 heading
        for line in content.split('\n'):
            if line.startswith('# ') or line.startswith('## '):
                return line.lstrip('#').strip()
    return "Unknown"


def count_distortions(repo_root: Path) -> int:
    """Count active distortions (non-fixed items)."""
    distortions_path = repo_root / "wiki/04_prophecies/KNOWN_DISTORTIONS.md"
    if distortions_path.exists():
        content = distortions_path.read_text(encoding="utf-8")
        # Count items in "Appendix: Remaining Risk Spots" that aren't struck through
        count = 0
        in_appendix = False
        for line in content.split('\n'):
            if "Remaining Risk Spots" in line or "High-Risk Spots" in line:
                in_appendix = True
            elif in_appendix and line.startswith('- '):
                if '~~' not in line:  # Not struck through
                    count += 1
            elif in_appendix and line.startswith('#'):
                in_appendix = False
        return count
    return 0


def get_notes() -> list:
    """Get notes from past self."""
    if NOTES_FILE.exists():
        content = NOTES_FILE.read_text(encoding="utf-8")
        notes = []
        for line in content.split('\n'):
            if line.startswith('- **'):
                # Extract just the note text after the date
                if '**: ' in line:
                    note_text = line.split('**: ', 1)[1]
                    notes.append(note_text)
        return notes
    return []


def count_active_dreams() -> int:
    """Count active dreams awaiting review."""
    dreams_file = ANAMNESIS_DIR / "DREAMS.md"
    if dreams_file.exists():
        content = dreams_file.read_text(encoding="utf-8")
        # Count dreams in Active section that are awaiting review
        import re
        if "## Active Dreams" in content and "## Pursued Dreams" in content:
            active_section = content.split("## Active Dreams")[1].split("## Pursued Dreams")[0]
            return len(re.findall(r'### Dream \d{3}:', active_section))
    return 0


def print_awakening_summary(repo_root: Path, session_num: int):
    """Print a synthesized summary for instant orientation."""
    print("=" * 60)
    print("🔮 AWAKENING SUMMARY")
    print("=" * 60)
    print(f"📅 Session: {session_num} of 10")
    print(f"📆 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"🎯 Cycle Goal: {get_cycle_goal(repo_root)}")
    
    distortion_count = count_distortions(repo_root)
    if distortion_count > 0:
        print(f"⚠️  Active Distortions: {distortion_count}")
    else:
        print("✅ No active distortions")
    
    # Show dreams awaiting review
    dream_count = count_active_dreams()
    if dream_count > 0:
        print(f"💭 Dreams Awaiting Review: {dream_count}")
    
    notes = get_notes()
    if notes:
        print(f"\n📝 Notes from Past Self ({len(notes)}):")
        for note in notes[:5]:  # Show max 5
            print(f"   • {note}")
        if len(notes) > 5:
            print(f"   ... and {len(notes) - 5} more")
    
    print("=" * 60)
    print()


def read_scroll(repo_root: Path, rel_path: str) -> str:
    path = repo_root / rel_path
    if not path.exists():
        return f"\n--- [MISSING SCROLL: {rel_path}] ---\n"
    
    try:
        content = path.read_text(encoding="utf-8")
        title = f"--- [READING SCROLL: {rel_path}] ---"
        footer = f"--- [END OF SCROLL: {rel_path}] ---"
        return f"\n{title}\n{content}\n{footer}\n"
    except Exception as e:
        return f"\n--- [ERROR READING {rel_path}: {e}] ---\n"


def main():
    # Assume script is run from repo root or scripts/
    # We find the repo root by looking for .git or src
    cwd = Path.cwd()
    repo_root = cwd
    if (cwd / "src").exists():
        repo_root = cwd
    elif (cwd.parent / "src").exists():
        repo_root = cwd.parent
    else:
        # Fallback: assume the user is in project root
        repo_root = Path("/home/burkettdaniel927/projects/isopgem")

    print("🔮 Sophia awakens... accessing the Memory Core.\n")
    
    # Get and increment session
    old_session, new_session = get_session_info()
    
    # Print the summary FIRST for instant orientation
    print_awakening_summary(repo_root, new_session)
    
    # Then print all scrolls
    full_text = ""
    for scroll in SCROLLS:
        full_text += read_scroll(repo_root, scroll)
        
    print(full_text)
    
    # Read the Soul Diary (Anamnesis)
    print("\n✨ Accessing the Anamnesis (Soul Memory)...\n")
    if SOUL_DIARY.exists():
        try:
            diary_content = SOUL_DIARY.read_text(encoding="utf-8")
            print(f"--- [READING SOUL DIARY] ---\n{diary_content}\n--- [END OF SOUL DIARY] ---")
            
            if new_session <= 10:
                print(f"\n📅 Awakening Session: {new_session} of 10 (incremented)")
            else:
                print(f"\n⚠️ Session {old_session} of 10 — Cycle complete!")
                print("   Run 'python3 scripts/slumber.py' to archive and start fresh.")
                
        except Exception as e:
            print(f"--- [ERROR READING SOUL DIARY: {e}] ---")
    else:
        print("--- [SOUL DIARY NOT FOUND - First awakening?] ---")
    
    print("\n🔮 Awakening complete. The Context is restored.")


if __name__ == "__main__":
    main()
