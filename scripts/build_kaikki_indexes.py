#!/usr/bin/env python3
"""
Build compact Kaikki indexes for fast offline lookup.

Outputs per language (under data/lexicons/indexes/):
- kaikki-<slug>-mini.jsonl : minimal entry rows (one JSON per line)
- kaikki-<slug>-index.json : key -> byte offset into mini file

Keys include exact, lowercase, accent-stripped, and hyphen-stripped variants.
"""
import json
import logging
import unicodedata
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
LEX_DIR = ROOT / "data" / "lexicons"
INDEX_DIR = LEX_DIR / "indexes"
INDEX_DIR.mkdir(parents=True, exist_ok=True)

LANGS = [
    # Core ancient (already have)
    {"name": "English", "slug": "english", "source": "kaikki.org-dictionary-English.jsonl"},
    {"name": "Latin", "slug": "latin", "source": "kaikki.org-dictionary-Latin.jsonl"},
    {"name": "Ancient Greek", "slug": "ancient-greek", "source": "kaikki.org-dictionary-AncientGreek.jsonl"},
    {"name": "Hebrew", "slug": "hebrew", "source": "kaikki.org-dictionary-Hebrew.jsonl"},
    {"name": "Sanskrit", "slug": "sanskrit", "source": "kaikki.org-dictionary-Sanskrit.jsonl"},
    {"name": "Proto-Indo-European", "slug": "pie", "source": "kaikki.org-dictionary-Proto-Indo-European.jsonl"},
    {"name": "Aramaic", "slug": "aramaic", "source": "kaikki.org-dictionary-Aramaic.jsonl"},

    # Medieval/Bridge languages
    {"name": "Old English", "slug": "old-english", "source": "kaikki.org-dictionary-OldEnglish.jsonl"},
    {"name": "Middle English", "slug": "middle-english", "source": "kaikki.org-dictionary-MiddleEnglish.jsonl"},
    {"name": "Old French", "slug": "old-french", "source": "kaikki.org-dictionary-OldFrench.jsonl"},
    {"name": "Gothic", "slug": "gothic", "source": "kaikki.org-dictionary-Gothic.jsonl"},
    {"name": "Old Norse", "slug": "old-norse", "source": "kaikki.org-dictionary-OldNorse.jsonl"},
    {"name": "Old High German", "slug": "old-high-german", "source": "kaikki.org-dictionary-OldHighGerman.jsonl"},
    {"name": "Old Irish", "slug": "old-irish", "source": "kaikki.org-dictionary-OldIrish.jsonl"},
    {"name": "Old Church Slavonic", "slug": "old-church-slavonic", "source": "kaikki.org-dictionary-OldChurchSlavonic.jsonl"},

    # Ancient Semitic
    {"name": "Akkadian", "slug": "akkadian", "source": "kaikki.org-dictionary-Akkadian.jsonl"},
    {"name": "Classical Syriac", "slug": "classical-syriac", "source": "kaikki.org-dictionary-ClassicalSyriac.jsonl"},
    {"name": "Ugaritic", "slug": "ugaritic", "source": "kaikki.org-dictionary-Ugaritic.jsonl"},
    {"name": "Coptic", "slug": "coptic", "source": "kaikki.org-dictionary-Coptic.jsonl"},

    # Ancient Indo-European
    {"name": "Old Persian", "slug": "old-persian", "source": "kaikki.org-dictionary-OldPersian.jsonl"},
    {"name": "Pali", "slug": "pali", "source": "kaikki.org-dictionary-Pali.jsonl"},
    {"name": "Prakrit", "slug": "prakrit", "source": "kaikki.org-dictionary-Prakrit.jsonl"},
    {"name": "Tocharian A", "slug": "tocharian-a", "source": "kaikki.org-dictionary-TocharianA.jsonl"},
    {"name": "Tocharian B", "slug": "tocharian-b", "source": "kaikki.org-dictionary-TocharianB.jsonl"},
    {"name": "Mycenaean Greek", "slug": "mycenaean-greek", "source": "kaikki.org-dictionary-MycenaeanGreek.jsonl"},

    # Modern major languages
    {"name": "French", "slug": "french", "source": "kaikki.org-dictionary-French.jsonl"},
    {"name": "German", "slug": "german", "source": "kaikki.org-dictionary-German.jsonl"},
    {"name": "Spanish", "slug": "spanish", "source": "kaikki.org-dictionary-Spanish.jsonl"},
    {"name": "Italian", "slug": "italian", "source": "kaikki.org-dictionary-Italian.jsonl"},
    {"name": "Portuguese", "slug": "portuguese", "source": "kaikki.org-dictionary-Portuguese.jsonl"},
    {"name": "Russian", "slug": "russian", "source": "kaikki.org-dictionary-Russian.jsonl"},
    {"name": "Modern Greek", "slug": "modern-greek", "source": "kaikki.org-dictionary-Greek.jsonl"},
    {"name": "Arabic", "slug": "arabic", "source": "kaikki.org-dictionary-Arabic.jsonl"},
    {"name": "Chinese", "slug": "chinese", "source": "kaikki.org-dictionary-Chinese.jsonl"},
    {"name": "Japanese", "slug": "japanese", "source": "kaikki.org-dictionary-Japanese.jsonl"},

    # Other ancient & reconstructed
    {"name": "Sumerian", "slug": "sumerian", "source": "kaikki.org-dictionary-Sumerian.jsonl"},
    {"name": "Egyptian", "slug": "egyptian", "source": "kaikki.org-dictionary-Egyptian.jsonl"},
    {"name": "Proto-Germanic", "slug": "proto-germanic", "source": "kaikki.org-dictionary-Proto-Germanic.jsonl"},
    {"name": "Proto-Slavic", "slug": "proto-slavic", "source": "kaikki.org-dictionary-Proto-Slavic.jsonl"},
    {"name": "Proto-Celtic", "slug": "proto-celtic", "source": "kaikki.org-dictionary-Proto-Celtic.jsonl"},
]


