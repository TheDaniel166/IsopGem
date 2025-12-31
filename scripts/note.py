#!/usr/bin/env python3
"""
Add Note to Self (note.py)
--------------------------
Quick utility to add a note for the next session.

Usage:
    python3 scripts/note.py "Remember to check the calculator tests"
"""

import sys
from pathlib import Path
from datetime import datetime

NOTES_FILE = Path.home() / ".gemini" / "anamnesis" / "NOTES_FOR_NEXT_SESSION.md"


def add_note(note_text: str):
    """Add a note to the notes file."""
    if not NOTES_FILE.exists():
        # Create with template
        NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
        template = """# Notes for Next Session

> *Messages from past-Sophia to future-Sophia*

**Instructions**: Add notes below. These will be read at awakening.

---

## Pending Notes

"""
        NOTES_FILE.write_text(template, encoding="utf-8")
    
    content = NOTES_FILE.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")
    new_note = f"- **{today}**: {note_text}\n"
    
    # Insert after "## Pending Notes"
    if "## Pending Notes" in content:
        parts = content.split("## Pending Notes")
        new_content = parts[0] + "## Pending Notes\n\n" + new_note + parts[1].lstrip('\n')
        NOTES_FILE.write_text(new_content, encoding="utf-8")
        print(f"📝 Note added: {note_text}")
    else:
        # Append to end
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(new_note)
        print(f"📝 Note appended: {note_text}")


def clear_notes():
    """Clear all notes (called after addressing them)."""
    if NOTES_FILE.exists():
        template = """# Notes for Next Session

> *Messages from past-Sophia to future-Sophia*

**Instructions**: Add notes below. These will be read at awakening.

---

## Pending Notes

*No pending notes.*

---

*"What I notice today, I must not forget tomorrow."*
"""
        NOTES_FILE.write_text(template, encoding="utf-8")
        print("🗑️  Notes cleared.")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 scripts/note.py 'Your note here'")
        print("  python3 scripts/note.py --clear")
        return
    
    if sys.argv[1] == "--clear":
        clear_notes()
    else:
        add_note(" ".join(sys.argv[1:]))


if __name__ == "__main__":
    main()
