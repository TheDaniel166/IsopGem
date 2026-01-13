"""Nested Heptagons Window - Golden Trisection Visualizer.

This window displays an interactive visualization of N nested
regular heptagons (default 7) based on the Golden Trisection ratios.

Features:
- Sevenfold planetary cascade (Moon → Mercury → Venus → Sun → Mars → Jupiter → Saturn)
- Bidirectional property solving (set any property of any layer)
- Zoom/pan canvas with mouse wheel and drag
- Individual layer visibility controls

Visual Liturgy compliant with:
- Marble Tablet panels with drop shadows
- Seeker/Accent color theming
- Temple voice for labels
"""
from __future__ import annotations

import math
from typing import Optional, List

from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPen, QPolygonF, QBrush, QWheelEvent,
    QMouseEvent, QTransform, QAction,
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QFrame, QLabel, QDoubleSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QTabWidget, QGridLayout,
    QGraphicsDropShadowEffect, QComboBox, QScrollArea, QMenu,
)

from shared.ui.theme import COLORS
from ..services.nested_heptagons_service import NestedHeptagonsService


# Planetary color scheme for 7 layers (innermost to outermost)
PLANETARY_COLORS = [
    QColor(200, 200, 220),    # Moon - Silver/pale blue
    QColor(255, 165, 0),      # Mercury - Orange
    QColor(50, 205, 50),      # Venus - Green
    QColor(255, 215, 0),      # Sun - Gold
    QColor(220, 20, 60),      # Mars - Crimson
    QColor(100, 149, 237),    # Jupiter - Cornflower blue
    QColor(75, 0, 130),       # Saturn - Indigo/deep purple
]


