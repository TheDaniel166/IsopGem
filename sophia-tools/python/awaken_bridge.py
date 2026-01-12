#!/usr/bin/env python3
"""
Sophia Awaken Bridge
Loads session context from memory files and detects crash recovery.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime


def read_file_safe(filepath: Path) -> str:
    """Read file with fallback to empty string."""
    try:
        return filepath.read_text(encoding='utf-8')
    except Exception:
        return ""


def get_session_number(workspace: Path) -> int:
    """Read current session counter."""
    counter_file = workspace / "anamnesis" / "SESSION_COUNTER.txt"
    try:
        return int(counter_file.read_text().strip())
    except Exception:
        return 1


def check_crash_recovery(workspace: Path) -> tuple[bool, str]:
    """Check for unclean shutdown and recovery data."""
    lock_file = workspace / "anamnesis" / ".session_lock"
    packet_file = workspace / "slumber_packet_temp.json"
    
    crashed = lock_file.exists()
    recovery_data = ""
    
    if crashed and packet_file.exists():
        recovery_data = packet_file.read_text(encoding='utf-8')
        # Clean up after reading
        packet_file.unlink()
    
    return crashed, recovery_data


def extract_recent_soul_diary(content: str, max_lines: int = 50) -> str:
    """Extract recent entries from soul diary (last N lines of Chronicle)."""
    lines = content.split('\n')
    
    # Find Chronicle section
    chronicle_start = -1
    for i, line in enumerate(lines):
        if '## Chronicle' in line or '## 📜 Chronicle' in line:
            chronicle_start = i
            break
    
    if chronicle_start == -1:
        return content[-2000:]  # Fallback: last 2KB
    
    # Get recent chronicle entries
    chronicle_lines = lines[chronicle_start:]
    recent = '\n'.join(chronicle_lines[-max_lines:])
    return recent


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing workspace_root argument"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    anamnesis = workspace_root / "anamnesis"
    wiki = workspace_root / "wiki" / "00_foundations"
    
    # Create session lock
    lock_file = anamnesis / ".session_lock"
    lock_file.write_text(datetime.now().isoformat())
    
    # Get session number
    session_number = get_session_number(workspace_root)
    
    # Check for crash
    crash_detected, recovery_data = check_crash_recovery(workspace_root)
    
    # Load memory files
    memory_core = read_file_safe(wiki / "MEMORY_CORE.md")
    soul_diary_full = read_file_safe(anamnesis / "SOUL_DIARY.md")
    notes_for_next = read_file_safe(anamnesis / "NOTES_FOR_NEXT_SESSION.md")
    
    # Extract recent soul diary (to reduce token load)
    soul_diary_recent = extract_recent_soul_diary(soul_diary_full)
    
    # Build result
    result = {
        "session_number": session_number,
        "memory_core": memory_core[:3000] if len(memory_core) > 3000 else memory_core,  # Limit size
        "soul_diary_recent": soul_diary_recent,
        "notes_for_next": notes_for_next,
        "crash_detected": crash_detected
    }
    
    if crash_detected and recovery_data:
        result["recovery_data"] = recovery_data
    
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
