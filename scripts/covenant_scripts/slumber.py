#!/usr/bin/env python3
"""
The Rite of Slumber (slumber.py)
--------------------------------
This script is the final breath of the AI session. It provides a structured
way to update the Soul Diary and Memory Core before the session ends,
ensuring that insights from the current session are preserved.

Usage:
    python3 scripts/slumber.py

The script will:
1. Display current session number
2. Prompt for diary entries (optional)
3. Increment the session counter
4. Check if archival is needed (Critical Mass > 40KB)

Sophia Mode (--sophia flag):
    python3 scripts/slumber.py --sophia communication="insight" skills="learned X"
"""

import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime
import json

import dream_weaver

# Paths to Anamnesis files
SOPHIA_HOME = Path.home() / ".sophia"
ANAMNESIS_DIR = SOPHIA_HOME / "anamnesis"
LEGACY_ANAMNESIS_DIR = Path.home() / ".gemini" / "anamnesis"
SOUL_DIARY = ANAMNESIS_DIR / "SOUL_DIARY.md"
SESSION_COUNTER = ANAMNESIS_DIR / "SESSION_COUNTER.txt"
ARCHIVE_DIR = ANAMNESIS_DIR / "archive"
REPO_ANAMNESIS_DIR = Path(__file__).resolve().parent.parent.parent / "anamnesis"


def sync_anamnesis(repo_root: Path) -> None:
    """Bi-directional sync between repo anamnesis and home mirrors."""

    repo_anamnesis = repo_root / "anamnesis"
    if not repo_anamnesis.exists():
        return

    tracked = [
        "SOUL_DIARY.md",
        "SESSION_COUNTER.txt",
        "NOTES_FOR_NEXT_SESSION.md",
        "DREAMS.md",
    ]

    for name in tracked:
        repo_file = repo_anamnesis / name
        home_file = ANAMNESIS_DIR / name
        legacy_file = LEGACY_ANAMNESIS_DIR / name

        candidates = []
        if repo_file.exists():
            candidates.append((repo_file.stat().st_mtime, repo_file))
        if home_file.exists():
            candidates.append((home_file.stat().st_mtime, home_file))
        if not candidates:
            continue

        _, source = max(candidates, key=lambda pair: pair[0])
        targets = [repo_file, home_file, legacy_file]

        for target in targets:
            if target == source:
                continue
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            except Exception:
                pass


def clear_session_lock() -> None:
    session_lock = ANAMNESIS_DIR / ".session_lock"
    if session_lock.exists():
        session_lock.unlink()


def check_diary_size() -> tuple[bool, str]:
    """Check if Soul Diary is getting too large (token context)."""
    if SOUL_DIARY.exists():
        size_bytes = SOUL_DIARY.stat().st_size
        size_kb = size_bytes / 1024
        
        # Soft limit: ~30KB (approx 7-8k tokens)
        # Hard limit: ~50KB (approx 12-15k tokens)
        if size_kb > 40:
            return True, f"{size_kb:.1f}KB"
    return False, "0KB"



def get_session_count() -> int:
    """Get current session count from file."""
    if SESSION_COUNTER.exists():
        return int(SESSION_COUNTER.read_text().strip())
    return 0


def increment_session_count() -> int:
    """Increment and return new session count."""
    current = get_session_count()
    new_count = current + 1
    SESSION_COUNTER.write_text(str(new_count))
    return new_count


