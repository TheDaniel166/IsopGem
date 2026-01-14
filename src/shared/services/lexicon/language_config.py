"""
Language configuration for comprehensive lexicon support.

Defines all supported languages with their properties for dynamic loading.
"""
"""
SHARED JUSTIFICATION:
- RATIONALE: Core Infrastructure
- USED BY: Internal shared/ modules only (1 references)
- CRITERION: 2 (Essential for app to function)
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class LanguageConfig:
    """Configuration for a language in the lexicon system."""
    name: str  # Display name (e.g., "Old English")
    slug: str  # Filename slug (e.g., "old-english")
    category: str  # Category for organization
    script: str  # Script type: latin, greek, hebrew, arabic, etc.
    source_file: Optional[str] = None  # Override source filename
    priority: int = 100  # Lower = higher priority in search results


# All supported languages organized by category
LANGUAGE_CONFIGS: List[LanguageConfig] = [
    # ===== CORE ANCIENT LANGUAGES =====
    LanguageConfig("English", "english", "core_ancient", "latin", priority=1),
    LanguageConfig("Latin", "latin", "core_ancient", "latin", priority=2),
    LanguageConfig("Ancient Greek", "ancient-greek", "core_ancient", "greek",
                   source_file="kaikki.org-dictionary-AncientGreek.jsonl", priority=3),
    LanguageConfig("Hebrew", "hebrew", "core_ancient", "hebrew",
                   source_file="kaikki.org-dictionary-Hebrew.jsonl", priority=4),
    LanguageConfig("Sanskrit", "sanskrit", "core_ancient", "devanagari", priority=5),
    LanguageConfig("Proto-Indo-European", "pie", "core_ancient", "latin",
                   source_file="kaikki.org-dictionary-ProtoIndoEuropean.jsonl", priority=6),
    LanguageConfig("Aramaic", "aramaic", "core_ancient", "aramaic", priority=7),

    # ===== MEDIEVAL/BRIDGE LANGUAGES =====
    LanguageConfig("Old English", "old-english", "medieval_bridge", "latin", priority=10),
    LanguageConfig("Middle English", "middle-english", "medieval_bridge", "latin", priority=11),
    LanguageConfig("Old French", "old-french", "medieval_bridge", "latin", priority=12),
    LanguageConfig("Gothic", "gothic", "medieval_bridge", "gothic", priority=13),
    LanguageConfig("Old Norse", "old-norse", "medieval_bridge", "latin", priority=14),
    LanguageConfig("Old High German", "old-high-german", "medieval_bridge", "latin", priority=15),
    LanguageConfig("Old Irish", "old-irish", "medieval_bridge", "latin", priority=16),
    LanguageConfig("Old Church Slavonic", "old-church-slavonic", "medieval_bridge", "cyrillic", priority=17),

    # ===== ANCIENT SEMITIC & NEAR EASTERN =====
    LanguageConfig("Akkadian", "akkadian", "ancient_semitic", "cuneiform", priority=20),
    LanguageConfig("Syriac", "syriac", "ancient_semitic", "syriac", priority=21),
    LanguageConfig("Phoenician", "phoenician", "ancient_semitic", "phoenician", priority=22),
    LanguageConfig("Ugaritic", "ugaritic", "ancient_semitic", "ugaritic", priority=23),
    LanguageConfig("Ancient Hebrew", "ancient-hebrew", "ancient_semitic", "hebrew", priority=24),
    LanguageConfig("Coptic", "coptic", "ancient_semitic", "coptic", priority=25),

    # ===== ANCIENT INDO-EUROPEAN =====
    LanguageConfig("Avestan", "avestan", "ancient_ie", "avestan", priority=30),
    LanguageConfig("Old Persian", "old-persian", "ancient_ie", "cuneiform", priority=31),
    LanguageConfig("Pali", "pali", "ancient_ie", "latin", priority=32),
    LanguageConfig("Prakrit", "prakrit", "ancient_ie", "devanagari", priority=33),
    LanguageConfig("Tocharian A", "tocharian-a", "ancient_ie", "latin", priority=34),
    LanguageConfig("Hittite", "hittite", "ancient_ie", "cuneiform", priority=35),

    # ===== MODERN MAJOR LANGUAGES =====
    LanguageConfig("French", "french", "modern_major", "latin", priority=40),
    LanguageConfig("German", "german", "modern_major", "latin", priority=41),
    LanguageConfig("Spanish", "spanish", "modern_major", "latin", priority=42),
    LanguageConfig("Italian", "italian", "modern_major", "latin", priority=43),
    LanguageConfig("Portuguese", "portuguese", "modern_major", "latin", priority=44),
    LanguageConfig("Russian", "russian", "modern_major", "cyrillic", priority=45),
    LanguageConfig("Modern Greek", "modern-greek", "modern_major", "greek",
                   source_file="kaikki.org-dictionary-Greek.jsonl", priority=46),
    LanguageConfig("Arabic", "arabic", "modern_major", "arabic", priority=47),
    LanguageConfig("Chinese", "chinese", "modern_major", "chinese", priority=48),
    LanguageConfig("Japanese", "japanese", "modern_major", "japanese", priority=49),

    # ===== OTHER ANCIENT =====
    LanguageConfig("Sumerian", "sumerian", "other_ancient", "cuneiform", priority=50),
    LanguageConfig("Egyptian", "egyptian", "other_ancient", "hieroglyphic", priority=51),
    LanguageConfig("Classical Syriac", "classical-syriac", "other_ancient", "syriac", priority=52),
    LanguageConfig("Middle Persian", "middle-persian", "other_ancient", "pahlavi", priority=53),
    LanguageConfig("Elamite", "elamite", "other_ancient", "cuneiform", priority=54),
]


def get_language_by_name(name: str) -> Optional[LanguageConfig]:
    """Get language config by display name."""
    for lang in LANGUAGE_CONFIGS:
        if lang.name.lower() == name.lower():
            return lang
    return None


def get_language_by_slug(slug: str) -> Optional[LanguageConfig]:
    """Get language config by slug."""
    for lang in LANGUAGE_CONFIGS:
        if lang.slug == slug:
            return lang
    return None


def get_languages_by_category(category: str) -> List[LanguageConfig]:
    """Get all languages in a category."""
    return [lang for lang in LANGUAGE_CONFIGS if lang.category == category]


def get_languages_by_script(script: str) -> List[LanguageConfig]:
    """Get all languages using a script."""
    return [lang for lang in LANGUAGE_CONFIGS if lang.script == script]


def get_source_filename(lang: LanguageConfig) -> str:
    """Get the source JSONL filename for a language."""
    if lang.source_file:
        return lang.source_file
    # Default pattern: kaikki.org-dictionary-<TitleCaseSlug>.jsonl
    slug_parts = lang.slug.split('-')
    title_case = ''.join(part.capitalize() for part in slug_parts)
    return f"kaikki.org-dictionary-{title_case}.jsonl"


def get_index_filename_base(lang: LanguageConfig) -> str:
    """Get the base name for index files."""
    return f"kaikki-{lang.slug}"


# Category metadata for UI organization
CATEGORY_METADATA: Dict[str, Dict[str, str]] = {
    "core_ancient": {
        "display_name": "Core Ancient Languages",
        "description": "Essential classical languages for etymology",
        "icon": "🏛️"
    },
    "medieval_bridge": {
        "display_name": "Medieval Bridge Languages",
        "description": "Languages connecting ancient to modern",
        "icon": "🏰"
    },
    "ancient_semitic": {
        "display_name": "Ancient Semitic & Near Eastern",
        "description": "Semitic and ancient Middle Eastern languages",
        "icon": "📜"
    },
    "ancient_ie": {
        "display_name": "Ancient Indo-European",
        "description": "Other ancient Indo-European languages",
        "icon": "🕉️"
    },
    "modern_major": {
        "display_name": "Modern Major Languages",
        "description": "Contemporary widely-spoken languages",
        "icon": "🌍"
    },
    "other_ancient": {
        "display_name": "Other Ancient Languages",
        "description": "Additional ancient and classical languages",
        "icon": "🔱"
    }
}