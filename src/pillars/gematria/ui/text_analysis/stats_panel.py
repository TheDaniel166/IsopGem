"""
Stats Panel - The Numerological Summary.
Panel displaying document statistics including word count and gematria totals.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt
from shared.ui.theme import COLORS, get_exegesis_group_style

class StatsPanel(QWidget):
    """
    Panel for displaying document statistics.
    """
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("Document Statistics")
        group.setStyleSheet(get_exegesis_group_style(title_top=12))
        group_layout = QFormLayout(group)
        group_layout.setSpacing(10)
        
        # Styles for labels
        self._lbl_style = f"font-size: 10pt; color: {COLORS['text_secondary']};"
        self._val_style = f"font-size: 11pt; font-weight: 600; color: {COLORS['text_primary']};"
        
        self.word_count_lbl = QLabel("0")
        self.word_count_lbl.setStyleSheet(self._val_style)
        l1 = QLabel("Word Count:")
        l1.setStyleSheet(self._lbl_style)
        group_layout.addRow(l1, self.word_count_lbl)
        
        self.char_count_lbl = QLabel("0")
        self.char_count_lbl.setStyleSheet(self._val_style)
        l2 = QLabel("Character Count:")
        l2.setStyleSheet(self._lbl_style)
        group_layout.addRow(l2, self.char_count_lbl)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #e2e8f0;")
        group_layout.addRow(line)
        
        self.total_val_lbl = QLabel("0")
        self.total_val_lbl.setStyleSheet(f"{self._val_style} color: {COLORS['focus']};")
        l3 = QLabel("Total Gematria:")
        l3.setStyleSheet(self._lbl_style)
        group_layout.addRow(l3, self.total_val_lbl)
        
        self.avg_val_lbl = QLabel("0")
        self.avg_val_lbl.setStyleSheet(self._val_style)
        l4 = QLabel("Avg. Word Value:")
        l4.setStyleSheet(self._lbl_style)
        group_layout.addRow(l4, self.avg_val_lbl)

        layout.addWidget(group)

        # Language breakdown group (hidden by default, shown when multi-language detected)
        self.lang_group = QGroupBox("Language Breakdown")
        self.lang_group.setStyleSheet(get_exegesis_group_style(title_top=12))
        self.lang_layout = QFormLayout(self.lang_group)
        self.lang_layout.setSpacing(8)
        self.lang_group.setVisible(False)  # Hidden until populated

        layout.addWidget(self.lang_group)
        layout.addStretch()
        
    def update_stats(self, stats: dict):
        """Update labels with stats dict."""
        self.word_count_lbl.setText(f"{stats.get('word_count', 0):,}")
        self.char_count_lbl.setText(f"{stats.get('char_count', 0):,}")
        self.total_val_lbl.setText(f"{stats.get('total_value', 0):,}")
        self.avg_val_lbl.setText(f"{stats.get('avg_word_val', 0):.2f}")

        lang_stats = stats.get("language_breakdown") or []
        self._render_language_breakdown(lang_stats, stats)

    def _render_language_breakdown(self, lang_stats, stats: dict):
        """Render the per-language rows; show only when multiple languages detected."""
        # Clear previous rows
        while self.lang_layout.count():
            item = self.lang_layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                item.layout().deleteLater()

        if not lang_stats or len(lang_stats) <= 1:
            self.lang_group.setVisible(False)
            return

        for entry in lang_stats:
            language = entry.get("language", "Unknown")
            cipher = entry.get("cipher", "None")
            total_value = entry.get("total_value", 0)
            word_count = entry.get("word_count", 0)

            label = QLabel(f"{language} | {cipher}")
            label.setStyleSheet(self._lbl_style)

            value = QLabel(f"{total_value:,}  (words: {word_count:,})")
            value.setStyleSheet(self._val_style)

            self.lang_layout.addRow(label, value)

        total_label = QLabel("All Languages")
        total_label.setStyleSheet(self._lbl_style)

        total_value_lbl = QLabel(
            f"{stats.get('total_value', 0):,}  (words: {stats.get('word_count', 0):,})"
        )
        total_value_lbl.setStyleSheet(f"{self._val_style} color: {COLORS['focus']};")
        self.lang_layout.addRow(total_label, total_value_lbl)

        self.lang_group.setVisible(True)