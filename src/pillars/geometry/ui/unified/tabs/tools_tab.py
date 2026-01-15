"""Tools tab for measurement and analysis features."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from shared.ui.theme import COLORS

if TYPE_CHECKING:
    from ..geometry3d.view3d import Geometry3DView


class ToolsTab:
    """Builder for the Tools tab containing measurement controls."""
    
    def __init__(self, viewport: Geometry3DView):
        """Initialize the tools tab builder.
        
        Args:
            viewport: The 3D viewport to control
        """
        self.viewport = viewport
        self._measure_button: QPushButton | None = None
        self._precision_spinbox: QSpinBox | None = None
        self._snap_slider: QSlider | None = None
        self._snap_label: QLabel | None = None
        self._snap_canonical_checkbox: QCheckBox | None = None
        self._show_angles_checkbox: QCheckBox | None = None
        self._angle_unit_combo: QComboBox | None = None
    
    def build(self, on_measure_toggled, on_snapshot_clicked) -> QWidget:
        """Build and return the tools tab widget.
        
        Args:
            on_measure_toggled: Callback for measure button toggle
            on_snapshot_clicked: Callback for snapshot button click
            
        Returns:
            The configured tools tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # Measurement Tools section
        self._add_measurement_tools_section(layout, on_measure_toggled)
        
        # Measurement Settings section
        self._add_measurement_settings_section(layout)
        
        # Angle Measurements section
        self._add_angle_measurements_section(layout)
        
        # Quick Actions section
        self._add_quick_actions_section(layout, on_snapshot_clicked)
        
        layout.addStretch()
        
        return tab
    
    def _add_measurement_tools_section(self, layout: QVBoxLayout, on_measure_toggled):
        """Add the measurement tools section."""
        section1 = QLabel("Measurement Tools")
        section1.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(section1)
        
        # Measure tool button
        self._measure_button = QPushButton("📏 Measure Tool")
        self._measure_button.setObjectName("MeasureToolBtn")
        self._measure_button.setCheckable(True)
        self._measure_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._measure_button.setStyleSheet(f"""
            QPushButton#MeasureToolBtn {{
                background-color: {COLORS['marble']};
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 600;
                color: {COLORS['void']};
            }}
            QPushButton#MeasureToolBtn:checked {{
                background-color: {COLORS['seeker_soft']};
                border-color: {COLORS['seeker']};
                color: {COLORS['seeker']};
            }}
            QPushButton#MeasureToolBtn:hover {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        self._measure_button.toggled.connect(on_measure_toggled)
        layout.addWidget(self._measure_button)
        
        # Clear measurements button
        clear_btn = QPushButton("🗑️ Clear Measurements")
        clear_btn.clicked.connect(self.viewport.clear_measurements)
        layout.addWidget(clear_btn)
    
    def _add_measurement_settings_section(self, layout: QVBoxLayout):
        """Add the measurement settings section."""
        section2 = QLabel("Measurement Settings")
        section2.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 12px;
        """)
        layout.addWidget(section2)
        
        # Decimal precision control
        precision_layout = QHBoxLayout()
        precision_layout.addWidget(QLabel("Decimal Precision:"))
        self._precision_spinbox = QSpinBox()
        self._precision_spinbox.setRange(0, 8)
        self._precision_spinbox.setValue(4)
        self._precision_spinbox.valueChanged.connect(self.viewport.set_measure_precision)
        precision_layout.addWidget(self._precision_spinbox)
        precision_layout.addStretch()
        layout.addLayout(precision_layout)
        
        # Snap threshold control
        snap_layout = QHBoxLayout()
        snap_layout.addWidget(QLabel("Snap Threshold:"))
        self._snap_slider = QSlider(Qt.Orientation.Horizontal)
        self._snap_slider.setRange(5, 50)
        self._snap_slider.setValue(15)
        self._snap_slider.valueChanged.connect(self.viewport.set_snap_threshold)
        snap_layout.addWidget(self._snap_slider)
        self._snap_label = QLabel("15px")
        self._snap_slider.valueChanged.connect(lambda v: self._snap_label.setText(f"{v}px"))
        snap_layout.addWidget(self._snap_label)
        layout.addLayout(snap_layout)
        
        # Snap to canonical checkbox
        self._snap_canonical_checkbox = QCheckBox("Snap to Canonical Shape")
        self._snap_canonical_checkbox.setChecked(False)
        self._snap_canonical_checkbox.setToolTip("Prefer snapping to the shape's intended vertices/edges")
        self._snap_canonical_checkbox.toggled.connect(self.viewport.set_snap_to_canonical)
        layout.addWidget(self._snap_canonical_checkbox)
    
    def _add_angle_measurements_section(self, layout: QVBoxLayout):
        """Add the angle measurements section."""
        section3 = QLabel("Angle Measurements")
        section3.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 12px;
        """)
        layout.addWidget(section3)
        
        # Show angles checkbox
        self._show_angles_checkbox = QCheckBox("Show Angles")
        self._show_angles_checkbox.setChecked(False)
        self._show_angles_checkbox.toggled.connect(self.viewport.set_show_angles)
        layout.addWidget(self._show_angles_checkbox)
        
        # Angle unit selection
        unit_layout = QHBoxLayout()
        unit_layout.addWidget(QLabel("Unit:"))
        self._angle_unit_combo = QComboBox()
        self._angle_unit_combo.addItems(["Degrees", "Radians"])
        self._angle_unit_combo.currentTextChanged.connect(
            lambda text: self.viewport.set_angle_unit(text.lower())
        )
        unit_layout.addWidget(self._angle_unit_combo)
        unit_layout.addStretch()
        layout.addLayout(unit_layout)
    
    def _add_quick_actions_section(self, layout: QVBoxLayout, on_snapshot_clicked):
        """Add the quick actions section."""
        section4 = QLabel("Quick Actions")
        section4.setStyleSheet(f"""
            color: {COLORS['stone']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 12px;
        """)
        layout.addWidget(section4)
        
        # Take snapshot button
        snapshot_btn = QPushButton("📸 Take Snapshot")
        snapshot_btn.clicked.connect(on_snapshot_clicked)
        layout.addWidget(snapshot_btn)
    
    @property
    def measure_button(self) -> QPushButton | None:
        """Get the measure button widget."""
        return self._measure_button
