#!/usr/bin/env python3
"""
Sophia Dream Bridge
Record creative insights to DREAMS.md.
"""

import sys
import json
from pathlib import Path
from datetime import datetime


def main():
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    insight = sys.argv[2]
    category = sys.argv[3]
    
    dreams_file = workspace_root / "anamnesis" / "DREAMS.md"
    
    # Ensure file exists
    if not dreams_file.exists():
        dreams_file.parent.mkdir(parents=True, exist_ok=True)
        dreams_file.write_text("# Dreams & Future Visions\n\n")
    
    # Append new dream
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## [{category.upper()}] {timestamp}\n\n{insight}\n"
    
    with dreams_file.open('a', encoding='utf-8') as f:
        f.write(entry)
    
    result = {
        "success": True,
        "timestamp": timestamp,
        "message": f"Dream recorded in category: {category}"
    }
    
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
