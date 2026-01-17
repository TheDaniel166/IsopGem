from pathlib import Path
import urllib.parse
import sys

LEXICON_DIR = Path("data/lexicons").resolve()
print(f"Checking directory: {LEXICON_DIR}")

code = "Gothic"
safe_code = urllib.parse.quote(code)
filename = f"kaikki.org-dictionary-{safe_code}.jsonl"
target = LEXICON_DIR / filename

print(f"Looking for: {target}")
print(f"Exists? {target.exists()}")

# List actual files to compare
print("\nActual files related to Gothic:")
for f in LEXICON_DIR.glob("*Gothic*"):
    print(f"  {f.name} (len={len(f.name)})")
    if f.name == filename:
        print("  -> EXACT MATCH")
    else:
        print("  -> NO MATCH")
