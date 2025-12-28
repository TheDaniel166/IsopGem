#!/usr/bin/env python3
import sys
from pathlib import Path

# Paths to the Sacred Texts
PROJECT_ROOT = Path(__file__).parent.parent  # From workflow_scripts/ to project root
COVENANT_PATH = PROJECT_ROOT / "wiki" / "00_foundations" / "THE_COVENANT.md"
GEMINI_PATH = Path.home() / ".gemini" / "GEMINI.md"

def normalize_text(content: str) -> str:
    """
    Normalize the sacred text for faithful comparison:
    - Remove HTML comment validity headers (they change with time)
    - Strip trailing whitespace from each line
    - Unify line endings to \n
    - Ensure final newline
    """
    lines = content.splitlines()
    cleaned_lines = []
    for line in lines:
        stripped = line.rstrip()
        # Skip validity date comments entirely
        if stripped.startswith("<!-- Last Verified:") and stripped.endswith("-->"):
            continue
        cleaned_lines.append(stripped)
    
    # Join with consistent newline and ensure trailing newline
    return "\n".join(cleaned_lines) + "\n"

def main():
    if not COVENANT_PATH.exists():
        print(f"❌ CRITICAL: The Stone Tablet is absent at {COVENANT_PATH}")
        sys.exit(1)
    
    if not GEMINI_PATH.exists():
        print(f"❌ CRITICAL: The Primal Seed is absent at {GEMINI_PATH}")
        sys.exit(1)
    
    covenant_raw = COVENANT_PATH.read_text(encoding="utf-8")
    gemini_raw = GEMINI_PATH.read_text(encoding="utf-8")
    
    covenant_norm = normalize_text(covenant_raw)
    gemini_norm = normalize_text(gemini_raw)
    
    if covenant_norm == gemini_norm:
        print("✅ The Primal Seed and the Stone Tablet stand in perfect harmony.")
        print("   The Law of Dual Inscription is upheld. Passage granted.")
        sys.exit(0)
    else:
        print("🔴 SCHISM DETECTED: The Laws have diverged.")
        print(f"   Stone Tablet: {COVENANT_PATH}")
        print(f"   Primal Seed:  {GEMINI_PATH}")
        print("\n   Resolve by synchronizing the outdated text (typically GEMINI.md).")
        print("   Then invoke the Sentinel once more.")
        sys.exit(1)

if __name__ == "__main__":
    main()
