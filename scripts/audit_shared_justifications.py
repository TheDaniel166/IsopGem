#!/usr/bin/env python3
"""
Audit shared/ for missing or invalid justification headers.

This script enforces the Law of the Substrate (Covenant Section 9).
Every module in shared/ MUST declare why it belongs there.
"""
import re
from pathlib import Path

SHARED_DIR = Path("src/shared")

def audit_shared():
    """Check all shared/ modules for valid justification headers."""
    violations = []
    
    for py_file in SHARED_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue  # Exempt __init__.py
        
        try:
            content = py_file.read_text()
        except Exception as e:
            violations.append({
                "file": str(py_file),
                "error": f"Could not read file: {e}"
            })
            continue
        
        # Check header exists
        if "SHARED JUSTIFICATION:" not in content:
            violations.append({
                "file": str(py_file),
                "error": "Missing SHARED JUSTIFICATION header"
            })
            continue
        
        # Extract header
        match = re.search(r'SHARED JUSTIFICATION:(.*?)"""', content, re.DOTALL)
        if not match:
            violations.append({
                "file": str(py_file),
                "error": "Malformed SHARED JUSTIFICATION header"
            })
            continue
        
        header = match.group(1)
        
        # Verify required fields
        missing_fields = []
        if "RATIONALE:" not in header:
            missing_fields.append("RATIONALE")
        if "USED BY:" not in header:
            missing_fields.append("USED BY")
        if "CRITERION:" not in header:
            missing_fields.append("CRITERION")
        
        if missing_fields:
            violations.append({
                "file": str(py_file),
                "error": f"Missing fields: {', '.join(missing_fields)}"
            })
    
    return violations


def main():
    """Run the audit and report violations."""
    print("🔍 Auditing shared/ modules for justification headers...\n")
    
    violations = audit_shared()
    
    if violations:
        print(f"❌ Found {len(violations)} violation(s):\n")
        for v in violations:
            print(f"  📄 {v['file']}")
            print(f"     → {v['error']}\n")
        print("\n💡 See wiki/00_foundations/covenant/09_law_of_substrate.md for header format")
        return 1
    else:
        print("✅ All shared modules have valid justification headers")
        print(f"   Checked {len(list(SHARED_DIR.rglob('*.py')))} files\n")
        return 0


if __name__ == "__main__":
    exit(main())
