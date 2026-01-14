#!/usr/bin/env python3
"""
Add justification headers to shared/ modules.

This tool helps document the current state of shared/ by adding
SHARED JUSTIFICATION headers to all modules.
"""
import subprocess
from pathlib import Path
from typing import List, Dict

SHARED_DIR = Path("src/shared")


def get_pillar_usage(file_path: Path) -> List[str]:
    """Find which pillars import this module."""
    # Convert file path to import path
    rel_path = file_path.relative_to("src").with_suffix("")
    import_path = str(rel_path).replace("/", ".")
    
    # Search for imports in pillars (multiple patterns)
    try:
        # Pattern 1: from shared.x import ...
        result1 = subprocess.run(
            ["grep", "-r", f"from {import_path}", "src/pillars/", "--include=*.py"],
            capture_output=True,
            text=True
        )
        
        # Pattern 2: import shared.x
        result2 = subprocess.run(
            ["grep", "-r", f"import {import_path}", "src/pillars/", "--include=*.py"],
            capture_output=True,
            text=True
        )
        
        # Combine results
        all_matches = []
        if result1.returncode == 0:
            all_matches.extend(result1.stdout.splitlines())
        if result2.returncode == 0:
            all_matches.extend(result2.stdout.splitlines())
        
        if not all_matches:
            return []
        
        # Extract pillar names from file paths
        pillars = set()
        for line in all_matches:
            if "src/pillars/" in line:
                parts = line.split("src/pillars/")[1].split("/")
                if parts:
                    pillars.add(parts[0].capitalize())
        
        return sorted(list(pillars))
    except Exception:
        return []


def verify_is_contract(file_path: Path) -> bool:
    """Verify a file is truly a contract (schema) and not behavior."""
    try:
        content = file_path.read_text()
        
        # If it has class definitions with methods (beyond __init__), it's likely behavior
        # This is a heuristic: look for "def " that's not __init__ or __repr__ etc
        lines = content.splitlines()
        in_class = False
        has_behavior_methods = False
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith("class "):
                in_class = True
            elif in_class and stripped.startswith("def "):
                # Skip dunder methods and common dataclass methods
                if not any(x in stripped for x in ["__init__", "__repr__", "__str__", "__eq__", "__hash__"]):
                    # Check if it's a property or just a method with logic
                    if "return" in line or "{" in line or "self." in line:
                        has_behavior_methods = True
                        break
        
        return not has_behavior_methods
    except Exception:
        return False


def categorize_file(file_path: Path, pillar_usage: List[str]) -> Dict[str, str]:
    """Determine the appropriate category and criterion for a file."""
    rel_path = str(file_path.relative_to("src/shared"))
    
    # Core Infrastructure (Criterion 2)
    if any(x in rel_path for x in ["database.py", "config.py", "signals/navigation", "errors/", "async_tasks/"]):
        return {
            "rationale": "Core Infrastructure",
            "criterion": "2 (Essential for app to function)",
            "grandfathered": False
        }
    
    # UI Infrastructure (Criterion 2)
    if any(x in rel_path for x in ["ui/theme.py", "ui/kinetic_enforcer.py"]):
        return {
            "rationale": "Core Infrastructure (UI)",
            "criterion": "2 (Essential for app to function)",
            "grandfathered": False
        }
    
    # Ports (Criterion 1)
    if "clock_provider" in rel_path or "ephemeris_provider" in rel_path:
        return {
            "rationale": "Port (Boundary abstraction)",
            "criterion": "1 (Cross-pillar infrastructure port)",
            "grandfathered": False
        }
    
    # Gematria - Domain logic but cross-pillar (Grandfathered)
    if "services/gematria/" in rel_path:
        if "base_calculator" in rel_path:
            return {
                "rationale": "Contract (Gematria calculator protocol)",
                "criterion": "4 (Shared data contract)",
                "grandfathered": False
            }
        else:
            return {
                "rationale": "Domain Logic (GRANDFATHERED - pending refactor)",
                "criterion": "Violation (Domain algorithms in shared)",
                "grandfathered": True
            }
    
    # Geometry - Single pillar domain logic (Grandfathered)
    if "services/geometry/" in rel_path:
        if "payload" in rel_path or "property" in rel_path or "constants" in rel_path:
            # Verify it's truly a contract
            if verify_is_contract(file_path):
                return {
                    "rationale": "Contract (Geometry DTOs)",
                    "criterion": "4 (Shared data contract)",
                    "grandfathered": False
                }
            else:
                return {
                    "rationale": "Contract (NEEDS REVIEW - contains behavior)",
                    "criterion": "4 (Shared data contract) - verify no logic",
                    "grandfathered": True
                }
        else:
            return {
                "rationale": "Domain Logic (GRANDFATHERED - should move to pillars/geometry)",
                "criterion": "Violation (Single-pillar domain logic)",
                "grandfathered": True
            }
    
    # Lexicon - Single pillar domain logic (Grandfathered)
    if "services/lexicon/" in rel_path or "repositories/lexicon/" in rel_path:
        return {
            "rationale": "Domain Logic (GRANDFATHERED - should move to pillars/lexicon)",
            "criterion": "Violation (Single-pillar domain logic)",
            "grandfathered": True
        }
    
    # Document Manager - Could be infrastructure (needs review)
    if "document_manager" in rel_path:
        if "models" in rel_path or "dtos" in rel_path:
            return {
                "rationale": "Contract (Document schemas) - GRANDFATHERED, may be infrastructure",
                "criterion": "4 (Shared data contract) OR 2 (if docs are global infrastructure)",
                "grandfathered": True
            }
        else:
            return {
                "rationale": "GRANDFATHERED - Unclear if infrastructure or pillar",
                "criterion": "2 (if global) OR Violation (if pillar-specific)",
                "grandfathered": True
            }
    
    # Astrology services
    if "astro_glyph" in rel_path or "venus_phenomena" in rel_path:
        return {
            "rationale": "Domain Logic (GRANDFATHERED - should move to pillars/astrology)",
            "criterion": "Violation (Single-pillar domain logic)",
            "grandfathered": True
        }
    
    # TQ services
    if "services/tq/" in rel_path:
        return {
            "rationale": "Domain Logic (GRANDFATHERED - should move to pillars/tq)",
            "criterion": "Violation (Single-pillar domain logic)",
            "grandfathered": True
        }
    
    # Rich text editor - UI component
    if "rich_text_editor" in rel_path:
        return {
            "rationale": "UI Component (GRANDFATHERED - should move to pillars/document_manager)",
            "criterion": "Violation (Single-pillar UI component)",
            "grandfathered": True
        }
    
    # Models
    if "models/" in rel_path:
        return {
            "rationale": "Contract (Data schemas) - GRANDFATHERED",
            "criterion": "4 (Shared data contract) - needs verification",
            "grandfathered": True
        }
    
    # Utils
    if "utils/" in rel_path:
        return {
            "rationale": "Pure Utility (GRANDFATHERED - needs domain-agnostic verification)",
            "criterion": "3 (Pure utility) - verify no domain semantics",
            "grandfathered": True
        }
    
    # Default: Grandfathered unknown
    return {
        "rationale": "GRANDFATHERED - Needs manual review",
        "criterion": "Unknown - requires categorization",
        "grandfathered": True
    }


