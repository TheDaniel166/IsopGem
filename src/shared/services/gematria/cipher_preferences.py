"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: Domain Logic (GRANDFATHERED - pending refactor)
- USED BY: Gematria (2 references)
- CRITERION: Violation (Domain algorithms in shared)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""Cipher preference manager for multi-language gematria calculations.

Allows users to configure which cipher to use for each language.
Preferences are persisted to user settings.
"""

import json
from pathlib import Path
from typing import Dict, Optional, List
from .language_detector import Language


class CipherPreferences:
    """Manages user preferences for gematria ciphers per language."""

    # Default cipher names for each language
    # These match the actual calculator.name values
    DEFAULT_CIPHERS = {
        Language.HEBREW: "Hebrew (Standard)",
        Language.GREEK: "Greek (Isopsephy)",  # Greek standard is called "Isopsephy"
        Language.ENGLISH: "English (TQ)",
        Language.LATIN: "English (TQ)",  # Use English TQ for Latin
        Language.ARABIC: "English (TQ)",  # Fallback until Arabic cipher added
        Language.UNKNOWN: "English (TQ)",  # Default fallback
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize cipher preferences.

        Args:
            config_path: Optional path to config file (defaults to user config dir)
        """
        if config_path is None:
            # Use user's config directory
            config_dir = Path.home() / ".config" / "isopgem"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = config_dir / "cipher_preferences.json"

        self.config_path = config_path
        self._preferences: Dict[str, str] = {}
        self._load_preferences()

    def _load_preferences(self):
        """Load preferences from config file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._preferences = data.get('ciphers', {})
            except Exception:
                # If loading fails, use defaults
                self._preferences = {}

        # Ensure all languages have a default
        for lang in Language:
            lang_key = lang.value
            if lang_key not in self._preferences:
                self._preferences[lang_key] = self.DEFAULT_CIPHERS[lang]

    def _save_preferences(self):
        """Save preferences to config file."""
        try:
            data = {'ciphers': self._preferences}
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cipher preferences: {e}")

    def get_cipher(self, language: Language) -> str:
        """
        Get the preferred cipher name for a language.

        Args:
            language: Language enum

        Returns:
            Cipher name string
        """
        lang_key = language.value
        return self._preferences.get(lang_key, self.DEFAULT_CIPHERS[language])

    def set_cipher(self, language: Language, cipher_name: str):
        """
        Set the preferred cipher for a language.

        Args:
            language: Language enum
            cipher_name: Name of the cipher to use
        """
        lang_key = language.value
        self._preferences[lang_key] = cipher_name
        self._save_preferences()

    def get_all_preferences(self) -> Dict[str, str]:
        """
        Get all cipher preferences.

        Returns:
            Dictionary mapping language names to cipher names
        """
        return self._preferences.copy()

    def reset_to_defaults(self):
        """Reset all preferences to default ciphers."""
        self._preferences = {
            lang.value: default_cipher
            for lang, default_cipher in self.DEFAULT_CIPHERS.items()
        }
        self._save_preferences()

    def get_available_ciphers_for_language(self, language: Language) -> List[str]:
        """
        Get list of available cipher names for a specific language.

        This is a helper method that provides suggested ciphers based on language.
        The actual cipher availability depends on what's loaded in the application.

        Args:
            language: Language enum

        Returns:
            List of suggested cipher names
        """
        cipher_suggestions = {
            Language.HEBREW: [
                "Hebrew (Standard)",
                "Hebrew (Sofit)",
                "Hebrew (Ordinal)",
                "Hebrew (Small Value)",
                "Hebrew (AtBash)",
                "Hebrew (Albam)",
                "Hebrew (Kolel)",
                "Hebrew (Square)",
                "Hebrew (Cube)",
                "Hebrew (Triangular)",
                "Hebrew (Full Value)",
            ],
            Language.GREEK: [
                "Greek (Standard)",
                "Greek (Ordinal)",
                "Greek (Small Value)",
                "Greek (Kolel)",
                "Greek (Square)",
                "Greek (Cube)",
                "Greek (Triangular)",
                "Greek (Full Value)",
            ],
            Language.ENGLISH: [
                "English TQ",
                "English (Ordinal)",
                "English (Reverse Ordinal)",
                "English (Reduced)",
                "TQ (Reduced)",
                "TQ (Square)",
                "TQ (Triangular)",
            ],
            Language.LATIN: [
                "English TQ",  # Latin can use English ciphers
                "English (Ordinal)",
            ],
            Language.ARABIC: [
                "English TQ",  # Fallback until Arabic support
            ],
            Language.UNKNOWN: [
                "English TQ",
            ],
        }

        return cipher_suggestions.get(language, ["English TQ"])


# Global instance for application-wide use
_global_preferences: Optional[CipherPreferences] = None


def get_cipher_preferences() -> CipherPreferences:
    """Get the global cipher preferences instance."""
    global _global_preferences
    if _global_preferences is None:
        _global_preferences = CipherPreferences()
    return _global_preferences


def set_language_cipher(language: Language, cipher_name: str):
    """Set cipher preference for a language (convenience function)."""
    prefs = get_cipher_preferences()
    prefs.set_cipher(language, cipher_name)


def get_language_cipher(language: Language) -> str:
    """Get cipher preference for a language (convenience function)."""
    prefs = get_cipher_preferences()
    return prefs.get_cipher(language)