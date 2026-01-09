"""
Interlinear Tools Panel - Dedicated tools for interlinear text exploration.

Provides specialized tools when Interlinear mode is active:
- TQ value cross-reference lookup
- Etymology chain explorer
- Word statistics and concordance quick access
- Export tools for interlinear analysis
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QGroupBox,
    QTextBrowser, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class InterlinearToolsPanel(QWidget):
    """
    Tools panel for interlinear text exploration.

    Features:
    - Cross-reference by TQ value
    - Etymology chain quick lookup
    - Word concordance access
    - Clean, minimal interface
    """

    # Signals
    tq_lookup_requested = pyqtSignal(int)  # TQ value to find
    word_lookup_requested = pyqtSignal(str)  # Word to explore

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the tools panel layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Header
        header = QLabel("Interlinear Tools")
        header.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            color: #7c3aed;
            padding: 8px;
        """)
        layout.addWidget(header)

        # --- TQ Cross-Reference ---
        tq_group = QGroupBox("TQ Cross-Reference")
        tq_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #6366f1;
                border: 2px solid #e9d5ff;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        tq_layout = QVBoxLayout(tq_group)
        tq_layout.setSpacing(8)

        # TQ input
        tq_input_layout = QHBoxLayout()
        tq_input_layout.addWidget(QLabel("TQ Value:"))
        self.tq_input = QLineEdit()
        self.tq_input.setPlaceholderText("Enter TQ value...")
        self.tq_input.returnPressed.connect(self._on_tq_lookup)
        tq_input_layout.addWidget(self.tq_input)

        self.tq_lookup_btn = QPushButton("Find Words")
        self.tq_lookup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tq_lookup_btn.clicked.connect(self._on_tq_lookup)
        self.tq_lookup_btn.setStyleSheet("""
            QPushButton {
                background: #7c3aed;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #6d28d9;
            }
        """)
        tq_input_layout.addWidget(self.tq_lookup_btn)
        tq_layout.addLayout(tq_input_layout)

        # TQ results
        self.tq_results = QListWidget()
        self.tq_results.setMaximumHeight(150)
        self.tq_results.setStyleSheet("""
            QListWidget {
                background: #faf5ff;
                border: 1px solid #e9d5ff;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 6px;
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background: #ede9fe;
            }
            QListWidget::item:selected {
                background: #c4b5fd;
                color: #1f2937;
            }
        """)
        self.tq_results.itemDoubleClicked.connect(self._on_tq_result_selected)
        tq_layout.addWidget(self.tq_results)

        layout.addWidget(tq_group)

        # --- Etymology Quick Lookup ---
        etym_group = QGroupBox("Etymology Lookup")
        etym_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #6366f1;
                border: 2px solid #e9d5ff;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        etym_layout = QVBoxLayout(etym_group)
        etym_layout.setSpacing(8)

        # Word input
        word_input_layout = QHBoxLayout()
        word_input_layout.addWidget(QLabel("Word:"))
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Enter word...")
        self.word_input.returnPressed.connect(self._on_word_lookup)
        word_input_layout.addWidget(self.word_input)

        self.word_lookup_btn = QPushButton("Explore")
        self.word_lookup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.word_lookup_btn.clicked.connect(self._on_word_lookup)
        self.word_lookup_btn.setStyleSheet("""
            QPushButton {
                background: #9333ea;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7e22ce;
            }
        """)
        word_input_layout.addWidget(self.word_lookup_btn)
        etym_layout.addLayout(word_input_layout)

        # Etymology preview
        self.etym_preview = QTextBrowser()
        self.etym_preview.setMaximumHeight(200)
        self.etym_preview.setOpenExternalLinks(False)
        self.etym_preview.setStyleSheet("""
            QTextBrowser {
                background: #faf5ff;
                border: 1px solid #e9d5ff;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        etym_layout.addWidget(self.etym_preview)

        layout.addWidget(etym_group)

        # --- Quick Actions ---
        actions_group = QGroupBox("Quick Actions")
        actions_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #6366f1;
                border: 2px solid #e9d5ff;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(6)

        self.export_btn = QPushButton("📄 Export Interlinear Analysis")
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.clicked.connect(self._on_export)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background: #6366f1;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background: #4f46e5;
            }
        """)
        actions_layout.addWidget(self.export_btn)

        self.concordance_btn = QPushButton("📚 Open Concordance")
        self.concordance_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.concordance_btn.clicked.connect(self._on_open_concordance)
        self.concordance_btn.setStyleSheet("""
            QPushButton {
                background: #8b5cf6;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background: #7c3aed;
            }
        """)
        actions_layout.addWidget(self.concordance_btn)

        layout.addWidget(actions_group)

        # --- Info/Status ---
        self.info_label = QLabel("Click words in the interlinear view to explore definitions and etymology.")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 11px;
                font-style: italic;
                padding: 8px;
                background: #f3f4f6;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.info_label)

        layout.addStretch()

    def _on_tq_lookup(self):
        """Handle TQ value lookup request."""
        value_text = self.tq_input.text().strip()
        if not value_text:
            return

        try:
            tq_value = int(value_text)
            self._find_words_by_tq(tq_value)
        except ValueError:
            self.info_label.setText("⚠️ Please enter a valid numeric TQ value.")

    def _find_words_by_tq(self, tq_value: int):
        """Find all words in concordance with the given TQ value."""
        try:
            from shared.services.lexicon.holy_key_service import HolyKeyService

            key_service = HolyKeyService()
            words = key_service.find_words_by_tq_value(tq_value)

            self.tq_results.clear()

            if not words:
                self.info_label.setText(f"No words found with TQ value {tq_value}")
                return

            for word_data in words:
                word = word_data.get('word', '')
                frequency = word_data.get('frequency', 0)

                item = QListWidgetItem(f"{word} ({frequency} occurrences)")
                item.setData(Qt.ItemDataRole.UserRole, word)
                self.tq_results.addItem(item)

            self.info_label.setText(f"Found {len(words)} words with TQ value {tq_value}")

        except Exception as e:
            logger.error(f"Error finding words by TQ value: {e}", exc_info=True)
            self.info_label.setText(f"Error: {e}")

    def _on_tq_result_selected(self, item: QListWidgetItem):
        """Handle double-click on TQ result - explore the word."""
        word = item.data(Qt.ItemDataRole.UserRole)
        if word:
            self.word_input.setText(word)
            self._on_word_lookup()

    def _on_word_lookup(self):
        """Handle word etymology lookup request."""
        word = self.word_input.text().strip()
        if not word:
            return

        self._show_etymology_preview(word)

    def _show_etymology_preview(self, word: str):
        """Show quick etymology preview for the word."""
        try:
            from shared.services.lexicon.etymology_db_service import EtymologyDbService

            etym_service = EtymologyDbService()
            relations = etym_service.get_etymologies(word.lower(), "English", max_results=5)

            if not relations:
                self.etym_preview.setHtml(f"""
                    <div style='color: #6b7280; font-style: italic;'>
                    No etymology data found for '{word}'
                    </div>
                """)
                return

            # Build preview HTML
            html_parts = []
            html_parts.append(f"<h3 style='color: #7c3aed; margin: 0 0 8px 0;'>{word}</h3>")

            type_icons = {
                'inherited_from': '👪',
                'borrowed_from': '🔄',
                'derived_from': '🌱',
                'has_root': '🌳',
            }

            for rel in relations[:5]:
                icon = type_icons.get(rel.reltype, '•')
                rel_display = rel.reltype.replace('_', ' ').title()
                lang = rel.related_lang if rel.related_lang else 'English'

                html_parts.append(f"""
                    <div style='margin: 4px 0; padding: 6px; background: #f3e8ff; border-radius: 3px;'>
                        {icon} <b>{rel_display}</b>: {rel.related_term} ({lang})
                    </div>
                """)

            if len(relations) > 5:
                html_parts.append(f"<p style='color: #6b7280; font-size: 11px; margin-top: 8px;'>...and {len(relations) - 5} more relationships</p>")

            self.etym_preview.setHtml("".join(html_parts))
            self.info_label.setText(f"Etymology: {len(relations)} relationships found")

        except Exception as e:
            logger.error(f"Error showing etymology preview: {e}", exc_info=True)
            self.etym_preview.setHtml(f"<div style='color: #ef4444;'>Error: {e}</div>")

    def _on_export(self):
        """Handle export interlinear analysis request."""
        # Signal parent to handle export
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Export", "Export functionality will be implemented soon.")

    def _on_open_concordance(self):
        """Handle open concordance request."""
        # Find parent main window and trigger concordance
        parent = self.parent()
        while parent:
            if hasattr(parent, '_open_concordance'):
                parent._open_concordance()
                return
            parent = parent.parent()