def generate_header(file_path: Path, pillar_usage: List[str], category: Dict[str, str]) -> str:
    """Generate a justification header for a file."""
    if not pillar_usage:
        used_by = "None detected (possible orphan - consider deletion if truly unused)"
    else:
        used_by = ", ".join(pillar_usage)
    
    header = f'''"""
SHARED JUSTIFICATION:
- RATIONALE: {category["rationale"]}
- USED BY: {used_by}
- CRITERION: {category["criterion"]}
"""
'''
    
    if category["grandfathered"]:
        header = f'''"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: {category["rationale"]}
- USED BY: {used_by}
- CRITERION: {category["criterion"]}

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""
'''
    
    return header


def add_header_to_file(file_path: Path, header: str) -> tuple[bool, bool]:
    """
    Add justification header to a file.
    
    Returns:
        (success, was_skipped): (True, False) if added, (False, True) if skipped, (False, False) if error
    """
    try:
        content = file_path.read_text()
        
        # Skip if already has header
        if "SHARED JUSTIFICATION:" in content:
            return (False, True)  # Skipped
        
        # Find where to insert (after shebang and module docstring if they exist)
        lines = content.splitlines(keepends=True)
        insert_pos = 0
        
        # Skip shebang
        if lines and lines[0].startswith("#!"):
            insert_pos = 1
        
        # Skip existing module docstring if present
        in_docstring = False
        for i in range(insert_pos, min(insert_pos + 10, len(lines))):
            if '"""' in lines[i]:
                if not in_docstring:
                    in_docstring = True
                else:
                    insert_pos = i + 1
                    break
        
        # Insert header
        new_content = "".join(lines[:insert_pos]) + header + "\n" + "".join(lines[insert_pos:])
        file_path.write_text(new_content)
        
        return (True, False)  # Success
    except Exception as e:
        print(f"  ❌ Error adding header: {e}")
        return (False, False)  # Error


def main():
    """Add headers to all shared/ modules."""
    print("🔧 Adding justification headers to shared/ modules...\n")
    
    py_files = [f for f in SHARED_DIR.rglob("*.py") if f.name != "__init__.py"]
    
    added = 0
    skipped = 0
    errors = 0
    
    for py_file in sorted(py_files):
        rel_path = py_file.relative_to(SHARED_DIR)
        print(f"\n📄 Processing: {rel_path}")
        
        # Get pillar usage
        pillars = get_pillar_usage(py_file)
        print(f"   Used by: {', '.join(pillars) if pillars else 'None (possible orphan)'}")
        
        # Categorize
        category = categorize_file(py_file, pillars)
        print(f"   Category: {category['rationale']}")
        
        # Generate and add header
        header = generate_header(py_file, pillars, category)
        
        success, was_skipped = add_header_to_file(py_file, header)
        
        if success:
            added += 1
            print(f"   ✅ Header added")
        elif was_skipped:
            skipped += 1
            print(f"   ⏭️  Skipped (already has header)")
        else:
            errors += 1
    
    print(f"\n\n{'='*60}")
    print(f"✅ Headers added: {added}")
    print(f"⏭️  Skipped (existing): {skipped}")
    print(f"❌ Errors: {errors}")
    print(f"{'='*60}\n")
    
    print("Next: Run audit to verify:")
    print("  python3 scripts/audit_shared_justifications.py")


if __name__ == "__main__":
    main()
