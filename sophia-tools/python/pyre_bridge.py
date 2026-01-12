#!/usr/bin/env python3
"""
Sophia Pyre Bridge
Archive files/directories before deletion (The Pyre ritual).
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime


def archive_to_pyre(workspace: Path, target_path: str, reason: str) -> dict:
    """Move target to .archive/ with timestamp and log."""
    target = workspace / target_path
    
    if not target.exists():
        return {
            "target": target_path,
            "archived_to": "",
            "reason": reason,
            "status": f"Target '{target_path}' does not exist"
        }
    
    # Create archive directory
    archive_root = workspace / ".archive"
    archive_root.mkdir(exist_ok=True)
    
    # Generate timestamped archive name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_name = target.name
    archive_name = f"{timestamp}_{target_name}"
    archive_dest = archive_root / archive_name
    
    # Move to archive
    try:
        if target.is_dir():
            shutil.copytree(target, archive_dest)
        else:
            shutil.copy2(target, archive_dest)
        
        # Log to PYRE_LOG.md
        pyre_log = archive_root / "PYRE_LOG.md"
        log_entry = f'''
## {timestamp} - {target_name}

**Original Path**: `{target_path}`
**Archived To**: `.archive/{archive_name}`
**Reason**: {reason}

---

'''
        
        if pyre_log.exists():
            existing_content = pyre_log.read_text()
            pyre_log.write_text(log_entry + existing_content)
        else:
            pyre_log.write_text("# Pyre Archive Log\n\n" + log_entry)
        
        return {
            "target": target_path,
            "archived_to": f".archive/{archive_name}",
            "reason": reason,
            "status": f"Successfully archived '{target_path}' to Pyre. Original still exists."
        }
    
    except Exception as e:
        return {
            "target": target_path,
            "archived_to": "",
            "reason": reason,
            "status": f"Failed to archive: {str(e)}"
        }


def main():
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    target_path = sys.argv[2]
    reason = sys.argv[3]
    
    result = archive_to_pyre(workspace_root, target_path, reason)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
