"""
History tab for the Unified Geometry Viewer.

Provides controls for:
- Calculation history timeline
- Undo/Redo navigation
- Session export
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from shared.ui.theme import COLORS, set_archetype

if TYPE_CHECKING:
    pass  # No type checking imports needed


class HistoryTab:
    """Builder for the History tab."""
    
    def build(
        self,
        on_undo_clicked: Callable[[], None],
        on_redo_clicked: Callable[[], None],
        on_export_session_clicked: Callable[[], None],
    ) -> tuple[QWidget, QPushButton, QPushButton, QWidget, QVBoxLayout, QLabel]:
        """
        Build the History tab with timeline and controls.
        
        Args:
            on_undo_clicked: Callback for undo button
            on_redo_clicked: Callback for redo button
            on_export_session_clicked: Callback for export session button
            
        Returns:
            Tuple of (tab widget, undo button, redo button, history list widget,
                     history list layout, empty state label)
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Section: Timeline
        section_label = QLabel("Calculation History")
        section_label.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(section_label)
        
        # Undo/Redo buttons
        nav_layout = QHBoxLayout()
        
        undo_btn = QPushButton("↶ Undo")
        set_archetype(undo_btn, "ghost")
        undo_btn.setEnabled(False)
        undo_btn.clicked.connect(on_undo_clicked)
        nav_layout.addWidget(undo_btn)
        
        redo_btn = QPushButton("↷ Redo")
        set_archetype(redo_btn, "ghost")
        redo_btn.setEnabled(False)
        redo_btn.clicked.connect(on_redo_clicked)
        nav_layout.addWidget(redo_btn)
        
        layout.addLayout(nav_layout)
        
        # History list (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setMaximumHeight(200)
        
        history_list_widget = QWidget()
        history_list_layout = QVBoxLayout(history_list_widget)
        history_list_layout.setContentsMargins(0, 0, 0, 0)
        history_list_layout.setSpacing(4)
        
        # Empty state
        empty_label = QLabel("No history yet")
        empty_label.setStyleSheet(f"color: {COLORS['mist']}; font-style: italic;")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        history_list_layout.addWidget(empty_label)
        
        history_list_layout.addStretch()
        
        scroll.setWidget(history_list_widget)
        layout.addWidget(scroll, 1)
        
        # Tip label
        tip_label = QLabel("Right-click an item for options (notes, rename, delete)")
        tip_label.setStyleSheet(f"""
            color: {COLORS['mist']};
            font-size: 10px;
            font-style: italic;
            padding: 4px 0;
        """)
        layout.addWidget(tip_label)
        
        # Export session button
        export_btn = QPushButton("💾 Export Session")
        set_archetype(export_btn, "ghost")
        export_btn.clicked.connect(on_export_session_clicked)
        layout.addWidget(export_btn)
        
        return tab, undo_btn, redo_btn, history_list_widget, history_list_layout, empty_label