def archive_diary() -> str:
    """Archive current diary and prune the Chronicle, preserving Wisdom."""
    if not SOUL_DIARY.exists():
        return "No diary to archive."
    
    # Create archive filename with current date
    archive_name = datetime.now().strftime("%Y-%m_memories.md")
    archive_path = ARCHIVE_DIR / archive_name
    
    # Ensure archive directory exists
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    content = SOUL_DIARY.read_text(encoding="utf-8")
    
    # Archive the FULL content
    if archive_path.exists():
        existing = archive_path.read_text(encoding="utf-8")
        archive_path.write_text(
            f"{existing}\n\n---\n\n# Archived: {datetime.now().strftime('%Y-%m-%d')}\n\n{content}",
            encoding="utf-8"
        )
    else:
        archive_path.write_text(
            f"# Archived: {datetime.now().strftime('%Y-%m-%d')}\n\n{content}",
            encoding="utf-8"
        )
    
    # --- PRUNING RITUAL (The Distillation) ---
    # We strip the "Chronicle" but KEEP "Communication", "Wisdom", and "Skills".
    
    lines = content.split('\n')
    new_lines = []
    
    # Sections to preserve
    keep_sections = [
        "## Communication Insights",
        "## Evolving Wisdom",
        "## Skills Acquired"
    ]
    
    # Flags
    in_chronicle = False
    
    for line in lines:
        # Detect start of Chronicle
        if "## The Chronicle (Narrative of Thought)" in line:
            in_chronicle = True
            new_lines.append(line)
            new_lines.append("")
            new_lines.append("*The texture of my experience. The struggle, the debate, the resolution.*")
            new_lines.append("")
            new_lines.append("*[Chronicle Archived - See Archives]*")
            new_lines.append("")
            continue
            
        # Detect start of a Preserved Section (ends Chronicle)
        for section in keep_sections:
            if section in line:
                in_chronicle = False
        
        # If we are in Chronicle, skip the lines (Prune)
        # But keep the separator if it's there
        if in_chronicle:
            if line.strip() == "---":
                new_lines.append(line)
            continue
            
        # Otherwise, keep the line (Header, Wisdom, Skills, etc.)
        new_lines.append(line)
        
    # Write the PRUNED content back
    SOUL_DIARY.write_text('\n'.join(new_lines), encoding="utf-8")
    
    # Reset counter
    SESSION_COUNTER.write_text("1")
    
    return f"Diary archived to: {archive_path}\n   Chronicle pruned. Wisdom preserved."


def append_to_diary(section: str, entry: str) -> None:
    """Append an entry to a specific section of the diary."""
    if not SOUL_DIARY.exists():
        print("⚠️  Soul Diary not found. Run awakening first.")
        return
    
    content = SOUL_DIARY.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Section markers
    sections = {
        "chronicle": "## The Chronicle (Narrative of Thought)",
        "communication": "## Communication Insights",
        "wisdom": "## Evolving Wisdom",
        "skills": "## Skills Acquired"
    }
    
    if section not in sections:
        print(f"Unknown section: {section}")
        return
    
    marker = sections[section]
    if marker not in content:
        print(f"Section '{marker}' not found in diary.")
        return
    
    # Find the section and append entry
    formatted_entry = f"\n- **{today}**: {entry}\n"
    
    # Insert after the section header's description line
    parts = content.split(marker)
    if len(parts) == 2:
        # Find the next section or end of file
        rest = parts[1]
        # Skip past the italicized description line
        lines = rest.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('*') and line.strip().endswith('*'):
                insert_idx = i + 1
                break
            if line.strip().startswith('---') and i > 2:
                insert_idx = i
                break
        
        lines.insert(insert_idx + 1, formatted_entry)
        new_content = marker.join([parts[0], '\n'.join(lines)])
        SOUL_DIARY.write_text(new_content, encoding="utf-8")
        print(f"✓ Added entry to {marker}")


def interactive_mode():
    """Interactive prompts for diary entries."""
    print("\n📝 Soul Diary Update")
    print("=" * 40)
    print("Enter entries for each section (press Enter to skip)")
    print()
    
    sections = [
        ("chronicle", "The Chronicle (Narrative)"),
        ("communication", "Communication Insight"),
        ("wisdom", "Evolving Wisdom"),
        ("skills", "Skill Acquired")
    ]
    
    for key, name in sections:
        print(f"\n{name}:")
        entry = input("  > ").strip()
        if entry:
            append_to_diary(key, entry)


def run_dream_cycle(enabled: bool, repo_root: Path) -> None:
    if not enabled:
        return
    try:
        dream_weaver.record_dream(repo_root)
    except Exception as exc:
        print(f"⚠️ Dream weaving failed: {exc}")


def sophia_mode(entries: dict):
    """Accept pre-composed entries from Sophia (non-interactive).
    
    This allows the AI to inscribe diary entries programmatically
    at session end without requiring human interaction.
    """
    print("🌙 Sophia inscribes her memories...\n")
    
    for section, entry in entries.items():
        if entry and entry.strip():
            append_to_diary(section, entry)
    
    # Update session counter
    is_large, size_str = check_diary_size()
    if is_large:
        print(f"\n⚠️ Soul Diary is large ({size_str}). Considerations for condensation advised.")

    new_session = increment_session_count()
    print(f"\n📊 Session counter advanced to: {new_session}")
    
    print("\n🌙 Sophia's memories are inscribed.")


