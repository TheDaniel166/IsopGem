"""Cipher selection dialog shown when opening documents with non-English languages."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt
from typing import Dict, List
from shared.services.gematria.language_detector import Language
from shared.services.gematria.cipher_preferences import CipherPreferences


class CipherSelectionDialog(QDialog):
    """Dialog for selecting ciphers for each detected language in a document."""

    def __init__(self, language_percentages: List[tuple[Language, float]],
                 available_calculators: Dict[str, any], parent=None):
        """
        Initialize cipher selection dialog.

        Args:
            language_percentages: List of (Language, percentage) tuples for detected languages
            available_calculators: Dict of calculator_name -> calculator instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.language_percentages = language_percentages
        self.available_calculators = available_calculators
        self.selected_ciphers: Dict[Language, str] = {}

        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Select Ciphers for Detected Languages")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Header
        header = QLabel("Multiple languages detected in this document.\nPlease select which cipher to use for each language:")
        header.setWordWrap(True)
        header.setStyleSheet("font-size: 13px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Language selection groups
        self.cipher_combos: Dict[Language, QComboBox] = {}

        for language, percentage in self.language_percentages:
            group = self._create_language_group(language, percentage)
            layout.addWidget(group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("Apply Ciphers")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet("""
            QPushButton {
                background: #7c3aed;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #6d28d9;
            }
        """)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

    def _create_language_group(self, language: Language, percentage: float) -> QGroupBox:
        """Create a group box for selecting cipher for a language."""
        # Language icons
        lang_icons = {
            Language.HEBREW: "🕎",
            Language.GREEK: "🏛️",
            Language.ARABIC: "🕌",
            Language.LATIN: "🏛️",
        }

        icon = lang_icons.get(language, "🌍")
        title = f"{icon} {language.value} ({percentage:.1f}% of document)"

        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e9d5ff;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        form = QFormLayout(group)

        # Get available ciphers for this language
        available_ciphers = self._get_ciphers_for_language(language)

        # Cipher selection combo
        combo = QComboBox()
        combo.addItems(available_ciphers)

        # Set default from preferences
        prefs = CipherPreferences()
        default_cipher = prefs.get_cipher(language)
        if default_cipher in available_ciphers:
            combo.setCurrentText(default_cipher)

        self.cipher_combos[language] = combo

        form.addRow("Cipher:", combo)

        return group

    def _get_ciphers_for_language(self, language: Language) -> List[str]:
        """Get list of available cipher names for a language."""
        # Define keywords to match ciphers to languages
        keywords = {
            Language.HEBREW: ["Hebrew", "Hebraic"],
            Language.GREEK: ["Greek", "Isopsephy"],
            Language.ARABIC: ["Arabic"],
            Language.LATIN: ["Latin", "English"],
            Language.ENGLISH: ["English", "TQ"],
        }

        lang_keywords = keywords.get(language, [])

        # Find matching calculators
        matching = []
        for calc_name in self.available_calculators.keys():
            for keyword in lang_keywords:
                if keyword.lower() in calc_name.lower():
                    matching.append(calc_name)
                    break

        return matching if matching else list(self.available_calculators.keys())

    def get_selected_ciphers(self) -> Dict[Language, str]:
        """Get the selected cipher for each language."""
        result = {}
        for language, combo in self.cipher_combos.items():
            result[language] = combo.currentText()
        return result
