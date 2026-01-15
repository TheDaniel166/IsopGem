"""
View/Camera settings tab for the Unified Geometry Viewer.

Provides controls for:
- Camera orientation (elevation, azimuth sliders)
- Quick view presets (Top, Front, Side, Iso)
- Zoom controls (in/out/fit/reset)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from shared.ui.theme import COLORS, set_archetype

if TYPE_CHECKING:
    from ...geometry3d.view3d import Geometry3DView


class ViewTab:
    """Builder for the View/Camera settings tab."""
    
    def __init__(self, viewport: Geometry3DView):
        """
        Initialize the View tab builder.
        
        Args:
            viewport: The 3D viewport to control
        """
        self._viewport = viewport
    
    def build(self) -> tuple[QWidget, QSlider, QSlider]:
        """
        Build the View/Camera settings tab.
        
        Returns:
            Tuple of (tab widget, elevation slider, azimuth slider)
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Section: Camera (3D only)
        section_label = QLabel("Camera (3D)")
        section_label.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(section_label)
        
        # Elevation slider
        elevation_slider, elevation_value = self._add_slider(
            layout, "Elevation:", -90, 90, 30, self._viewport.set_elevation
        )
        
        # Azimuth slider
        azimuth_slider, azimuth_value = self._add_slider(
            layout, "Azimuth:", 0, 360, 45, self._viewport.set_azimuth
        )
        
        # Section: Quick Views
        section2 = QLabel("Quick Views")
        section2.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 8px;
        """)
        layout.addWidget(section2)
        
        # Quick view buttons grid
        quick_views_layout = QHBoxLayout()
        quick_views_layout.setSpacing(8)
        
        quick_views = [
            ("Top", 0, 0),
            ("Front", -90, 0),
            ("Side", 0, 90),
            ("Iso", 30, 45),
        ]
        for name, elev, azim in quick_views:
            btn = self._create_quick_view_button(
                name, elev, azim, elevation_slider, azimuth_slider
            )
            quick_views_layout.addWidget(btn)
        
        layout.addLayout(quick_views_layout)
        
        # Section: Zoom
        section3 = QLabel("Zoom")
        section3.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 8px;
        """)
        layout.addWidget(section3)
        
        # Zoom buttons
        zoom_layout = QHBoxLayout()
        zoom_layout.setSpacing(8)
        
        zoom_in_btn = self._create_tool_button("➕ Zoom In")
        zoom_in_btn.clicked.connect(self._viewport.zoom_in)
        zoom_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = self._create_tool_button("➖ Zoom Out")
        zoom_out_btn.clicked.connect(self._viewport.zoom_out)
        zoom_layout.addWidget(zoom_out_btn)
        
        layout.addLayout(zoom_layout)
        
        # Fit and Reset buttons
        fit_btn = QPushButton("🔍 Fit to View")
        fit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                color: {COLORS['stone']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                color: {COLORS['void']};
            }}
        """)
        fit_btn.clicked.connect(self._viewport.fit_to_view)
        layout.addWidget(fit_btn)
        
        reset_btn = QPushButton("↺ Reset View")
        set_archetype(reset_btn, "ghost")
        reset_btn.clicked.connect(self._viewport.reset_view)
        layout.addWidget(reset_btn)
        
        layout.addStretch()
        
        return tab, elevation_slider, azimuth_slider
    
    def _add_slider(
        self,
        layout: QVBoxLayout,
        label: str,
        min_val: int,
        max_val: int,
        default: int,
        callback: callable
    ) -> tuple[QSlider, QLabel]:
        """Helper to create and add a slider with label."""
        slider_layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: {COLORS['stone']}; font-size: 12px;")
        slider_layout.addWidget(label_widget)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.valueChanged.connect(lambda v: callback(float(v)))
        slider_layout.addWidget(slider)
        
        value_label = QLabel(f"{default}°")
        value_label.setStyleSheet(f"color: {COLORS['mist']}; font-size: 11px;")
        value_label.setFixedWidth(40)
        slider.valueChanged.connect(lambda v: value_label.setText(f"{v}°"))
        slider_layout.addWidget(value_label)
        
        layout.addLayout(slider_layout)
        
        return slider, value_label
    
    def _create_quick_view_button(
        self,
        name: str,
        elev: int,
        azim: int,
        elevation_slider: QSlider,
        azimuth_slider: QSlider
    ) -> QPushButton:
        """Create a quick view preset button."""
        btn = QPushButton(name)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                color: {COLORS['stone']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                color: {COLORS['void']};
            }}
        """)
        
        def set_view():
            elevation_slider.setValue(elev)
            azimuth_slider.setValue(azim)
            self._viewport.set_elevation(float(elev))
            self._viewport.set_azimuth(float(azim))
        
        btn.clicked.connect(set_view)
        return btn
    
    def _create_tool_button(self, text: str) -> QPushButton:
        """Create a styled tool button."""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                color: {COLORS['stone']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_hover']};
                color: {COLORS['void']};
            }}
        """)
        return btn
