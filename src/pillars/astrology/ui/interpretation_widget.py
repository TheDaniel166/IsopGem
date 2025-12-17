"""Interpretation Result Widget."""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt

from pillars.astrology.models.interpretation_models import InterpretationReport
from shared.ui.theme import COLORS

class InterpretationWidget(QWidget):
    """Displays a generated chart interpretation report."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        self.header_label = QLabel("Interpretation")
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.header_label)

        self.text_view = QTextEdit()
        self.text_view.setReadOnly(True)
        self.text_view.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                font-family: 'Roboto', sans-serif;
                font-size: 14px;
                padding: 10px;
            }}
        """)
        # Custom Placeholder
        self.text_view.setPlaceholderText("Generate a chart to see the interpretation here.")
        self.layout.addWidget(self.text_view)

    def display_report(self, report: InterpretationReport) -> None:
        """Render the report into the text view."""
        self.header_label.setText(f"Interpretation for {report.chart_name}")
        
        # Simple Markdown to HTML conversion (or just use setMarkdown if supported)
        # PyQt6 QTextEdit supports Markdown natively.
        self.text_view.setMarkdown(report.to_markdown())
