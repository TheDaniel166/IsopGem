#!/usr/bin/env python3
"""
Update shared/ justification headers with corrected usage data.

Uses the verification results from verify_shared_usage.py to update
headers with accurate pillar usage information.
"""
import json
from pathlib import Path
from typing import Dict

# Load verification results
VERIFICATION_FILE = Path("wiki/04_prophecies/shared_usage_verification.json")
verification_data = json.loads(VERIFICATION_FILE.read_text())


def update_header(file_path: Path, usage_data: Dict) -> bool:
    """Update the USED BY field in an existing header."""
    try:
        content = file_path.read_text()
        
        if "SHARED JUSTIFICATION:" not in content:
            print(f"  ⚠️  No header found in {file_path.name}")
            return False
        
        # Extract current header
        lines = content.splitlines()
        
        # Find and update the USED BY line
        updated_lines = []
        for line in lines:
            if "- USED BY:" in line:
                # Replace with correct data
                if usage_data["is_orphan"]:
                    new_line = "- USED BY: NONE (TRUE ORPHAN - safe to delete)"
                elif usage_data["pillars"]:
                    pillars_str = ", ".join(usage_data["pillars"])
                    refs = usage_data["total_references"]
                    new_line = f"- USED BY: {pillars_str} ({refs} references)"
                else:
                    # Used internally but not by pillars
                    refs = usage_data["total_references"]
                    new_line = f"- USED BY: Internal shared/ modules only ({refs} references)"
                
                updated_lines.append(new_line)
            else:
                updated_lines.append(line)
        
        # Write back
        file_path.write_text("\n".join(updated_lines))
        return True
    
    except Exception as e:
        print(f"  ❌ Error updating {file_path.name}: {e}")
        return False


def main():
    """Update all headers with correct usage data."""
    print("🔄 Updating shared/ headers with corrected usage data\n")
    print(f"Source: {VERIFICATION_FILE}\n")
    
    shared_root = Path("src/shared")
    updated = 0
    skipped = 0
    errors = 0
    
    for rel_path, usage_data in sorted(verification_data.items()):
        file_path = shared_root / rel_path
        
        if not file_path.exists():
            print(f"  ⚠️  File not found: {rel_path}")
            skipped += 1
            continue
        
        print(f"📄 {rel_path}")
        
        if usage_data["is_orphan"]:
            print(f"   🗑️  TRUE ORPHAN - marking for deletion")
        elif usage_data["pillars"]:
            print(f"   ✅ {len(usage_data['pillars'])} pillars, {usage_data['total_references']} refs")
        else:
            print(f"   🔗 Internal use only, {usage_data['total_references']} refs")
        
        if update_header(file_path, usage_data):
            updated += 1
        else:
            errors += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Headers updated: {updated}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Errors: {errors}")
    print(f"{'='*60}\n")
    
    print("Next steps:")
    print("  1. Review the 2 true orphans and delete if confirmed")
    print("  2. Run audit: python3 scripts/audit_shared_justifications.py")
    print("  3. Commit the corrected headers\n")


if __name__ == "__main__":
    main()
