"""
Output/Export tab for the Unified Geometry Viewer.

Provides controls for:
- Viewport snapshots
- Measurement data export
- Canon declaration export (JSON)
- Validation report export
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from shared.ui.theme import COLORS, set_archetype

if TYPE_CHECKING:
    pass  # No type checking imports needed


class OutputTab:
    """Builder for the Output/Export tab."""
    
    def build(
        self,
        on_snapshot_clicked: Callable[[], None],
        on_copy_measurements_clicked: Callable[[], None],
        on_copy_declaration_clicked: Callable[[], None],
        on_copy_validation_clicked: Callable[[], None],
    ) -> QWidget:
        """
        Build the Output/Export tab.
        
        Args:
            on_snapshot_clicked: Callback for snapshot button
            on_copy_measurements_clicked: Callback for copy measurements
            on_copy_declaration_clicked: Callback for copy declaration
            on_copy_validation_clicked: Callback for copy validation report
            
        Returns:
            The configured tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Section: Export
        section_label = QLabel("Export")
        section_label.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(section_label)
        
        # Snapshot button
        snapshot_btn = QPushButton("📷 Save Snapshot")
        set_archetype(snapshot_btn, "ghost")
        snapshot_btn.clicked.connect(on_snapshot_clicked)
        layout.addWidget(snapshot_btn)
        
        # Copy measurements button
        copy_btn = QPushButton("📋 Copy Measurements")
        set_archetype(copy_btn, "ghost")
        copy_btn.clicked.connect(on_copy_measurements_clicked)
        layout.addWidget(copy_btn)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {COLORS['ash']};")
        divider.setFixedHeight(1)
        layout.addWidget(divider)
        
        # Section: Canon Exports
        canon_section = QLabel("Canon Exports")
        canon_section.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(canon_section)
        
        # Copy Declaration button
        decl_btn = QPushButton("📜 Copy Declaration (JSON)")
        set_archetype(decl_btn, "seeker")
        decl_btn.clicked.connect(on_copy_declaration_clicked)
        layout.addWidget(decl_btn)
        
        # Copy Validation Report button
        report_btn = QPushButton("📊 Copy Validation Report")
        set_archetype(report_btn, "seeker")
        report_btn.clicked.connect(on_copy_validation_clicked)
        layout.addWidget(report_btn)
        
        layout.addStretch()
        
        return tab
