#!/usr/bin/env python3
"""
Comprehensive Kaikki.org Dictionary Downloader

Downloads etymologically significant dictionaries from Kaikki.org for
comprehensive offline word origin analysis.

Categories:
1. Ancient Semitic: Hebrew, Aramaic, Akkadian, Phoenician, Ugaritic, Syriac
2. Ancient Indo-European: Latin, Ancient Greek, Sanskrit, PIE, Avestan
3. Medieval/Classical: Old English, Middle English, Old French, Old Norse, Gothic
4. Modern Major: English, French, German, Spanish, Italian, Russian
5. Other Ancient: Coptic, Egyptian, Sumerian, Hittite
"""
import json
import logging
import urllib.request
import sys
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Target directory
LEXICON_DIR = Path(__file__).parent.parent / "data" / "lexicons"
LEXICON_DIR.mkdir(parents=True, exist_ok=True)

# Base URL for Kaikki dictionaries
KAIKKI_BASE = "https://kaikki.org/dictionary/rawdata/"

# Etymologically significant languages (organized by importance/size)
DICTIONARIES = {
    # ===== TIER 1: Essential Ancient Languages (Already have most) =====
    "core_ancient": [
        ("English", "English", "2.7GB", "Modern reference"),
        ("Latin", "Latin", "1GB", "Classical foundation"),
        ("AncientGreek", "Ancient Greek", "255MB", "Classical/Biblical"),
        ("Hebrew", "Hebrew", "45MB", "Biblical/Semitic"),
        ("Sanskrit", "Sanskrit", "93MB", "Indo-European root"),
        ("Proto-Indo-European", "Proto-Indo-European", "11MB", "IE reconstruction"),
        ("Aramaic", "Aramaic", "3.3MB", "Biblical/Semitic"),
    ],

    # ===== TIER 2: Critical Medieval/Bridge Languages =====
    "medieval_bridge": [
        ("OldEnglish", "Old English", "86K senses", "Anglo-Saxon roots"),
        ("MiddleEnglish", "Middle English", "63K senses", "English bridge"),
        ("OldFrench", "Old French", "11K senses", "Romance bridge"),
        ("Gothic", "Gothic", "25K senses", "Earliest Germanic"),
        ("OldNorse", "Old Norse", "15K senses", "Norse/Viking roots"),
        ("OldHighGerman", "Old High German", "4K senses", "German roots"),
        ("OldIrish", "Old Irish", "8K senses", "Celtic roots"),
        ("OldChurchSlavonic", "Old Church Slavonic", "6K senses", "Slavic liturgical"),
    ],

    # ===== TIER 3: Additional Ancient Semitic & Near Eastern =====
    "ancient_semitic": [
        ("Akkadian", "Akkadian", "2K senses", "Mesopotamian"),
        ("ClassicalSyriac", "Classical Syriac", "8K senses", "Eastern Aramaic"),
        ("Ugaritic", "Ugaritic", "1K senses", "Canaanite"),
        ("Coptic", "Coptic", "4K senses", "Egyptian Christian"),
    ],

    # ===== TIER 4: Other Ancient Indo-European =====
    "ancient_ie": [
        ("OldPersian", "Old Persian", "619 senses", "Ancient Iranian"),
        ("Pali", "Pali", "13K senses", "Buddhist texts"),
        ("Prakrit", "Prakrit", "3K senses", "Middle Indo-Aryan"),
        ("TocharianA", "Tocharian A", "555 senses", "Extinct IE West"),
        ("TocharianB", "Tocharian B", "3K senses", "Extinct IE East"),
        ("MycenaeanGreek", "Mycenaean Greek", "605 senses", "Bronze Age Greek"),
    ],

    # ===== TIER 5: Modern Major Languages (for complete coverage) =====
    "modern_major": [
        ("French", "French", "454K senses", "Modern Romance"),
        ("German", "German", "621K senses", "Modern Germanic"),
        ("Spanish", "Spanish", "859K senses", "Modern Romance"),
        ("Italian", "Italian", "716K senses", "Modern Romance"),
        ("Portuguese", "Portuguese", "502K senses", "Modern Romance"),
        ("Russian", "Russian", "489K senses", "Modern Slavic"),
        ("Greek", "Modern Greek", "112K senses", "Modern Hellenic"),
        ("Arabic", "Arabic", "98K senses", "Modern Semitic"),
        ("Chinese", "Chinese", "377K senses", "Sino-Tibetan"),
        ("Japanese", "Japanese", "226K senses", "Japonic"),
    ],

    # ===== TIER 6: Other Ancient/Classical =====
    "other_ancient": [
        ("Sumerian", "Sumerian", "3K senses", "Ancient Mesopotamian"),
        ("Egyptian", "Egyptian", "8K senses", "Ancient Egyptian"),
        ("Proto-Germanic", "Proto-Germanic", "8K senses", "Germanic reconstruction"),
        ("Proto-Slavic", "Proto-Slavic", "7K senses", "Slavic reconstruction"),
        ("Proto-Celtic", "Proto-Celtic", "2K senses", "Celtic reconstruction"),
    ],
}


