"""
Canon validation tab for the Unified Geometry Viewer.

Provides display of:
- Validation status (icon and text)
- Findings/warnings from Canon validation
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from shared.ui.theme import COLORS


class CanonTab:
    """Builder for the Canon validation details tab."""
    
    def build(self) -> tuple[QWidget, QFrame, QLabel, QLabel, QTextEdit]:
        """
        Build the Canon validation details tab.
        
        Returns:
            Tuple of (tab widget, status frame, status icon, status text, findings text area)
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Section: Validation Status
        section_label = QLabel("Validation Status")
        section_label.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(section_label)
        
        # Large status indicator
        status_frame = QFrame()
        status_frame.setObjectName("CanonStatusFrame")
        status_frame.setStyleSheet(f"""
            QFrame#CanonStatusFrame {{
                background-color: {COLORS['navigator_soft']};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        
        status_layout = QVBoxLayout(status_frame)
        
        status_icon = QLabel("⏳")
        status_icon.setStyleSheet("font-size: 32px;")
        status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(status_icon)
        
        status_text = QLabel("Awaiting validation")
        status_text.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 14px;
            font-weight: 500;
        """)
        status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(status_text)
        
        layout.addWidget(status_frame)
        
        # Findings section
        findings_label = QLabel("Findings")
        findings_label.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(findings_label)
        
        # Findings list (scrollable text area)
        findings_text = QTextEdit()
        findings_text.setReadOnly(True)
        findings_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['cloud']};
                border: 1px solid {COLORS['ash']};
                border-radius: 4px;
                color: {COLORS['stone']};
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 11px;
                padding: 8px;
            }}
        """)
        findings_text.setPlaceholderText("No findings to display")
        layout.addWidget(findings_text, 1)
        
        return tab, status_frame, status_icon, status_text, findings_text
