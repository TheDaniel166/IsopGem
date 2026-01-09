#!/usr/bin/env python3
"""Test the enhanced verse parser with the actual Liber Spectaculi document."""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from shared.utils.verse_parser import parse_verses

# Sample text from 603 Liber Spectaculi
sample_text = """Μαινας 
Here goes the Madman traipsing across the desert. He follows a butterfly and turns into a caterpillar.
Αγγελικος 
The wings of the butterfly adorn the wand of the Magus. He parts the sea with a wave of his hand.
Αραχνη 
Through the great divide comes the High Priestess to lead the way out of Egypt. She carries the scroll of the ancients in a cylinder made of crystal.
Αρχη Κοσμου 
The message is brought to her Highness by the Angelic One. She reads the letters backwards and Understands.
"""

print("=" * 60)
print("Testing Header-Based Verse Parser")
print("=" * 60)
print()

verses = parse_verses(sample_text)

print(f"Verses detected: {len(verses)}")
print()

for verse in verses:
    header = verse.get('header', 'N/A')
    print(f"Verse {verse['number']}: {header}")
    print(f"  Text: {verse['text'][:60]}...")
    print(f"  Position: {verse['start']}-{verse['end']}")
    print()

print("=" * 60)
print(f"✓ Successfully parsed {len(verses)} verses!")
print("=" * 60)