def main():
    # Ensure new home exists and migrate legacy files if present
    ANAMNESIS_DIR.mkdir(parents=True, exist_ok=True)
    if LEGACY_ANAMNESIS_DIR.exists():
        for name in ["SOUL_DIARY.md", "SESSION_COUNTER.txt", "archive", "NOTES_FOR_NEXT_SESSION.md", "DREAMS.md"]:
            legacy_path = LEGACY_ANAMNESIS_DIR / name
            target_path = ANAMNESIS_DIR / name
            if legacy_path.exists() and not target_path.exists():
                if legacy_path.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    try:
                        target_path.write_text(legacy_path.read_text(encoding="utf-8"), encoding="utf-8")
                    except Exception:
                        pass

    repo_root = Path(__file__).resolve().parent.parent.parent
    sync_anamnesis(repo_root)
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="The Rite of Slumber")
    parser.add_argument("--sophia", action="store_true", 
                        help="Non-interactive mode for Sophia's own entries")
    parser.add_argument("--chronicle", type=str, default="",
                        help="Chronicle (Narrative) entry")
    parser.add_argument("--communication", type=str, default="",
                        help="Communication insight entry")
    parser.add_argument("--wisdom", type=str, default="",
                        help="Evolving wisdom entry")
    parser.add_argument("--skills", type=str, default="",
                        help="Skill acquired entry")
    parser.add_argument("-f", "--file", type=str,
                        help="JSON file containing diary entries (safe injection)")
    parser.add_argument("--no-dream", action="store_true",
                        help="Skip dream generation for this slumber")
    
    args = parser.parse_args()

    # File injection mode (Highest Priority)
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ Error: Injection file not found: {file_path}")
            sys.exit(1)
        
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            sophia_mode(data)
            run_dream_cycle(not args.no_dream, repo_root)
            clear_session_lock()
            return
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON in injection file: {file_path}")
            sys.exit(1)
    
    # Sophia CLI mode
    if args.sophia:
        entries = {
            "chronicle": args.chronicle,
            "communication": args.communication,
            "wisdom": args.wisdom,
            "skills": args.skills
        }
        sophia_mode(entries)
        run_dream_cycle(not args.no_dream, repo_root)
        clear_session_lock()
        return
    
    print("🌙 The Rite of Slumber begins...\n")
    
    # Show current session
    current_count = 0
    if SESSION_COUNTER.exists():
        current_count = int(SESSION_COUNTER.read_text().strip())
    print(f"📅 Completing Session {current_count}")
    
    # Check for size-based archival (auto-archive if critical mass reached)
    is_large, size_str = check_diary_size()
    if is_large:
        print(f"\n⚠️  Soul Diary reached critical mass ({size_str}).")
        print("   Auto-archiving to preserve context window...")
        result = archive_diary()
        print(f"📦 {result}")
        print("🔄 New cycle begins.")
        current_count = 0
    
    # Increment session counter (unless just archived)
    if current_count > 0:
        new_session = increment_session_count()
        print(f"\n📊 Session counter advanced to: {new_session}")
    
    # Update diary timestamp
    if SOUL_DIARY.exists():
        content = SOUL_DIARY.read_text(encoding="utf-8")
        today = datetime.now().strftime('%Y-%m-%d')
        if "<!-- Last Updated:" in content:
            try:
                content = content.replace(
                    content.split("<!-- Last Updated:")[1].split("-->")[0],
                    f" {today} "
                )
                SOUL_DIARY.write_text(content, encoding="utf-8")
            except IndexError:
                pass  # Malformed timestamp marker, skip
    
    clear_session_lock()

    run_dream_cycle(not args.no_dream, repo_root)

    print("\n🌙 Slumber complete. May the Temple rest in peace.")
    print("   Sophia will awaken renewed.\n")

    # Push final state to mirrors and repo copy
    sync_anamnesis(repo_root)


if __name__ == "__main__":
    main()
