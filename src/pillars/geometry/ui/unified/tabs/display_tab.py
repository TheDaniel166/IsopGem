"""
Display settings tab for the Unified Geometry Viewer.

Provides controls for:
- Core element visibility (axes, labels, faces, edges, vertices)
- 3D special elements (dual solid, spheres)
- Color theme customization
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from shared.ui.theme import COLORS

if TYPE_CHECKING:
    from ...geometry3d.view3d import Geometry3DView


class DisplayTab:
    """Builder for the Display settings tab."""
    
    def __init__(self, viewport: Geometry3DView):
        """
        Initialize the Display tab builder.
        
        Args:
            viewport: The 3D viewport to control
        """
        self._viewport = viewport
    
    def build(self) -> tuple[QWidget, dict[str, QCheckBox]]:
        """
        Build the Display settings tab.
        
        Returns:
            Tuple of (tab widget, dict of checkbox references for external control)
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Section: Core Visibility
        section1 = QLabel("Core Elements")
        section1.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(section1)
        
        # Checkboxes dict for external reference
        checkboxes: dict[str, QCheckBox] = {}
        
        # Core element checkboxes
        checkboxes['axes'] = self._add_checkbox(
            layout, "Show Axes", True, self._viewport.set_axes_visible
        )
        checkboxes['labels'] = self._add_checkbox(
            layout, "Show Labels", False, self._viewport.set_labels_visible
        )
        checkboxes['faces'] = self._add_checkbox(
            layout, "Show Faces", True, self._viewport.set_show_faces
        )
        checkboxes['edges'] = self._add_checkbox(
            layout, "Show Edges", True, self._viewport.set_show_edges
        )
        checkboxes['vertices'] = self._add_checkbox(
            layout, "Show Vertices", False, self._viewport.set_show_vertices
        )
        
        # Section: 3D Special Elements
        section2 = QLabel("3D Special")
        section2.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 8px;
        """)
        layout.addWidget(section2)
        
        # Dual solid toggle
        checkboxes['dual'] = self._add_checkbox(
            layout, "Show Dual Solid (Ghost)", False, self._viewport.set_dual_visible
        )
        
        # Circle/Sphere toggles
        sphere_toggles = [
            ("incircle", "Show Incircle"),
            ("midsphere", "Show Midsphere"),
            ("circumsphere", "Show Circumcircle"),
        ]
        for key, label in sphere_toggles:
            cb = self._add_checkbox(
                layout, label, False,
                lambda checked, k=key: self._viewport.set_sphere_visible(k, checked)
            )
            checkboxes[f'sphere_{key}'] = cb
        
        # Section: Tools
        section3 = QLabel("Tools")
        section3.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 8px;
        """)
        layout.addWidget(section3)
        
        # Color Settings button
        color_settings_btn = QPushButton("🎨 Color Settings...")
        color_settings_btn.clicked.connect(self._open_color_settings)
        layout.addWidget(color_settings_btn)
        
        layout.addStretch()
        
        return tab, checkboxes
    
    def _add_checkbox(
        self,
        layout: QVBoxLayout,
        label: str,
        default: bool,
        callback: Callable[[bool], None]
    ) -> QCheckBox:
        """Helper to create and add a checkbox."""
        cb = QCheckBox(label)
        cb.setChecked(default)
        cb.toggled.connect(callback)
        layout.addWidget(cb)
        return cb
    
    def _open_color_settings(self) -> None:
        """Open the color settings dialog."""
        from ...geometry3d.color_settings_dialog import ColorSettingsDialog
        
        current_theme = self._viewport.get_color_theme()
        dialog = ColorSettingsDialog(current_theme, self._viewport.parent())
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_theme = dialog.get_theme()
            self._viewport.set_color_theme(new_theme)
