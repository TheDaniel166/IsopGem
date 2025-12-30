"""Nested Heptagons Window - Golden Trisection Visualizer.

This window displays an interactive visualization of three nested
regular heptagons based on the Golden Trisection ratios.

Visual Liturgy compliant with:
- Marble Tablet panels with drop shadows
- Seeker/Accent color theming
- Temple voice for labels
"""
from __future__ import annotations

import math
from typing import Optional

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPen, QPolygonF, QBrush,
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QFrame, QLabel, QDoubleSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QTabWidget, QGridLayout,
    QGraphicsDropShadowEffect, QComboBox,
)

from shared.ui.theme import COLORS
from ..services.nested_heptagons_service import NestedHeptagonsService


class HeptagonCanvas(QWidget):
    """Canvas widget for rendering nested heptagons."""
    
    def __init__(self, service: NestedHeptagonsService, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.service = service
        self.setMinimumSize(400, 400)
        
        # Display options
        self.show_outer = True
        self.show_middle = True
        self.show_inner = True
        self.show_circumcircle = True
        self.show_incircle = True
        self.show_diagonals = False
        self.show_labels = True
        self.show_measurements = True
        
        # Colors
        self.outer_color = QColor(50, 50, 200)      # Deep blue
        self.middle_color = QColor(50, 150, 50)     # Forest green
        self.inner_color = QColor(200, 50, 50)      # Ruby red
        self.circumcircle_color = QColor(200, 200, 255, 150)
        self.incircle_color = QColor(255, 200, 200, 150)
    
    def paintEvent(self, event) -> None:
        """Paint the nested heptagons visualization."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(COLORS['surface']))
        
        # Calculate center and scale
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        
        outer_circumradius = self.service.outer_properties().circumradius
        scale = min(width, height) / (2.5 * outer_circumradius) if outer_circumradius > 0 else 1
        
        # Draw circumcircle (outer)
        if self.show_circumcircle:
            painter.setPen(QPen(self.circumcircle_color, 1))
            r = outer_circumradius * scale
            painter.drawEllipse(QPointF(center_x, center_y), r, r)
        
        # Draw incircle (outer)
        if self.show_incircle:
            painter.setPen(QPen(self.incircle_color, 1))
            r = self.service.outer_properties().inradius * scale
            painter.drawEllipse(QPointF(center_x, center_y), r, r)
        
        # Draw outer heptagon
        if self.show_outer:
            self._draw_heptagon(
                painter, center_x, center_y, scale,
                self.service.outer_vertices(),
                self.outer_color, "O"
            )
        
        # Draw middle heptagon
        if self.show_middle:
            self._draw_heptagon(
                painter, center_x, center_y, scale,
                self.service.middle_vertices(),
                self.middle_color, "M"
            )
        
        # Draw inner heptagon
        if self.show_inner:
            self._draw_heptagon(
                painter, center_x, center_y, scale,
                self.service.inner_vertices(),
                self.inner_color, "I"
            )
        
        painter.end()
    
    def _draw_heptagon(
        self, painter: QPainter, 
        cx: float, cy: float, scale: float,
        vertices, color: QColor, prefix: str
    ) -> None:
        """Draw a heptagon with optional labels."""
        polygon = QPolygonF()
        scaled_verts = []
        
        for v in vertices:
            x = cx + v.x * scale
            y = cy + v.y * scale
            polygon.append(QPointF(x, y))
            scaled_verts.append((x, y))
        
        # Draw polygon
        painter.setPen(QPen(color, 2))
        painter.drawPolygon(polygon)
        
        # Draw diagonals
        if self.show_diagonals:
            painter.setPen(QPen(color.lighter(150), 1, Qt.PenStyle.DashLine))
            for i in range(7):
                x1, y1 = scaled_verts[i]
                # Short diagonal (skip 1 vertex)
                j = (i + 2) % 7
                x2, y2 = scaled_verts[j]
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        
        # Draw vertex labels
        if self.show_labels:
            painter.setPen(QPen(color, 1))
            font = QFont("Georgia", 9)
            painter.setFont(font)
            
            for i, (x, y) in enumerate(scaled_verts):
                # Offset label outward
                v = vertices[i]
                mag = math.sqrt(v.x**2 + v.y**2)
                if mag > 0:
                    ox = v.x / mag * 15
                    oy = v.y / mag * 15
                    painter.drawText(int(x + ox), int(y + oy), f"{prefix}{i+1}")


class NestedHeptagonsWindow(QWidget):
    """Window for the Nested Heptagons Golden Trisection Calculator."""
    
    def __init__(self, parent: Optional[QWidget] = None, window_manager=None):
        super().__init__(parent)
        self.setWindowTitle("The Golden Trisection")
        self.setMinimumSize(1100, 700)
        
        self.service = NestedHeptagonsService()
        self._setup_ui()
        self._update_displays()
    
    def _setup_ui(self) -> None:
        """Build the UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Background
        self.setStyleSheet(f"""
            NestedHeptagonsWindow {{
                background: {COLORS['background']};
            }}
        """)
        
        # Header
        header = QLabel("⬡ The Golden Trisection ⬡")
        header.setFont(QFont("Georgia", 22, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {COLORS['seeker']}; padding: 8px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        subtitle = QLabel("Σ = 2.247  |  Ρ = 1.802  |  α = 0.247")
        subtitle.setFont(QFont("Georgia", 11))
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {COLORS['border']};
                width: 2px;
            }}
        """)
        
        # Left panel: Controls
        left_panel = self._create_control_panel()
        splitter.addWidget(left_panel)
        
        # Center: Canvas
        self.canvas = HeptagonCanvas(self.service)
        canvas_frame = self._wrap_in_tablet(self.canvas)
        splitter.addWidget(canvas_frame)
        
        # Right panel: Properties
        right_panel = self._create_properties_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([280, 500, 320])
        main_layout.addWidget(splitter, 1)
    
    def _wrap_in_tablet(self, widget: QWidget) -> QFrame:
        """Wrap a widget in a Visual Liturgy tablet with drop shadow."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect(frame)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 40))
        frame.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(widget)
        
        return frame
    
    def _create_control_panel(self) -> QFrame:
        """Create the left control panel."""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 40))
        panel.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(panel)
        
        # Input group
        input_group = QGroupBox("Primary Inputs")
        input_group.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
        input_group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['seeker']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }}
        """)
        input_layout = QFormLayout(input_group)
        
        # Middle edge input (primary driver)
        self.middle_edge_spin = QDoubleSpinBox()
        self.middle_edge_spin.setRange(0.01, 10000)
        self.middle_edge_spin.setValue(1.0)
        self.middle_edge_spin.setDecimals(4)
        self.middle_edge_spin.setSuffix(" units")
        self.middle_edge_spin.valueChanged.connect(self._on_middle_edge_changed)
        input_layout.addRow("Middle Edge:", self.middle_edge_spin)
        
        # Orientation
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItem("Vertex at Top", "vertex_top")
        self.orientation_combo.addItem("Side at Top", "side_top")
        self.orientation_combo.currentIndexChanged.connect(self._on_orientation_changed)
        input_layout.addRow("Orientation:", self.orientation_combo)
        
        layout.addWidget(input_group)
        
        # Visualization group
        viz_group = QGroupBox("Visualization")
        viz_group.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
        viz_group.setStyleSheet(input_group.styleSheet().replace(
            COLORS['seeker'], COLORS['accent']
        ))
        viz_layout = QGridLayout(viz_group)
        
        self.outer_check = QCheckBox("Outer Heptagon")
        self.outer_check.setChecked(True)
        self.outer_check.stateChanged.connect(self._update_canvas)
        viz_layout.addWidget(self.outer_check, 0, 0)
        
        self.middle_check = QCheckBox("Middle Heptagon")
        self.middle_check.setChecked(True)
        self.middle_check.stateChanged.connect(self._update_canvas)
        viz_layout.addWidget(self.middle_check, 0, 1)
        
        self.inner_check = QCheckBox("Inner Heptagon")
        self.inner_check.setChecked(True)
        self.inner_check.stateChanged.connect(self._update_canvas)
        viz_layout.addWidget(self.inner_check, 1, 0)
        
        self.circumcircle_check = QCheckBox("Circumcircle")
        self.circumcircle_check.setChecked(True)
        self.circumcircle_check.stateChanged.connect(self._update_canvas)
        viz_layout.addWidget(self.circumcircle_check, 1, 1)
        
        self.incircle_check = QCheckBox("Incircle")
        self.incircle_check.setChecked(True)
        self.incircle_check.stateChanged.connect(self._update_canvas)
        viz_layout.addWidget(self.incircle_check, 2, 0)
        
        self.diagonals_check = QCheckBox("Diagonals")
        self.diagonals_check.setChecked(False)
        self.diagonals_check.stateChanged.connect(self._update_canvas)
        viz_layout.addWidget(self.diagonals_check, 2, 1)
        
        self.labels_check = QCheckBox("Vertex Labels")
        self.labels_check.setChecked(True)
        self.labels_check.stateChanged.connect(self._update_canvas)
        viz_layout.addWidget(self.labels_check, 3, 0)
        
        layout.addWidget(viz_group)
        
        # Constants group
        const_group = QGroupBox("Sacred Ratios")
        const_group.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
        const_group.setStyleSheet(input_group.styleSheet())
        const_layout = QFormLayout(const_group)
        
        sigma_label = QLabel(f"{NestedHeptagonsService.SIGMA:.6f}")
        sigma_label.setToolTip("Long diagonal in unit-edge heptagon")
        const_layout.addRow("Σ (SIGMA):", sigma_label)
        
        rho_label = QLabel(f"{NestedHeptagonsService.RHO:.6f}")
        rho_label.setToolTip("Short diagonal in unit-edge heptagon")
        const_layout.addRow("Ρ (RHO):", rho_label)
        
        alpha_label = QLabel(f"{NestedHeptagonsService.ALPHA:.6f}")
        alpha_label.setToolTip("Nested heptagon edge ratio")
        const_layout.addRow("α (ALPHA):", alpha_label)
        
        layout.addWidget(const_group)
        layout.addStretch()
        
        return panel
    
    def _create_properties_panel(self) -> QFrame:
        """Create the right properties panel with tabs."""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 40))
        panel.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(panel)
        
        title = QLabel("Calculated Properties")
        title.setFont(QFont("Georgia", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['seeker']}; border: none;")
        layout.addWidget(title)
        
        # Tabs for each heptagon
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                background: transparent;
            }}
            QTabBar::tab {{
                background: {COLORS['surface']};
                color: {COLORS['text_secondary']};
                padding: 8px 16px;
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['primary_light']};
                color: {COLORS['text_primary']};
            }}
        """)
        
        # Create property displays
        self.outer_props = self._create_property_form()
        self.middle_props = self._create_property_form()
        self.inner_props = self._create_property_form()
        
        tabs.addTab(self.outer_props, "Outer")
        tabs.addTab(self.middle_props, "Middle")
        tabs.addTab(self.inner_props, "Inner")
        
        layout.addWidget(tabs)
        
        return panel
    
    def _create_property_form(self) -> QWidget:
        """Create a form showing heptagon properties."""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(8)
        
        labels = {}
        for prop in [
            "Edge Length", "Perimeter", "Area",
            "Short Diagonal", "Long Diagonal",
            "Inradius", "Circumradius",
            "Incircle Circ.", "Circumcircle Circ."
        ]:
            label = QLabel("—")
            label.setFont(QFont("Georgia", 10))
            label.setStyleSheet(f"color: {COLORS['text_primary']};")
            layout.addRow(f"{prop}:", label)
            labels[prop] = label
        
        widget.labels = labels
        return widget
    
    def _on_middle_edge_changed(self, value: float) -> None:
        """Handle middle edge input change."""
        self.service.middle_edge = value
        self._update_displays()
    
    def _on_orientation_changed(self) -> None:
        """Handle orientation change."""
        self.service.orientation = self.orientation_combo.currentData()
        self.canvas.update()
    
    def _update_canvas(self) -> None:
        """Update canvas display options."""
        self.canvas.show_outer = self.outer_check.isChecked()
        self.canvas.show_middle = self.middle_check.isChecked()
        self.canvas.show_inner = self.inner_check.isChecked()
        self.canvas.show_circumcircle = self.circumcircle_check.isChecked()
        self.canvas.show_incircle = self.incircle_check.isChecked()
        self.canvas.show_diagonals = self.diagonals_check.isChecked()
        self.canvas.show_labels = self.labels_check.isChecked()
        self.canvas.update()
    
    def _update_displays(self) -> None:
        """Update all property displays."""
        self._update_property_display(self.outer_props, self.service.outer_properties())
        self._update_property_display(self.middle_props, self.service.middle_properties())
        self._update_property_display(self.inner_props, self.service.inner_properties())
        self.canvas.update()
    
    def _update_property_display(self, widget: QWidget, props) -> None:
        """Update a property form with new values."""
        labels = widget.labels
        labels["Edge Length"].setText(f"{props.edge_length:.6f}")
        labels["Perimeter"].setText(f"{props.perimeter:.6f}")
        labels["Area"].setText(f"{props.area:.6f}")
        labels["Short Diagonal"].setText(f"{props.short_diagonal:.6f}")
        labels["Long Diagonal"].setText(f"{props.long_diagonal:.6f}")
        labels["Inradius"].setText(f"{props.inradius:.6f}")
        labels["Circumradius"].setText(f"{props.circumradius:.6f}")
        labels["Incircle Circ."].setText(f"{props.incircle_circumference:.6f}")
        labels["Circumcircle Circ."].setText(f"{props.circumcircle_circumference:.6f}")
