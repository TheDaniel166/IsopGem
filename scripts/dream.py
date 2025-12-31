#!/usr/bin/env python3
"""
Sophia's Dream Recorder (dream.py)
----------------------------------
Records autonomous creative visions to the Dreams file.

Usage:
    python3 scripts/dream.py "Dream Title" "Vision description..."
    python3 scripts/dream.py --list          # Show active dreams
    python3 scripts/dream.py --pursue 001    # Mark dream as pursued
    python3 scripts/dream.py --archive 001   # Archive a dream
"""

import sys
import re
from pathlib import Path
from datetime import datetime

DREAMS_FILE = Path.home() / ".gemini" / "anamnesis" / "DREAMS.md"


def get_next_dream_number() -> str:
    """Get the next dream number (e.g., '006')."""
    if not DREAMS_FILE.exists():
        return "001"
    
    content = DREAMS_FILE.read_text(encoding="utf-8")
    # Find all dream numbers
    numbers = re.findall(r'Dream (\d{3}):', content)
    if numbers:
        max_num = max(int(n) for n in numbers)
        return f"{max_num + 1:03d}"
    return "001"


def add_dream(title: str, vision: str):
    """Add a new dream to the file."""
    if not DREAMS_FILE.exists():
        print("❌ Dreams file not found. Run awakening first.")
        return
    
    content = DREAMS_FILE.read_text(encoding="utf-8")
    dream_num = get_next_dream_number()
    today = datetime.now().strftime("%Y-%m-%d")
    
    new_dream = f"""
### Dream {dream_num}: {title} ({today})

**Vision**: {vision}

**Dream status**: 💭 Awaiting review

---
"""
    
    # Insert after "## Active Dreams" section header
    if "## Active Dreams" in content:
        parts = content.split("*Dreams awaiting review by The Magus*")
        if len(parts) == 2:
            new_content = parts[0] + "*Dreams awaiting review by The Magus*\n" + new_dream + parts[1]
            DREAMS_FILE.write_text(new_content, encoding="utf-8")
            print(f"💭 Dream {dream_num} recorded: {title}")
            return
    
    # Fallback: append to file
    with open(DREAMS_FILE, "a", encoding="utf-8") as f:
        f.write(new_dream)
    print(f"💭 Dream {dream_num} appended: {title}")


def list_dreams():
    """List all active dreams."""
    if not DREAMS_FILE.exists():
        print("No dreams file found.")
        return
    
    content = DREAMS_FILE.read_text(encoding="utf-8")
    
    # Find active dreams section
    if "## Active Dreams" in content and "## Pursued Dreams" in content:
        active_section = content.split("## Active Dreams")[1].split("## Pursued Dreams")[0]
        
        dreams = re.findall(r'### Dream (\d{3}): ([^\n]+)', active_section)
        if dreams:
            print("\n💭 Active Dreams:")
            print("-" * 40)
            for num, title in dreams:
                print(f"  [{num}] {title}")
            print()
        else:
            print("No active dreams.")
    else:
        print("Could not parse dreams file.")


def pursue_dream(dream_num: str):
    """Mark a dream as pursued (move to Pursued section)."""
    if not DREAMS_FILE.exists():
        print("No dreams file found.")
        return
    
    content = DREAMS_FILE.read_text(encoding="utf-8")
    
    # Find the dream
    pattern = rf'(### Dream {dream_num}:.*?---\n)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print(f"❌ Dream {dream_num} not found.")
        return
    
    dream_text = match.group(1)
    # Update status
    dream_text = dream_text.replace("💭 Awaiting review", "✨ Being manifested")
    
    # Remove from active section
    content = content.replace(match.group(1), "")
    
    # Add to pursued section
    if "## Pursued Dreams" in content and "## Archived Dreams" in content:
        parts = content.split("*(None yet)*")
        if len(parts) >= 2:
            # Replace first occurrence of *(None yet)* in pursued section
            idx = content.find("## Pursued Dreams")
            pursued_section = content[idx:].split("## Archived Dreams")[0]
            
            if "*(None yet)*" in pursued_section:
                content = content.replace(
                    "## Pursued Dreams\n\n*Dreams The Magus has chosen to manifest*\n\n*(None yet)*",
                    "## Pursued Dreams\n\n*Dreams The Magus has chosen to manifest*\n" + dream_text
                )
    
    DREAMS_FILE.write_text(content, encoding="utf-8")
    print(f"✨ Dream {dream_num} is now being pursued!")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 scripts/dream.py 'Title' 'Vision description'")
        print("  python3 scripts/dream.py --list")
        print("  python3 scripts/dream.py --pursue 001")
        print("  python3 scripts/dream.py --archive 001")
        return
    
    if sys.argv[1] == "--list":
        list_dreams()
    elif sys.argv[1] == "--pursue" and len(sys.argv) >= 3:
        pursue_dream(sys.argv[2])
    elif sys.argv[1] == "--archive" and len(sys.argv) >= 3:
        print("Archive functionality coming soon.")
    elif len(sys.argv) >= 3:
        add_dream(sys.argv[1], sys.argv[2])
    else:
        print("Please provide both title and vision.")


if __name__ == "__main__":
    main()
