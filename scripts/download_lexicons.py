#!/usr/bin/env python3
"""
Download Greek and Hebrew lexicon data for offline use.

Downloads:
1. Strong's Greek Dictionary (5,500 entries)
2. Strong's Hebrew Dictionary (8,600 entries)
3. Perseus Liddell-Scott Greek-English Lexicon (116,000 entries)

Total size: ~50 MB
License: Public Domain / CC BY-SA
"""
import json
import logging
import urllib.request
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Target directory
LEXICON_DIR = Path(__file__).parent.parent / "data" / "lexicons"
LEXICON_DIR.mkdir(parents=True, exist_ok=True)


def download_strongs_greek():
    """Download Strong's Greek Dictionary from public domain source."""
    logger.info("Downloading Strong's Greek Dictionary...")

    # Using BibleHub public domain data
    url = "https://raw.githubusercontent.com/morphgnt/strongs-dictionary-xml/master/strongsgreek.xml"
    output_file = LEXICON_DIR / "strongs_greek.xml"

    try:
        urllib.request.urlretrieve(url, output_file)
        logger.info(f"✓ Downloaded Strong's Greek to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to download Strong's Greek: {e}")
        logger.info("You can manually download from: https://github.com/morphgnt/strongs-dictionary-xml")
        return False


def download_strongs_hebrew():
    """Download Strong's Hebrew Dictionary from public domain source."""
    logger.info("Downloading Strong's Hebrew Dictionary...")

    # Try OpenScriptures Hebrew lexicon
    url = "https://raw.githubusercontent.com/openscriptures/HebrewLexicon/master/HebrewStrong.xml"
    output_file = LEXICON_DIR / "strongs_hebrew.xml"

    try:
        urllib.request.urlretrieve(url, output_file)
        logger.info(f"✓ Downloaded Strong's Hebrew to {output_file}")
        return True
    except Exception as e:
        # Try alternate STEPBible source
        try:
            logger.info("Trying alternate source (STEPBible)...")
            url = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/master/TOTHT%20-%20Translators%20OT%20Hebrew%20Tagged%20text%20-%20STEPBible.org%20CC%20BY.txt"
            # This is a tagged text, not ideal but let's try JSON source instead
            url = "https://raw.githubusercontent.com/eliranwong/OpenHebrewBible/master/lexicon/BDB_lexicon.json"
            output_file = LEXICON_DIR / "strongs_hebrew.json"
            urllib.request.urlretrieve(url, output_file)
            logger.info(f"✓ Downloaded Hebrew lexicon (BDB) to {output_file}")
            return True
        except Exception as e2:
            logger.error(f"Failed to download Strong's Hebrew: {e2}")
            logger.info("Manual download: https://github.com/openscriptures/HebrewLexicon")
            return False


def download_perseus_lexicon():
    """Download Perseus Liddell-Scott Greek-English Lexicon."""
    logger.info("Downloading Perseus Liddell-Scott Lexicon...")
    logger.info("(This is large - ~30 MB, may take a minute...)")

    url = "https://raw.githubusercontent.com/PerseusDL/lexica/master/CTS_XML_TEI/perseus/pdllex/grc/lsj/grc.lsj.perseus-eng1.xml"
    output_file = LEXICON_DIR / "perseus_lsj.xml"

    try:
        urllib.request.urlretrieve(url, output_file)
        logger.info(f"✓ Downloaded Perseus LSJ to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to download Perseus: {e}")
        return False


def parse_strongs_to_json():
    """Parse Strong's XML files to JSON for faster lookups."""
    logger.info("Converting Strong's dictionaries to JSON...")

    # Greek
    greek_xml = LEXICON_DIR / "strongs_greek.xml"
    if greek_xml.exists():
        try:
            tree = ET.parse(greek_xml)
            root = tree.getroot()

            entries = []
            for entry in root.findall(".//entry"):
                # Get the <greek> element which has unicode, translit as attributes
                greek_elem = entry.find('greek')
                pronunciation_elem = entry.find('pronunciation')

                if greek_elem is not None:
                    word = greek_elem.get('unicode', '')
                    translit = greek_elem.get('translit', '')
                else:
                    word = ''
                    translit = ''

                pronunciation = pronunciation_elem.get('strongs', '') if pronunciation_elem is not None else ''

                # Get definition and derivation
                def_elem = entry.find('strongs_def')
                deriv_elem = entry.find('strongs_derivation')

                definition = ''.join(def_elem.itertext()).strip() if def_elem is not None else ''
                derivation = ''.join(deriv_elem.itertext()).strip() if deriv_elem is not None else ''

                entries.append({
                    'strongs': entry.get('strongs', ''),
                    'word': word,
                    'translit': translit,
                    'pronunciation': pronunciation,
                    'definition': definition,
                    'derivation': derivation
                })

            output = LEXICON_DIR / "strongs_greek.json"
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ Converted {len(entries)} Greek entries to JSON")
        except Exception as e:
            logger.error(f"Failed to parse Greek XML: {e}")

    # Hebrew
    hebrew_xml = LEXICON_DIR / "strongs_hebrew.xml"
    if hebrew_xml.exists():
        try:
            tree = ET.parse(hebrew_xml)
            root = tree.getroot()

            entries = []
            # OpenScriptures Hebrew lexicon has different structure
            # Namespace-aware parsing
            ns = {'lex': 'http://openscriptures.github.com/morphhb/namespace'}

            for entry in root.findall('.//lex:entry', ns):
                # Get the <w> element which contains the Hebrew word
                w_elem = entry.find('lex:w', ns)
                if w_elem is None:
                    w_elem = entry.find('w')  # Try without namespace

                if w_elem is not None:
                    word = w_elem.text or ''
                    translit = w_elem.get('xlit', '')
                    pronunciation = w_elem.get('pron', '')
                else:
                    word = ''
                    translit = ''
                    pronunciation = ''

                # Get definition from <meaning> and <usage>
                meaning_elem = entry.find('lex:meaning', ns) or entry.find('meaning')
                usage_elem = entry.find('lex:usage', ns) or entry.find('usage')
                source_elem = entry.find('lex:source', ns) or entry.find('source')

                meaning_text = ''.join(meaning_elem.itertext()).strip() if meaning_elem is not None else ''
                usage_text = usage_elem.text.strip() if usage_elem is not None and usage_elem.text else ''
                source_text = ''.join(source_elem.itertext()).strip() if source_elem is not None else ''

                definition = f"{meaning_text}. Usage: {usage_text}" if meaning_text and usage_text else meaning_text or usage_text

                entries.append({
                    'strongs': entry.get('id', ''),
                    'word': word,
                    'translit': translit,
                    'pronunciation': pronunciation,
                    'definition': definition,
                    'derivation': source_text
                })

            output = LEXICON_DIR / "strongs_hebrew.json"
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ Converted {len(entries)} Hebrew entries to JSON")
        except Exception as e:
            logger.error(f"Failed to parse Hebrew XML: {e}")


def main():
    """Download all lexicon data."""
    logger.info("=" * 60)
    logger.info("IsopGem Lexicon Downloader")
    logger.info("=" * 60)

    success_count = 0

    if download_strongs_greek():
        success_count += 1

    if download_strongs_hebrew():
        success_count += 1

    if download_perseus_lexicon():
        success_count += 1

    # Convert to JSON for faster access
    if success_count > 0:
        parse_strongs_to_json()

    logger.info("=" * 60)
    logger.info(f"Complete! Downloaded {success_count}/3 lexicons")
    logger.info(f"Location: {LEXICON_DIR}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
