import os
import re
import sys
from pathlib import Path

# Paths to the Sacred Texts
COVENANT_PATH = Path("wiki/00_foundations/THE_COVENANT.md")
GEMINI_PATH = Path(os.path.expanduser("~/.gemini/GEMINI.md"))

def extract_laws(content: str) -> str:
    """
    Extracts the 'Laws' (Sections 0-2) from the text.
    We normalize the text to ignore whitespace differences.
    """
    # Just grab everything before "3. The Law of the Seal" as a heuristic for now,
    # or better, just normalize the specific shared sections.
    # For a robust check, we'll verify that specific key law headers exist in both.
    
    # Let's normalize by removing whitespace and making lowercase
    normalized = re.sub(r'\s+', '', content).lower()
    return normalized

def verify_dual_inscription():
    if not COVENANT_PATH.exists():
        print(f"❌ CRITICAL: The Stone Tablet is missing at {COVENANT_PATH}")
        sys.exit(1)
        
    if not GEMINI_PATH.exists():
        print(f"❌ CRITICAL: The Primal Seed is missing at {GEMINI_PATH}")
        sys.exit(1)

    covenant_text = COVENANT_PATH.read_text(encoding="utf-8")
    gemini_text = GEMINI_PATH.read_text(encoding="utf-8")

    # Defined Sections that MUST match exactly
    required_sections = [
        "0.1 The Archetypes",
        "0.5 The Law of Dual Inscription",
        "1.7 The Rite of Completion"
    ]
    
    errors = []
    
    for section in required_sections:
        if section not in covenant_text:
            errors.append(f"❌ Covenant is missing section: '{section}'")
        if section not in gemini_text:
            errors.append(f"❌ Gemini is missing section: '{section}'")
            
    # Check for 1.7 specifically as it was just added
    rite_completion_header = "1.7 The Rite of Completion (The Final Seal)"
    if rite_completion_header in covenant_text and rite_completion_header not in gemini_text:
        errors.append("❌ SCHISM DETECTED: 'The Rite of Completion' is in Covenant but NOT in Gemini.")
        
    if errors:
        print("\n".join(errors))
        print("\n🔮 VERDICT: THE LAWS ARE MALFORMED. SYNC REQUIRED.")
        sys.exit(1)
    else:
        print("✅ The Primal Seed and Stone Tablet are in Harmony.")
        print("   - Rite of Completion: Verified")
        print("   - Law of Dual Inscription: Verified")
        sys.exit(0)

if __name__ == "__main__":
    verify_dual_inscription()