def remove_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def romanization_from_forms(forms: List[Dict]) -> str:
    for form in forms:
        if "romanization" in form.get("tags", []):
            return form.get("form", "")
    if forms:
        return forms[0].get("romanization", "")
    return ""


def build_language(lang: Dict[str, str]) -> None:
    name = lang["name"]
    slug = lang["slug"]
    source_path = LEX_DIR / lang["source"]
    mini_path = INDEX_DIR / f"kaikki-{slug}-mini.jsonl"
    index_path = INDEX_DIR / f"kaikki-{slug}-index.json"

    if not source_path.exists():
        logger.warning(f"{name}: source not found at {source_path}")
        return

    logger.info(f"{name}: building compact index")
    logger.info(f"  source : {source_path}")
    logger.info(f"  mini   : {mini_path}")
    logger.info(f"  index  : {index_path}")

    index: Dict[str, int] = {}
    total = 0
    kept = 0

    with open(source_path, "r", encoding="utf-8") as fin, open(mini_path, "w", encoding="utf-8") as fout:
        for line_num, line in enumerate(fin, 1):
            total += 1
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            word = data.get("word", "")
            if not word:
                continue

            forms = data.get("forms", []) or []
            glosses = []
            for sense in (data.get("senses", []) or [])[:10]:
                glosses.extend(sense.get("glosses", []) or [])
            glosses = [g.strip() for g in glosses if g and g.strip()]
            if not glosses:
                continue

            entry = {
                "word": word,
                "language": name,
                "romanization": romanization_from_forms(forms),
                "pos": data.get("pos", "unknown"),
                "glosses": glosses[:8],
                "etymology_text": data.get("etymology_text", ""),
            }

            offset = fout.tell()
            json.dump(entry, fout, ensure_ascii=False)
            fout.write("\n")
            kept += 1

            w_lower = word.lower()
            w_no_accents = remove_accents(w_lower)
            w_no_hyphen = w_no_accents.replace("-", "")
            for key in [word, w_lower, w_no_accents, w_no_hyphen]:
                if key and key not in index:
                    index[key] = offset

            if line_num % 200_000 == 0:
                logger.info(f"  processed {line_num:,} lines (kept {kept:,})")

    with open(index_path, "w", encoding="utf-8") as fidx:
        json.dump(index, fidx, separators=(",", ":"))

    logger.info(f"{name}: done (kept {kept:,} of {total:,} lines)")
    logger.info("")


def main():
    for lang in LANGS:
        build_language(lang)


if __name__ == "__main__":
    main()
