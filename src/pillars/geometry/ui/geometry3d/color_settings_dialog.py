"""Color Settings Dialog for 3D Viewport Customization."""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QColorDialog, QGroupBox, QGridLayout
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

from .view3d import ColorTheme


class ColorSettingsDialog(QDialog):
    """Dialog for customizing viewport colors."""
    
    def __init__(self, current_theme: ColorTheme, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Viewport Color Settings")
        self.setMinimumSize(600, 700)
        
        self._theme = ColorTheme(
            background=QColor(current_theme.background),
            face_default=QColor(current_theme.face_default),
            edge=QColor(current_theme.edge),
            vertex_normal=QColor(current_theme.vertex_normal),
            vertex_selected=QColor(current_theme.vertex_selected),
            vertex_hovered=QColor(current_theme.vertex_hovered),
            center_normal=QColor(current_theme.center_normal),
            center_selected=QColor(current_theme.center_selected),
            center_hovered=QColor(current_theme.center_hovered),
            measure_line=QColor(current_theme.measure_line),
            measure_text_bg=QColor(current_theme.measure_text_bg),
            measure_text_fg=QColor(current_theme.measure_text_fg),
            measure_area_bg=QColor(current_theme.measure_area_bg),
            measure_area_fg=QColor(current_theme.measure_area_fg),
            measure_volume_bg=QColor(current_theme.measure_volume_bg),
            measure_volume_fg=QColor(current_theme.measure_volume_fg),
            axis_x=QColor(current_theme.axis_x),
            axis_y=QColor(current_theme.axis_y),
            axis_z=QColor(current_theme.axis_z),
            label_bg=QColor(current_theme.label_bg),
            label_fg=QColor(current_theme.label_fg),
            sphere_incircle=QColor(current_theme.sphere_incircle),
            sphere_midsphere=QColor(current_theme.sphere_midsphere),
            sphere_circumsphere=QColor(current_theme.sphere_circumsphere),
        )
        
        self._color_buttons = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Build the UI."""
        layout = QVBoxLayout(self)
        
        # Scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Background group
        self._add_color_group(scroll_layout, "Background", [
            ("background", "Background Color")
        ])
        
        # Geometry group
        self._add_color_group(scroll_layout, "Geometry Elements", [
            ("face_default", "Default Face Color"),
            ("edge", "Edge Color"),
            ("vertex_normal", "Vertex (Normal)"),
            ("vertex_selected", "Vertex (Selected)"),
            ("vertex_hovered", "Vertex (Hovered)"),
        ])
        
        # Center point group
        self._add_color_group(scroll_layout, "Center Point", [
            ("center_normal", "Center (Normal)"),
            ("center_selected", "Center (Selected)"),
            ("center_hovered", "Center (Hovered)"),
        ])
        
        # Measurement tool group
        self._add_color_group(scroll_layout, "Measurement Tool", [
            ("measure_line", "Line Color"),
            ("measure_text_bg", "Distance Label Background"),
            ("measure_text_fg", "Distance Label Text"),
            ("measure_area_bg", "Area Label Background"),
            ("measure_area_fg", "Area Label Text"),
            ("measure_volume_bg", "Volume Label Background"),
            ("measure_volume_fg", "Volume Label Text"),
        ])
        
        # Axes group
        self._add_color_group(scroll_layout, "Axes", [
            ("axis_x", "X-Axis"),
            ("axis_y", "Y-Axis"),
            ("axis_z", "Z-Axis"),
        ])
        
        # Labels group
        self._add_color_group(scroll_layout, "Labels", [
            ("label_bg", "Label Background"),
            ("label_fg", "Label Text"),
        ])
        
        # Spheres group
        self._add_color_group(scroll_layout, "Spheres", [
            ("sphere_incircle", "Incircle"),
            ("sphere_midsphere", "Midsphere"),
            ("sphere_circumsphere", "Circumsphere"),
        ])
        
        # Angle measurements group
        self._add_color_group(scroll_layout, "Angle Measurements", [
            ("angle_arc", "Angle Arc"),
            ("angle_text_bg", "Angle Text Background"),
            ("angle_text_fg", "Angle Text Foreground"),
        ])
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.accept)
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
    
    def _add_color_group(self, parent_layout: QVBoxLayout, title: str, color_items: list):
        """Add a color group box."""
        group = QGroupBox(title)
        grid = QGridLayout()
        
        row = 0
        for attr_name, label_text in color_items:
            label = QLabel(label_text)
            grid.addWidget(label, row, 0)
            
            color_btn = QPushButton()
            color_btn.setFixedSize(80, 30)
            color = getattr(self._theme, attr_name)
            color_btn.setStyleSheet(f"background-color: {color.name()};")
            color_btn.clicked.connect(lambda checked, attr=attr_name: self._pick_color(attr))
            
            self._color_buttons[attr_name] = color_btn
            grid.addWidget(color_btn, row, 1)
            
            row += 1
        
        group.setLayout(grid)
        parent_layout.addWidget(group)
    
    def _pick_color(self, attr_name: str):
        """Open color picker for an attribute."""
        current_color = getattr(self._theme, attr_name)
        color = QColorDialog.getColor(current_color, self, f"Pick {attr_name}")
        
        if color.isValid():
            setattr(self._theme, attr_name, color)
            self._color_buttons[attr_name].setStyleSheet(f"background-color: {color.name()};")
    
    def _reset_to_defaults(self):
        """Reset all colors to defaults."""
        self._theme = ColorTheme()
        for attr_name, btn in self._color_buttons.items():
            color = getattr(self._theme, attr_name)
            btn.setStyleSheet(f"background-color: {color.name()};")
    
    def get_theme(self) -> ColorTheme:
        """Get the configured theme."""
        return self._theme