def get_file_size(url: str) -> str:
    """Get remote file size without downloading."""
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=10) as response:
            size = int(response.headers.get('Content-Length', 0))
            if size > 1024**3:
                return f"{size / 1024**3:.1f} GB"
            elif size > 1024**2:
                return f"{size / 1024**2:.0f} MB"
            elif size > 1024:
                return f"{size / 1024:.0f} KB"
            else:
                return f"{size} bytes"
    except Exception:
        return "unknown size"


def download_dictionary(code: str, name: str, estimated_size: str) -> bool:
    """Download a single Kaikki dictionary."""
    # Try multiple filename patterns
    patterns = [
        f"kaikki.org-dictionary-{code}.jsonl",
        f"kaikki.org-dictionary-{code}-words.jsonl",
    ]

    for pattern in patterns:
        url = KAIKKI_BASE + pattern
        output_file = LEXICON_DIR / pattern

        # Skip if already exists
        if output_file.exists():
            logger.info(f"✓ {name} already exists ({output_file.name})")
            return True

        try:
            # Check if URL exists
            logger.info(f"Checking {name} at {url}...")
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    # File exists, download it
                    actual_size = get_file_size(url)
                    logger.info(f"Downloading {name} ({actual_size})...")
                    logger.info(f"  URL: {url}")

                    urllib.request.urlretrieve(url, output_file)
                    logger.info(f"✓ Downloaded {name} to {output_file.name}")
                    return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Try next pattern
                continue
            else:
                logger.error(f"HTTP error {e.code} for {name}")
                return False
        except Exception as e:
            logger.debug(f"Failed to download {name} with pattern {pattern}: {e}")
            continue

    logger.warning(f"✗ {name} not found at Kaikki.org (tried {len(patterns)} patterns)")
    return False


def download_tier(tier_name: str, dictionaries: List[tuple], auto_confirm: bool = False) -> int:
    """Download all dictionaries in a tier."""
    logger.info("=" * 70)
    logger.info(f"TIER: {tier_name.upper().replace('_', ' ')}")
    logger.info("=" * 70)

    total_size = sum(
        float(est.replace('GB', '')) * 1024 if 'GB' in est
        else float(est.replace('MB', '').replace('~', '').strip()) if 'MB' in est
        else 0
        for _, _, est, _ in dictionaries
    )

    logger.info(f"Languages in tier: {len(dictionaries)}")
    logger.info(f"Estimated total size: ~{total_size:.0f} MB")
    logger.info("")

    for code, name, size, desc in dictionaries:
        logger.info(f"  • {name:30} {size:15} - {desc}")
    logger.info("")

    if not auto_confirm:
        response = input(f"Download this tier? [y/N]: ").strip().lower()
        if response != 'y':
            logger.info("Skipped tier.\n")
            return 0

    success_count = 0
    for code, name, size, desc in dictionaries:
        if download_dictionary(code, name, size):
            success_count += 1

    logger.info(f"\nTier complete: {success_count}/{len(dictionaries)} downloaded\n")
    return success_count


def main():
    """Download Kaikki dictionaries by tier."""
    logger.info("=" * 70)
    logger.info("IsopGem Comprehensive Kaikki Dictionary Downloader")
    logger.info("=" * 70)
    logger.info(f"Target directory: {LEXICON_DIR}")
    logger.info("")

    # Check command line arguments
    auto_mode = "--auto" in sys.argv or "-y" in sys.argv
    tier_filter = None

    for arg in sys.argv[1:]:
        if arg.startswith("--tier="):
            tier_filter = arg.split("=")[1]

    total_downloaded = 0

    # Display tier summary
    logger.info("Available tiers:")
    for i, (tier_name, dicts) in enumerate(DICTIONARIES.items(), 1):
        logger.info(f"  {i}. {tier_name:25} - {len(dicts):2} languages")
    logger.info("")

    # Download tiers
    for tier_name, dicts in DICTIONARIES.items():
        if tier_filter and tier_filter != tier_name:
            continue

        count = download_tier(tier_name, dicts, auto_confirm=auto_mode)
        total_downloaded += count

    logger.info("=" * 70)
    logger.info(f"Download complete! Total: {total_downloaded} dictionaries")
    logger.info(f"Location: {LEXICON_DIR}")
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. Run: python scripts/build_kaikki_indexes.py")
    logger.info("  2. Update ClassicalLexiconService to add new languages")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
