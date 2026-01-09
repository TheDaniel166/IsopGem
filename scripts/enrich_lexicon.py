#!/usr/bin/env python3
"""
The Rite of Enrichment
----------------------
A script to automatically populate the Holy Key Lexicon with:
1. Etymologies (via 'ety' library)
2. Definitions (via Free Dictionary API)

This script respects the "Sovereignty" of the Holy Key by only 
enriching keys that have NO existing definitions.

Usage:
    python3 scripts/enrich_lexicon.py --language es --lexicon-languages "Ancient Greek,Hebrew"
"""
import argparse
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import quote

import ety
import requests

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from shared.services.lexicon.holy_key_service import HolyKeyService
from shared.services.lexicon.comprehensive_lexicon_service import ComprehensiveLexiconService
from shared.services.lexicon.language_config import get_language_by_name, get_language_by_slug

def parse_args():
    parser = argparse.ArgumentParser(description="Enrich Holy Key entries with definitions and etymologies.")
    parser.add_argument(
        "-l",
        "--language",
        default="en",
        help="ISO language code for dictionary lookups (e.g., en, es, fr).",
    )
    parser.add_argument(
        "--lexicon-languages",
        default="Ancient Greek,Modern Greek,Hebrew,Ancient Hebrew,English",
        help=(
            "Comma-separated language names to query from local lexicons before hitting the API. "
            "Examples: 'Ancient Greek,Hebrew' or 'English,Spanish'."
        ),
    )
    return parser.parse_args()


def _normalize_language_name(name: str) -> str:
    """Resolve a language name or slug to the canonical display name."""
    clean = name.strip()
    if not clean:
        return ""
    # Try by name first, then slug
    lang = get_language_by_name(clean) or get_language_by_slug(clean)
    return lang.name if lang else clean


def parse_language_list(value: str) -> list[str]:
    """Parse comma-separated languages into a normalized list."""
    parts = [p.strip() for p in value.split(",") if p.strip()]
    return [_normalize_language_name(p) for p in parts]


def _detect_scripts(word: str) -> set[str]:
    """Lightweight script detection for routing lookups."""
    scripts = set()
    for ch in word:
        code = ord(ch)
        if 0x0370 <= code <= 0x03FF or 0x1F00 <= code <= 0x1FFF:
            scripts.add("greek")
        elif 0x0590 <= code <= 0x05FF:
            scripts.add("hebrew")
    if not scripts:
        scripts.add("latin")
    return scripts


def _augment_languages_for_word(word: str, base_languages: list[str]) -> list[str]:
    """Ensure script-specific lexicons (Greek/Hebrew) are included for a word."""
    scripts = _detect_scripts(word)
    extra = []
    if "greek" in scripts:
        extra.extend(["Ancient Greek", "Modern Greek"])
    if "hebrew" in scripts:
        extra.extend(["Hebrew", "Ancient Hebrew"])

    ordered = []
    seen = set()
    for lang in base_languages + extra:
        if lang and lang not in seen:
            ordered.append(lang)
            seen.add(lang)
    return ordered


def fetch_definitions(word: str, language: str) -> list[str]:
    """Fetch definitions from Free Dictionary API for a given language."""
    language_code = language.strip()
    url = f"https://api.dictionaryapi.dev/api/v2/entries/{language_code}/{quote(unicodedata.normalize('NFC', word))}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                # Extract first meaning
                # We could get more, but let's stick to the primary one for now
                meanings = data[0].get('meanings', [])
                defs = []
                for m in meanings:
                    part_of_speech = m.get('partOfSpeech', 'unknown')
                    for d in m.get('definitions', [])[:1]: # Take top def per POS
                        defs.append(f"({part_of_speech}) {d.get('definition')}")
                return defs
        else:
            print(f"  [!] No definitions for '{word}' using language '{language_code}' (status {response.status_code}).")
    except Exception as e:
        print(f"  [!] API Error for '{word}': {e}")
    return []

def get_etymology(word):
    """Fetch etymology using local 'ety' library."""
    try:
        origins = ety.origins(word)
        if origins:
            # Format nicely: "word (lang) < root (lang)"
            return [str(o) for o in origins]
    except Exception as e:
        print(f"  [!] Etymology Error for '{word}': {e}")
    return []

def main():
    args = parse_args()
    service = HolyKeyService()
    lexicon_service = ComprehensiveLexiconService()
    lexicon_languages = parse_language_list(args.lexicon_languages)
    
    print("=== The Rite of Enrichment ===")
    
    # Get target keys
    targets = service.get_undefined_keys()
    total = len(targets)
    print(f"Found {total} keys requiring enrichment.")
    
    if total == 0:
        print("Nothing to do.")
        return

    processed = 0
    enriched = 0
    
    for key_id, word in targets:
        processed += 1
        normalized_word = unicodedata.normalize('NFC', word)
        lookup_languages = _augment_languages_for_word(normalized_word, lexicon_languages)
        print(f"[{processed}/{total}] Enriching '{word}' -> lookup languages: {', '.join(lookup_languages)}")
        
        has_update = False
        
        # 1. Etymology
        etyms = get_etymology(word)
        if etyms:
            content = "Recursive Origins: " + "; ".join(etyms[:3]) # Limit to 3 branches
            service.db.add_definition(key_id, "Etymology", content, source="ety-python")
            print(f"  + Added Etymology")
            has_update = True

        # 2. Local lexicon lookups (Greek/Hebrew/etc.)
        for lang in lookup_languages:
            entries = lexicon_service.lookup(normalized_word, lang)
            for entry in entries:
                segments = [entry.definition]
                if entry.transliteration:
                    segments.append(f"Translit: {entry.transliteration}")
                if entry.etymology:
                    segments.append(f"Etym: {entry.etymology}")
                if entry.morphology:
                    segments.append(entry.morphology)
                content = f"[{entry.language}] " + " | ".join(segments)
                service.db.add_definition(
                    key_id,
                    "Standard",
                    content,
                    source=entry.source or "Comprehensive Lexicon",
                )
                print(f"  + Added Lexicon Definition ({entry.language})")
                has_update = True

        # 3. Definitions via API (language-aware)
        time.sleep(0.5) 
        defs = fetch_definitions(word, args.language)
        for d in defs:
            service.db.add_definition(key_id, "Standard", d, source="FreeDict API")
            print(f"  + Added Definition: {d[:30]}...")
            has_update = True
            
        if has_update:
            enriched += 1
            
    print("-" * 30)
    print(f"Rite Complete.")
    print(f"Processed: {processed}")
    print(f"Enriched: {enriched}")

if __name__ == "__main__":
    main()