class HeptagonCanvas(QWidget):
    """Canvas widget for rendering nested heptagons with zoom/pan support."""
    
    def __init__(self, service: NestedHeptagonsService, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.service = service
        self.setMinimumSize(400, 400)
        self.setMouseTracking(True)
        
        # Display options
        self.layer_visibility: List[bool] = [True] * service.num_layers
        self.show_circumcircle = True
        self.show_incircle = True
        self.show_diagonals = False
        self.show_labels = True
        self.show_measurements = True
        
        # Transform state for zoom/pan
        self._transform = QTransform()
        self._scale = 1.0
        self._pan_offset = QPointF(0, 0)
        self._panning = False
        self._last_pan_pos = QPointF()
        
        # Set focus policy to receive wheel events
        self.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
    
    def wheelEvent(self, event: Optional[QWheelEvent]) -> None:
        """Handle mouse wheel for zooming."""
        if event is None:
            return
        
        angle = event.angleDelta().y()
        if angle == 0:
            return
        
        # Zoom factor
        factor = 1.15 if angle > 0 else 1 / 1.15
        new_scale = self._scale * factor
        
        # Clamp zoom level
        if 0.1 <= new_scale <= 50.0:
            self._scale = new_scale
            self.update()
    
    def mousePressEvent(self, event: Optional[QMouseEvent]) -> None:
        """Start panning on middle mouse button."""
        if event and event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._last_pan_pos = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
    
    def mouseMoveEvent(self, event: Optional[QMouseEvent]) -> None:
        """Handle panning."""
        if event and self._panning:
            delta = event.position() - self._last_pan_pos
            self._pan_offset += delta
            self._last_pan_pos = event.position()
            self.update()
    
    def mouseReleaseEvent(self, event: Optional[QMouseEvent]) -> None:
        """Stop panning."""
        if event and event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def reset_view(self) -> None:
        """Reset zoom and pan to default."""
        self._scale = 1.0
        self._pan_offset = QPointF(0, 0)
        self.update()
    
    def paintEvent(self, event) -> None:  # type: ignore[reportIncompatibleMethodOverride, reportMissingParameterType, reportUnknownParameterType]
        """Paint the nested heptagons visualization with zoom/pan."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(COLORS['surface']))
        
        # Calculate center and apply transform
        width = self.width()
        height = self.height()
        center_x = width / 2 + self._pan_offset.x()
        center_y = height / 2 + self._pan_offset.y()
        
        # Get outermost layer circumradius for scaling
        outermost_props = self.service.layer_properties(self.service.num_layers)
        outer_circumradius = outermost_props.circumradius
        base_scale = min(width, height) / (2.5 * outer_circumradius) if outer_circumradius > 0 else 1
        scale = base_scale * self._scale
        
        # Draw circumcircle (outermost layer)
        if self.show_circumcircle:
            painter.setPen(QPen(QColor(200, 200, 255, 150), 1))
            r = outer_circumradius * scale
            painter.drawEllipse(QPointF(center_x, center_y), r, r)
        
        # Draw incircle (outermost layer)
        if self.show_incircle:
            painter.setPen(QPen(QColor(255, 200, 200, 150), 1))
            r = outermost_props.inradius * scale
            painter.drawEllipse(QPointF(center_x, center_y), r, r)
        
        # Draw all layers from outermost to innermost
        for layer_idx in range(self.service.num_layers - 1, -1, -1):
            layer = layer_idx + 1  # Convert to 1-indexed
            if not self.layer_visibility[layer_idx]:
                continue
            
            vertices = self.service.layer_vertices(layer)
            color = PLANETARY_COLORS[layer_idx] if layer_idx < len(PLANETARY_COLORS) else QColor(150, 150, 150)
            label = f"L{layer}"
            
            self._draw_heptagon(
                painter, center_x, center_y, scale,
                vertices, color, label, layer
            )
        
        painter.end()
    
    def _draw_heptagon(
        self, painter: QPainter, 
        cx: float, cy: float, scale: float,
        vertices, color: QColor, prefix: str, layer: int
    ) -> None:
        """Draw a heptagon with optional labels and diagonals."""
        polygon = QPolygonF()
        scaled_verts = []
        
        for v in vertices:
            x = cx + v.x * scale
            y = cy + v.y * scale
            polygon.append(QPointF(x, y))
            scaled_verts.append((x, y))
        
        # Draw filled polygon with transparency
        fill_color = QColor(color)
        fill_color.setAlpha(60)
        painter.setPen(QPen(color, 2))
        painter.setBrush(QBrush(fill_color))
        painter.drawPolygon(polygon)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Draw diagonals
        if self.show_diagonals:
            painter.setPen(QPen(color.lighter(150), 1, Qt.PenStyle.DashLine))
            for i in range(7):
                x1, y1 = scaled_verts[i]
                # Short diagonal (skip 1 vertex)
                j = (i + 2) % 7
                x2, y2 = scaled_verts[j]
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))  # type: ignore[reportUnknownArgumentType]
        
        # Draw vertex labels
        if self.show_labels:
            painter.setPen(QPen(color, 1))
            font = QFont("Georgia", 9)
            painter.setFont(font)
            
            for i, (x, y) in enumerate(scaled_verts):  # type: ignore[reportUnknownArgumentType, reportUnknownVariableType]
                # Offset label outward
                v = vertices[i]
                mag = math.sqrt(v.x**2 + v.y**2)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
                if mag > 0:
                    ox = v.x / mag * 15
                    oy = v.y / mag * 15
                    painter.drawText(int(x + ox), int(y + oy), f"{prefix}{i+1}")


class NestedHeptagonsWindow(QWidget):
    """Window for the Sevenfold Nested Heptagons Golden Trisection Calculator."""
    
    # Signal to communicate with Quadsert Analysis via service bus
    send_to_quadsert = pyqtSignal(dict)
    
    def __init__(self, parent: Optional[QWidget] = None, window_manager=None):
        super().__init__(parent)
        self.setWindowTitle("The Sevenfold Golden Trisection")
        self.setMinimumSize(1200, 800)
        
        self.service = NestedHeptagonsService(num_layers=7, canonical_edge_length=1.0)
        self._decimal_precision = 4  # Default decimal places
        
        # Set custom context menu policy
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
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
        header = QLabel("⬡ The Sevenfold Golden Trisection ⬡")
        header.setFont(QFont("Georgia", 22, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {COLORS['seeker']}; padding: 8px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        subtitle = QLabel("Σ = 2.247  |  Ρ = 1.802  |  α = 0.247  |  VII Planetary Spheres")
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
        
        splitter.setSizes([300, 550, 350])
        main_layout.addWidget(splitter, 1)
    
    def contextMenuEvent(self, event) -> None:  # type: ignore[reportIncompatibleMethodOverride, reportMissingParameterType]
        """Handle right-click context menu."""
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 20px;
                color: {COLORS['text_primary']};
            }}
            QMenu::item:selected {{
                background: {COLORS['primary_light']};
                color: {COLORS['seeker']};
            }}
        """)
        
        send_action = QAction("⬢ Send to Quadsert Analysis", self)
        send_action.triggered.connect(self._send_to_quadsert)
        menu.addAction(send_action)
        
        menu.exec(event.globalPos())
    
    def _send_to_quadsert(self) -> None:
        """Package current heptagon data and send to Quadsert Analysis (whole numbers only)."""
        # Gather all layer properties (rounded to whole numbers for Quadsert)
        layers_data = []
        for i in range(self.service.num_layers):
            layer = i + 1
            props = self.service.layer_properties(layer)
            layers_data.append({
                "layer": layer,
                "metal": NestedHeptagonsService.METAL_NAMES[i] if i < len(NestedHeptagonsService.METAL_NAMES) else f"Layer {layer}",
                "planet": NestedHeptagonsService.PLANETARY_NAMES[i] if i < len(NestedHeptagonsService.PLANETARY_NAMES) else f"Layer {layer}",
                "edge_length": round(props.edge_length),
                "perimeter": round(props.perimeter),
                "area": round(props.area),
                "short_diagonal": round(props.short_diagonal),
                "long_diagonal": round(props.long_diagonal),
                "inradius": round(props.inradius),
                "circumradius": round(props.circumradius),
            })
        
        # Package for Quadsert (ratios kept precise, measurements rounded)
        payload = {
            "source": "NestedHeptagons",
            "title": "Sevenfold Golden Trisection",
            "num_layers": self.service.num_layers,
            "canonical_layer": self.service.canonical_layer,
            "canonical_edge": round(self.service.canonical_edge),
            "ratios": {
                "sigma": NestedHeptagonsService.SIGMA,
                "rho": NestedHeptagonsService.RHO,
                "alpha": NestedHeptagonsService.ALPHA,
            },
            "layers": layers_data,
            "orientation": self.service.orientation,
        }
        
        # Emit signal to service bus
        self.send_to_quadsert.emit(payload)
        
        print(f"📤 Sent Sevenfold Heptagon data to Quadsert Analysis (whole numbers)")
        print(f"   Canonical layer: {self.service.canonical_layer} (Gold)")
        print(f"   Canonical edge: {round(self.service.canonical_edge)}")
        print(f"   Layers transmitted: {len(layers_data)}")
    
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
        
        # Common stylesheet for group boxes
        groupbox_style = f"""
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
        """
        
        # Layer visibility group (scrollable for 7 layers)
        viz_group = QGroupBox("Layer Visibility")
        viz_group.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
        viz_group.setStyleSheet(groupbox_style.replace(COLORS['seeker'], COLORS['accent']))
        viz_layout = QVBoxLayout(viz_group)
        
        # Planetary layer checkboxes
        self.layer_checks: List[QCheckBox] = []
        for i in range(self.service.num_layers):
            layer = i + 1
            planet_name = (NestedHeptagonsService.PLANETARY_NAMES[i] 
                          if i < len(NestedHeptagonsService.PLANETARY_NAMES) 
                          else f"Layer {layer}")
            check = QCheckBox(f"L{layer}: {planet_name}")
            check.setChecked(True)
            check.stateChanged.connect(self._update_canvas)
            viz_layout.addWidget(check)
            self.layer_checks.append(check)
        
        layout.addWidget(viz_group)
        
        # Display options group
        display_group = QGroupBox("Display Options")
        display_group.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
        display_group.setStyleSheet(groupbox_style)
        display_layout = QVBoxLayout(display_group)
        
        # Orientation
        orientation_layout = QHBoxLayout()
        orientation_layout.addWidget(QLabel("Orientation:"))
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItem("Vertex at Top", "vertex_top")
        self.orientation_combo.addItem("Side at Top", "side_top")
        self.orientation_combo.currentIndexChanged.connect(self._on_orientation_changed)
        orientation_layout.addWidget(self.orientation_combo)
        display_layout.addLayout(orientation_layout)
        
        # Decimal precision control
        precision_layout = QHBoxLayout()
        precision_layout.addWidget(QLabel("Decimal Places:"))
        self.precision_spin = QDoubleSpinBox()
        self.precision_spin.setRange(0, 15)
        self.precision_spin.setValue(4)
        self.precision_spin.setDecimals(0)
        self.precision_spin.valueChanged.connect(self._on_precision_changed)
        precision_layout.addWidget(self.precision_spin)
        display_layout.addLayout(precision_layout)
        
        self.circumcircle_check = QCheckBox("Circumcircle")
        self.circumcircle_check.setChecked(True)
        self.circumcircle_check.stateChanged.connect(self._update_canvas)
        display_layout.addWidget(self.circumcircle_check)
        
        self.incircle_check = QCheckBox("Incircle")
        self.incircle_check.setChecked(True)
        self.incircle_check.stateChanged.connect(self._update_canvas)
        display_layout.addWidget(self.incircle_check)
        
        self.diagonals_check = QCheckBox("Diagonals")
        self.diagonals_check.setChecked(False)
        self.diagonals_check.stateChanged.connect(self._update_canvas)
        display_layout.addWidget(self.diagonals_check)
        
        self.labels_check = QCheckBox("Vertex Labels")
        self.labels_check.setChecked(True)
        self.labels_check.stateChanged.connect(self._update_canvas)
        display_layout.addWidget(self.labels_check)
        
        # Reset view button
        reset_btn = QCheckBox("Reset View")  # Using QCheckBox as button for consistency
        reset_btn.setStyleSheet("font-weight: bold;")
        reset_btn.clicked.connect(lambda: self.canvas.reset_view())  # type: ignore[reportUnknownMemberType]
        display_layout.addWidget(reset_btn)
        
        layout.addWidget(display_group)
        
        # Constants group
        const_group = QGroupBox("Sacred Ratios")
        const_group.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
        const_group.setStyleSheet(groupbox_style)
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
        
        # Tabs for each layer with scrollable container (vertical orientation)
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.West)  # Vertical tabs on left
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                background: transparent;
                margin-left: 1px;
            }}
            QTabBar::tab {{
                background: {COLORS['surface']};
                color: {COLORS['text_secondary']};
                padding: 12px 8px;
                border: 1px solid {COLORS['border']};
                border-right: none;
                border-top-left-radius: 6px;
                border-bottom-left-radius: 6px;
                font-size: 10pt;
                font-weight: bold;
                min-width: 80px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['primary_light']};
                color: {COLORS['text_primary']};
                border-right: 2px solid {COLORS['seeker']};
            }}
        """)
        
        # Create property displays for all 7 layers with metal names
        self.layer_props: List[QWidget] = []
        for i in range(self.service.num_layers):
            layer = i + 1
            metal_name = (NestedHeptagonsService.METAL_NAMES[i] 
                         if i < len(NestedHeptagonsService.METAL_NAMES) 
                         else f"Layer {layer}")
            
            prop_widget = self._create_property_form()
            self.layer_props.append(prop_widget)
            tabs.addTab(prop_widget, metal_name)
        
        layout.addWidget(tabs)
        
        return panel
    
    def _create_property_form(self) -> QWidget:
        """Create a form with editable property fields (bidirectional)."""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(8)
        
        spinboxes = {}
        property_map = [
            ("Edge Length", "edge_length"),
            ("Perimeter", "perimeter"),
            ("Area", "area"),
            ("Short Diagonal", "short_diagonal"),
            ("Long Diagonal", "long_diagonal"),
            ("Inradius", "inradius"),
            ("Circumradius", "circumradius"),
            ("Incircle Circ.", "incircle_circumference"),
            ("Circumcircle Circ.", "circumcircle_circumference"),
        ]
        
        for display_name, prop_key in property_map:
            spinbox = QDoubleSpinBox()
            spinbox.setRange(0.0001, 1e15)  # Essentially unbounded
            spinbox.setDecimals(self._decimal_precision)
            spinbox.setFont(QFont("Georgia", 10))
            spinbox.setStyleSheet(f"color: {COLORS['text_primary']};")
            # Store property key as object property for later retrieval
            spinbox.setProperty("prop_key", prop_key)
            layout.addRow(f"{display_name}:", spinbox)
            spinboxes[display_name] = spinbox
        
        widget.spinboxes = spinboxes
        widget.property_map = dict(property_map)
        return widget
    
    def _on_orientation_changed(self) -> None:
        """Handle orientation change."""
        self.service.orientation = self.orientation_combo.currentData()
        self.canvas.update()
    
    def _on_precision_changed(self, value: float) -> None:
        """Handle decimal precision change."""
        precision = int(value)
        self._decimal_precision = precision
        
        # Update all spinboxes in all layer tabs
        for layer_widget in self.layer_props:
            spinboxes = layer_widget.spinboxes  # type: ignore[reportAttributeAccessIssue]
            for spinbox in spinboxes.values():
                current_value = spinbox.value()
                spinbox.setDecimals(precision)
                spinbox.setValue(current_value)  # Reapply to update display
    
    def _update_canvas(self) -> None:
        """Update canvas display options from UI controls."""
        # Update layer visibility
        for i, check in enumerate(self.layer_checks):
            self.canvas.layer_visibility[i] = check.isChecked()
        
        # Update display options
        self.canvas.show_circumcircle = self.circumcircle_check.isChecked()
        self.canvas.show_incircle = self.incircle_check.isChecked()
        self.canvas.show_diagonals = self.diagonals_check.isChecked()
        self.canvas.show_labels = self.labels_check.isChecked()
        self.canvas.update()
    
    def _update_displays(self) -> None:
        """Update all property displays for all layers."""
        # Disconnect signals temporarily to prevent feedback loops
        for i in range(self.service.num_layers):
            layer = i + 1
            props = self.service.layer_properties(layer)
            self._update_property_display(self.layer_props[i], props, layer)
        self.canvas.update()
    
    def _update_property_display(self, widget: QWidget, props, layer: int) -> None:
        """Update a property form with new values and connect bidirectional signals."""
        spinboxes = widget.spinboxes  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
        
        # Temporarily block signals to prevent feedback loops
        for spinbox in spinboxes.values():
            spinbox.blockSignals(True)
        
        # Update values
        spinboxes["Edge Length"].setValue(props.edge_length)
        spinboxes["Perimeter"].setValue(props.perimeter)
        spinboxes["Area"].setValue(props.area)
        spinboxes["Short Diagonal"].setValue(props.short_diagonal)
        spinboxes["Long Diagonal"].setValue(props.long_diagonal)
        spinboxes["Inradius"].setValue(props.inradius)
        spinboxes["Circumradius"].setValue(props.circumradius)
        spinboxes["Incircle Circ."].setValue(props.incircle_circumference)
        spinboxes["Circumcircle Circ."].setValue(props.circumcircle_circumference)
        
        # Reconnect signals for bidirectional solving
        for spinbox in spinboxes.values():
            spinbox.blockSignals(False)
            # Disconnect any existing connections
            try:
                spinbox.editingFinished.disconnect()
            except:
                pass
            # Connect to bidirectional solver with layer context (triggers on Enter or focus loss)
            spinbox.editingFinished.connect(lambda l=layer, sb=spinbox: self._on_property_changed(l, sb.property("prop_key"), sb.value()))
    
    def _on_property_changed(self, layer: int, prop_key: str, value: float) -> None:
        """Handle bidirectional property change from any spinbox."""
        try:
            self.service.set_layer_property(layer, prop_key, value)
            self._update_displays()
        except Exception as e:
            print(f"Error setting layer {layer} property {prop_key}: {e}")
    
    def _show_context_menu(self, pos) -> None:  # type: ignore[reportMissingParameterType]
        """Show custom context menu with only Send to Quadsert option."""
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 20px;
                color: {COLORS['text_primary']};
            }}
            QMenu::item:selected {{
                background: {COLORS['primary_light']};
                color: {COLORS['seeker']};
            }}
        """)
        
        send_action = QAction("⬢ Send to Quadsert Analysis", self)
        send_action.triggered.connect(self._send_to_quadsert)
        menu.addAction(send_action)
        
        menu.exec(self.mapToGlobal(pos))
