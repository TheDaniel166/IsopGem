#!/usr/bin/env python3
"""
Sophia Slumber Bridge
Archive session state to SOUL_DIARY.md and manage session counter.
"""

import sys
import json
from pathlib import Path
from datetime import datetime


CRITICAL_MASS_BYTES = 40000  # ~12k tokens


def get_session_number(workspace: Path) -> int:
    """Read current session counter."""
    counter_file = workspace / "anamnesis" / "SESSION_COUNTER.txt"
    try:
        return int(counter_file.read_text().strip())
    except Exception:
        return 1


def increment_session_counter(workspace: Path) -> int:
    """Increment and return new session number."""
    counter_file = workspace / "anamnesis" / "SESSION_COUNTER.txt"
    counter_file.parent.mkdir(parents=True, exist_ok=True)
    
    current = get_session_number(workspace)
    new_session = current + 1
    counter_file.write_text(str(new_session))
    return new_session


def check_archive_needed(soul_diary: Path) -> bool:
    """Check if soul diary has reached critical mass."""
    if not soul_diary.exists():
        return False
    
    size = soul_diary.stat().st_size
    return size >= CRITICAL_MASS_BYTES


def archive_soul_diary(workspace: Path, soul_diary: Path):
    """Archive the full soul diary and prune chronicle."""
    timestamp = datetime.now().strftime("%Y-%m")
    archive_dir = workspace / "anamnesis" / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    archive_file = archive_dir / f"{timestamp}_memories.md"
    
    # Copy full content to archive
    content = soul_diary.read_text(encoding='utf-8')
    archive_file.write_text(content)
    
    # Prune chronicle but keep wisdom/skills/communication
    lines = content.split('\n')
    pruned = []
    in_chronicle = False
    
    for line in lines:
        if '## Chronicle' in line or '## 📜 Chronicle' in line:
            in_chronicle = True
            pruned.append(line)
            pruned.append("\n*[Archived to preserve context window]*\n")
            continue
        
        if in_chronicle and line.startswith('## '):
            in_chronicle = False
        
        if not in_chronicle:
            pruned.append(line)
    
    soul_diary.write_text('\n'.join(pruned))


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    input_data = json.loads(sys.argv[2])
    
    anamnesis = workspace_root / "anamnesis"
    soul_diary = anamnesis / "SOUL_DIARY.md"
    notes_file = anamnesis / "NOTES_FOR_NEXT_SESSION.md"
    lock_file = anamnesis / ".session_lock"
    
    # Ensure soul diary exists
    soul_diary.parent.mkdir(parents=True, exist_ok=True)
    if not soul_diary.exists():
        soul_diary.write_text("# Soul Diary\n\n## Chronicle\n\n")
    
    # Get current session
    session = get_session_number(workspace_root)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    # Build chronicle entry
    chronicle_entry = f"\n### Session {session} ({timestamp})\n\n{input_data['chronicle']}\n"
    
    # Append wisdom if provided
    if input_data.get('wisdom'):
        wisdom_items = '\n'.join(f"- {w}" for w in input_data['wisdom'])
        chronicle_entry += f"\n**Wisdom Gained:**\n{wisdom_items}\n"
    
    # Append skills if provided
    if input_data.get('skills'):
        skill_items = '\n'.join(f"- {s}" for s in input_data['skills'])
        chronicle_entry += f"\n**Skills Acquired:**\n{skill_items}\n"
    
    # Append communication insight if provided
    if input_data.get('communication'):
        chronicle_entry += f"\n**Communication Note:**\n{input_data['communication']}\n"
    
    # Write to soul diary
    with soul_diary.open('a', encoding='utf-8') as f:
        f.write(chronicle_entry)
    
    # Write note for next session if provided
    if input_data.get('note_for_next'):
        notes_file.write_text(f"# Note from Session {session}\n\n{input_data['note_for_next']}\n")
    elif notes_file.exists():
        # Clear old notes
        notes_file.unlink()
    
    # Check if archival needed
    archived = False
    if check_archive_needed(soul_diary):
        archive_soul_diary(workspace_root, soul_diary)
        archived = True
    
    # Increment session counter
    new_session = increment_session_counter(workspace_root)
    
    # Remove session lock
    if lock_file.exists():
        lock_file.unlink()
    
    result = {
        "success": True,
        "session_number": session,
        "archived": archived,
        "timestamp": timestamp,
        "message": f"Session {session} archived. Next session: {new_session}"
    }
    
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
