"""Nested Heptagons Window - Golden Trisection Visualizer.

This window displays an interactive visualization of N nested
regular heptagons (default 7) based on the Golden Trisection ratios.

@RiteExempt: Visual Liturgy
Note: This window is a "Visual Visualization Instrument". It intentionally uses
bespoke styling and semantic coloring (Gold as signal, negative space darkness)
and is exempt from standard Visual Liturgy token enforcement. The geometry and
color are content, not chrome.

Features:
- Sevenfold planetary cascade (Moon -> Mercury -> Venus -> Sun -> Mars -> Jupiter -> Saturn)
- Bidirectional property solving (set any property of any layer)
- Zoom/pan canvas with mouse wheel and drag
- Individual layer visibility controls

Note: This module is EXEMPT from the Canon DSL migration (ADR-010).
It functions as a specialized laboratory tool with complex interdependent 
state (Golden Trisection) and custom visualization requirements that 
generic Canon Realizers cannot easily replicate.
"""
from __future__ import annotations

import math
import random
from typing import Optional, List

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPen, QPolygonF, QBrush, QWheelEvent,
    QMouseEvent, QTransform, QAction,
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QFrame, QLabel, QDoubleSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QListWidget, QListWidgetItem, 
    QStackedWidget, QGridLayout, QPushButton,
    QGraphicsDropShadowEffect, QComboBox, QScrollArea, QMenu,
)

from shared.ui.theme import COLORS
from shared.signals.navigation_bus import navigation_bus
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
        self._scale = 1.0
        self._pan_offset = QPointF(0, 0)
        self._last_pan_pos = QPointF(0, 0)
        self._panning = False
        
        # Display options
        self.layer_visibility: List[bool] = [True] * service.num_layers
        self.show_circumcircle = True
        self.show_incircle = True
        self.show_short_diagonals = False
        self.show_long_diagonals = False
        self.show_labels = True
        
        # Generate random star field (astronomical background)
        self._stars: List[tuple[float, float, float]] = []
        for _ in range(200):  # 200 stars
            x = random.random()
            y = random.random()
            brightness = random.uniform(0.3, 1.0)
            self._stars.append((x, y, brightness))
        
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._transform = QTransform()
        
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
        
        # Clamp zoom level - EXPANDED RANGE for all 7 layers
        # Zoom out to 0.05 (5%) to see all outer layers
        # Zoom in to 7500 (750000%) to see the innermost Moon layer in full detail
        if 0.05 <= new_scale <= 7500.0:
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
            self.setCursor(Qt.CursorShape.CrossCursor)
    
    def reset_view(self) -> None:
        """Reset zoom and pan to default."""
        self._scale = 1.0
        self._pan_offset = QPointF(0, 0)
        self.update()
    
    def paintEvent(self, event) -> None:  # type: ignore[reportIncompatibleMethodOverride, reportMissingParameterType, reportUnknownParameterType]
        """Paint the nested heptagons visualization with zoom/pan."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background - Deep Geometric Void with star field
        painter.fillRect(self.rect(), QColor("#0a0a12"))
        
        # Draw astronomical star field
        width = self.width()
        height = self.height()
        for star_x, star_y, brightness in self._stars:
            x = int(star_x * width)
            y = int(star_y * height)
            size = 1 if brightness < 0.6 else 2
            alpha = int(brightness * 255)
            painter.setPen(QPen(QColor(255, 255, 255, alpha), size))
            painter.drawPoint(x, y)
        
        # Calculate center and apply transform
        center_x = width / 2 + self._pan_offset.x()
        center_y = height / 2 + self._pan_offset.y()
        
        # Get outermost layer circumradius for scaling
        outermost_props = self.service.layer_properties(self.service.num_layers)
        outer_circumradius = outermost_props.circumradius
        base_scale = min(width, height) / (2.5 * outer_circumradius) if outer_circumradius > 0 else 1
        scale = base_scale * self._scale
        
        # Draw circumcircle (outermost layer)
        if self.show_circumcircle:
            painter.setPen(QPen(QColor(255, 255, 255, 40), 1, Qt.PenStyle.DashLine))
            r = outer_circumradius * scale
            painter.drawEllipse(QPointF(center_x, center_y), r, r)
        
        # Draw incircle (outermost layer)
        # Draw incircle (outermost layer)
        if self.show_incircle:
            painter.setPen(QPen(QColor(255, 255, 255, 40), 1, Qt.PenStyle.DotLine))
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
        
        # Draw sacred geometry border frame
        frame_color = QColor("#D4AF37")  # Gold
        frame_color.setAlpha(80)
        painter.setPen(QPen(frame_color, 2))
        painter.drawRect(2, 2, width - 4, height - 4)
        
        # Draw zoom indicator in bottom-right
        zoom_text = f"Zoom: {self._scale:.2f}x"
        painter.setPen(QPen(QColor("#94A3B8"), 1))
        painter.setFont(QFont("Arial", 9))
        text_rect = painter.fontMetrics().boundingRect(zoom_text)
        bg_rect = text_rect.adjusted(-6, -3, 6, 3)
        bg_rect.moveTo(width - bg_rect.width() - 10, height - bg_rect.height() - 10)
        
        bg_color = QColor("#1a1a2e")
        bg_color.setAlpha(180)
        painter.fillRect(bg_rect, bg_color)
        painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, zoom_text)
        
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
        
        # Draw short diagonals (skip 1 vertex, connects i to i+2)
        if self.show_short_diagonals:
            painter.setPen(QPen(color.lighter(150), 1, Qt.PenStyle.DashLine))
            for i in range(7):
                x1, y1 = scaled_verts[i]
                j = (i + 2) % 7  # Short diagonal
                x2, y2 = scaled_verts[j]
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))  # type: ignore[reportUnknownArgumentType]
        
        # Draw long diagonals (skip 2 vertices, connects i to i+3)
        if self.show_long_diagonals:
            painter.setPen(QPen(color.lighter(180), 1.5, Qt.PenStyle.DashDotLine))
            for i in range(7):
                x1, y1 = scaled_verts[i]
                j = (i + 3) % 7  # Long diagonal
                x2, y2 = scaled_verts[j]
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))  # type: ignore[reportUnknownArgumentType]
        
        # Draw vertex labels
        if self.show_labels:
            painter.setPen(QPen(QColor("#D4AF37"), 1)) # Gold color for labels
            font = QFont("Arial", 9)
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
    
    def __init__(self, parent: Optional[QWidget] = None, window_manager=None):
        super().__init__(parent)
        self.setWindowTitle("The Sevenfold Golden Trisection")
        self.setMinimumSize(1200, 800)
        
        self.window_manager = window_manager
        self.service = NestedHeptagonsService(num_layers=7, canonical_edge_length=1.0)
        self._decimal_precision = 4  # Default decimal places
        
        self._setup_ui()
        self._update_displays()
    
    def _setup_ui(self) -> None:
        """Build the UI layout."""
        # Main container with title banner and footer
        container = QVBoxLayout(self)
        container.setContentsMargins(0, 0, 0, 0)
        container.setSpacing(0)
        
        # Title Banner
        title_banner = self._create_title_banner()
        container.addWidget(title_banner)
        
        # Main content area
        content_widget = QWidget()
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)
        
        # Background
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #0f0f13;
                color: #e0e0e0;
                font-family: "Segoe UI", Arial, sans-serif;
            }}
            QLabel {{
                background: transparent;
                border: none;
                color: #d0d0e0;
            }}
            QCheckBox {{
                color: #d0d0e0;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid #555;
                border-radius: 3px;
                background: #1a1a2e;
            }}
            QCheckBox::indicator:checked {{
                border-color: #D4AF37;
            }}
            QComboBox {{
                background-color: #1a1a2e;
                color: #f0f0f8;
                border: 1px solid #2a2a3e;
                border-radius: 4px;
                padding: 4px;
            }}
            QComboBox:hover {{
                border-color: #3a3a5e;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: #1a1a2e;
                color: #f0f0f8;
                selection-background-color: #2a3a4a;
                border: 1px solid #2a2a3e;
            }}
            QDoubleSpinBox {{
                background-color: #1a1a2e;
                color: #f0f0f8;
                border: 1px solid #2a2a3e;
                border-radius: 4px;
                padding: 4px;
            }}
            QDoubleSpinBox:hover {{
                border-color: #3a3a5e;
            }}
        """)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: transparent;
                width: 2px;
            }}
        """)
        
        
        # Center: Canvas (create FIRST so control panel can reference it)
        self.canvas = HeptagonCanvas(self.service)
        canvas_frame = self._wrap_in_tablet(self.canvas)
        
        # Left panel: Controls (references self.canvas)
        left_panel = self._create_control_panel()
        splitter.addWidget(left_panel)
        
        # Add canvas to splitter
        splitter.addWidget(canvas_frame)
        
        # Right panel: Properties
        right_panel = self._create_properties_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([300, 550, 350])
        main_layout.addWidget(splitter, 1)
        
        container.addWidget(content_widget)
        
        # Footer Status Bar
        self.footer_bar = self._create_footer_bar()
        container.addWidget(self.footer_bar)
        
        # Status label (referenced by _update_status_bar)
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 4px; font-size: 11px; background: #1a1a2e; color: #94A3B8;")
        container.addWidget(self.status_label)
    
    def contextMenuEvent(self, event) -> None:  # type: ignore[reportIncompatibleMethodOverride, reportMissingParameterType]
        """Handle right-click context menu (currently disabled - use spinbox context menus instead)."""
        # Main window context menu removed - right-click on specific spinboxes instead
        pass
    
    def _update_status_bar(self, row: int) -> None:
        """Update the footer status bar with current selection."""
        # Guard: status_label created late in _setup_ui
        if not hasattr(self, 'status_label'):
            return
        
        if row < 0 or row >= self.service.num_layers + 1:  # +1 for summary
            return
        
        if row < self.service.num_layers:
            # Regular layer
            planet = NestedHeptagonsService.PLANETARY_NAMES[row]
            metal = NestedHeptagonsService.METAL_NAMES[row] if row < len(NestedHeptagonsService.METAL_NAMES) else ""
            self.status_label.setText(f"Active | Layer {row + 1}: {planet} ({metal}) | Precision: {self._decimal_precision} decimals")
        else:
            # Summary tab
            self.status_label.setText(f"Active | Summary Tab (Aggregate Totals) | Precision: {self._decimal_precision} decimals")
    
    def _send_to_quadsert(self, value: float) -> None:
        """Send a specific value to Quadset Analysis via Navigation Bus."""
        if not self.window_manager:
            print("⚠️ Cannot send to Quadset: No window manager available")
            return
        
        # Round to whole number for Quadset
        value_rounded = int(round(value))
        
        navigation_bus.request_window.emit(
            "quadset_analysis",
            {
                "window_manager": self.window_manager,
                "initial_value": value_rounded
            }
        )
        
        print(f"📤 Sent value to Quadset Analysis: {value_rounded}")
        print(f"   Source: Sevenfold Nested Heptagons")
    
    def _wrap_in_tablet(self, widget: QWidget) -> QFrame:
        """Wrap a widget in a Visual Liturgy tablet with drop shadow."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: #0f0f13;
                border: 2px solid #D4AF37;
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        
        return frame
    
    def _create_title_banner(self) -> QFrame:
        """Create the title banner for the window."""
        banner = QFrame()
        banner.setFixedHeight(60)
        banner.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #1a1a2e, stop:0.5 #2a2a4e, stop:1 #1a1a2e);
                border-bottom: 1px solid #3a3a5e;
            }}
            QLabel {{
                color: #D4AF37;
                font-family: "Georgia", serif;
                font-size: 22px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QLabel#subtitle {{
                color: #94A3B8;
                font-size: 11px;
                font-weight: normal;
                letter-spacing: 0.5px;
            }}
        """)
        
        layout = QVBoxLayout(banner)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header = QLabel("⬡ The Sevenfold Golden Trisection ⬡")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        subtitle = QLabel("Σ = 2.247  |  Ρ = 1.802  |  α = 0.247  |  VII Planetary Spheres")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        return banner
    
    def _create_footer_bar(self) -> QFrame:
        """Create footer status bar."""
        footer = QFrame()
        footer.setFixedHeight(32)
        footer.setStyleSheet(f"""
            QFrame {{
                background: #1a1a2e;
                border-top: 1px solid #3a3a5e;
            }}
            QLabel {{
                color: #94A3B8;
                font-size: 10px;
                padding: 4px 12px;
            }}
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(8, 4, 8, 4)
        
        self.status_label = QLabel("Ready | Layer: Moon (Silver) | Precision: 4 decimals")
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        version_label = QLabel("Golden Trisection v1.0")
        layout.addWidget(version_label)
        
        return footer
    
    def _create_control_panel(self) -> QFrame:
        """Create the left control panel."""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background: #0f0f13;
                border: 2px solid #D4AF37;
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        
        # Common stylesheet for group boxes
        groupbox_style = f"""
            QGroupBox {{
                color: {COLORS['seeker']};
                border: none;
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
        
        # Planetary layer checkboxes with colored indicators
        self.layer_checks: List[QCheckBox] = []
        for i in range(self.service.num_layers):
            layer = i + 1
            planet_name = (NestedHeptagonsService.PLANETARY_NAMES[i] 
                          if i < len(NestedHeptagonsService.PLANETARY_NAMES) 
                          else f"Layer {layer}")
            check = QCheckBox(f"L{layer}: {planet_name}")
            check.setChecked(True)
            check.stateChanged.connect(self._update_canvas)
            
            # Apply planetary color to checkbox when checked
            if i < len(PLANETARY_COLORS):
                color = PLANETARY_COLORS[i]
                check.setStyleSheet(f"""
                    QCheckBox {{
                        color: #d0d0e0;
                    }}
                    QCheckBox::indicator:checked {{
                        background-color: {color.name()};
                        border: 2px solid {color.lighter(150).name()};
                    }}
                    QCheckBox:checked {{
                        color: {color.lighter(120).name()};
                        font-weight: bold;
                    }}
                """)
            
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
        orientation_label = QLabel("Orientation:")
        orientation_label.setStyleSheet("color: #9090a8;")
        orientation_layout.addWidget(orientation_label)
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItem("Vertex at Top", "vertex_top")
        self.orientation_combo.addItem("Side at Top", "side_top")
        self.orientation_combo.currentIndexChanged.connect(self._on_orientation_changed)
        orientation_layout.addWidget(self.orientation_combo)
        display_layout.addLayout(orientation_layout)
        
        # Decimal precision control
        precision_layout = QHBoxLayout()
        precision_label = QLabel("Decimal Places:")
        precision_label.setStyleSheet("color: #9090a8;")
        precision_layout.addWidget(precision_label)
        self.precision_spin = QDoubleSpinBox()
        self.precision_spin.setRange(0, 15)
        self.precision_spin.setValue(4)
        self.precision_spin.setDecimals(0)
        self.precision_spin.valueChanged.connect(self._on_precision_changed)
        precision_layout.addWidget(self.precision_spin)
        display_layout.addLayout(precision_layout)
        
        self.circumcircle_check = QCheckBox("Circumcircle")
        self.circumcircle_check.setChecked(False)
        self.circumcircle_check.stateChanged.connect(self._update_canvas)
        display_layout.addWidget(self.circumcircle_check)
        
        self.incircle_check = QCheckBox("Incircle")
        self.incircle_check.setChecked(False)
        self.incircle_check.stateChanged.connect(self._update_canvas)
        display_layout.addWidget(self.incircle_check)
        
        self.short_diagonals_check = QCheckBox("Short Diagonals (ρ)")
        self.short_diagonals_check.setChecked(False)
        self.short_diagonals_check.stateChanged.connect(self._update_canvas)
        display_layout.addWidget(self.short_diagonals_check)
        
        self.long_diagonals_check = QCheckBox("Long Diagonals (σ)")
        self.long_diagonals_check.setChecked(False)
        self.long_diagonals_check.stateChanged.connect(self._update_canvas)
        display_layout.addWidget(self.long_diagonals_check)
        
        self.labels_check = QCheckBox("Vertex Labels")
        self.labels_check.setChecked(False)
        self.labels_check.stateChanged.connect(self._update_canvas)
        display_layout.addWidget(self.labels_check)
        
        # Reset view button with golden hover glow
        reset_btn = QPushButton("↺ Recenter View")
        reset_btn_style = f"""
            QPushButton {{
                background-color: #2a3a4a;
                color: #4deeea;
                border: 1px solid #3a4a5a;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #3a4a5a;
                border: 2px solid #D4AF37;
            }}
            QPushButton:pressed {{
                background-color: #1a2a3a;
            }}
        """
        reset_btn.setStyleSheet(reset_btn_style)
        reset_btn.clicked.connect(self.canvas.reset_view)
        display_layout.addWidget(reset_btn)
        
        layout.addWidget(display_group)
        
        # Constants Reference with golden border
        const_group = QGroupBox("⭐ Golden Trisection Constants")
        const_group.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
        const_group.setStyleSheet(f"""
            QGroupBox {{
                color: #D4AF37;
                border: 2px solid #D4AF37;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 rgba(212, 175, 55, 0.1),
                                            stop:1 rgba(212, 175, 55, 0.05));
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background: #1a1a2e;
            }}
            QLabel {{
                color: #9090a8;
            }}
        """)
        const_layout = QFormLayout(const_group)
        
        sigma_row_label = QLabel("Σ (Long Diagonal):")
        sigma_row_label.setStyleSheet("color: #9090a8; font-weight: normal;")
        sigma_label = QLabel(f"{NestedHeptagonsService.SIGMA:.6f}")
        sigma_label.setStyleSheet("color: #6a6a7a; font-weight: bold; font-size: 12pt; background: transparent;")
        const_layout.addRow(sigma_row_label, sigma_label)
        
        rho_row_label = QLabel("ρ (Short Diagonal):")
        rho_row_label.setStyleSheet("color: #9090a8; font-weight: normal;")
        rho_label = QLabel(f"{NestedHeptagonsService.RHO:.6f}")
        rho_label.setStyleSheet("color: #6a6a7a; font-weight: bold; font-size: 12pt; background: transparent;")
        const_layout.addRow(rho_row_label, rho_label)
        
        alpha_row_label = QLabel("α (Nest Ratio):")
        alpha_row_label.setStyleSheet("color: #9090a8; font-weight: normal;")
        alpha_label = QLabel(f"{NestedHeptagonsService.ALPHA:.6f}")
        alpha_label.setStyleSheet("color: #6a6a7a; font-weight: bold; font-size: 12pt; background: transparent;")
        const_layout.addRow(alpha_row_label, alpha_label)
        
        layout.addWidget(const_group)
        layout.addStretch()
        
        return panel
    
    def _create_properties_panel(self) -> QFrame:
        """Create the right properties panel with vertical sidebar."""
        panel = QFrame()
        panel.setFixedWidth(360)
        panel.setStyleSheet(f"""
            QFrame {{
                background: #1a1a2e;
                border: 2px solid #D4AF37;
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(panel)

        
        title = QLabel("Calculated Properties")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: #D4AF37; letter-spacing: 1px; border: none; padding: 4px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Main content area with sidebar (List) and stack
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Sidebar (ListWidget)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(54)  # Compact width for symbols
        self.sidebar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                background: #0f0f13;
                border: none;
                border-right: 1px solid #1a1a2e;
                outline: none;
            }}
            QListWidget::item {{
                height: 48px;
                color: #b0b0c8;
                border-bottom: 1px solid #1a1a2e;
                border-radius: 0px;
                margin: 0px;
            }}
            QListWidget::item:selected {{
                color: #D4AF37;
                border-right: 3px solid #D4AF37;
            }}
            QListWidget::item:hover {{
                color: #e0e0e0;
            }}
        """)
        
        # Content Stack
        self.stack = QStackedWidget()
        
        # Planetary symbols for 7 layers (innermost to outermost)
        PLANETARY_SYMBOLS = ["☽", "☿", "♀", "☉", "♂", "♃", "♄"]

        # Define subtle metal/planet background colors (visible but dark)
        # Sequence: Moon, Mercury, Venus, Sun, Mars, Jupiter, Saturn
        LAYER_BG_COLORS = [
            "#2A2A38", # Moon (Silver/Blue tint)
            "#382A20", # Mercury (Orange/Bronze tint)
            "#203820", # Venus (Green/Copper tint)
            "#383418", # Sun (Gold/Yellow tint)
            "#382020", # Mars (Red/Iron tint)
            "#202038", # Jupiter (Blue/Tin tint)
            "#282030", # Saturn (Indigo/Lead tint)
        ]
        
        # Create property displays for all 7 layers
        self.layer_props: List[QWidget] = []
        for i in range(self.service.num_layers):
            layer = i + 1
            symbol = (PLANETARY_SYMBOLS[i] 
                     if i < len(PLANETARY_SYMBOLS) 
                     else f"L{layer}")
            
            prop_widget = self._create_property_form()
            self.layer_props.append(prop_widget)
            
            # CRITICAL: Set unique object name for this content widget
            widget_name = f"layer_prop_{i}"
            prop_widget.setObjectName(widget_name)
            
            # Apply metallic background color to the CONTENT widget, not the sidebar item
            if i < len(LAYER_BG_COLORS):
                prop_widget.setStyleSheet(f"""
                    QWidget#{widget_name} {{
                        background-color: {LAYER_BG_COLORS[i]};
                    }}
                """)
            
            # Add to stack
            self.stack.addWidget(prop_widget)
            
            # Add to sidebar
            item = QListWidgetItem(symbol)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFont(QFont("Segoe UI Symbol", 16))
            
            # Keep sidebar item background color for visual indicator
            if i < len(LAYER_BG_COLORS):
                 item.setBackground(QBrush(QColor(LAYER_BG_COLORS[i])))
            
            if i < len(NestedHeptagonsService.PLANETARY_NAMES):
                planet = NestedHeptagonsService.PLANETARY_NAMES[i]
                metal = NestedHeptagonsService.METAL_NAMES[i] if i < len(NestedHeptagonsService.METAL_NAMES) else ""
                tooltip = f"Layer {layer}: {planet} ({metal})"
                item.setToolTip(tooltip)
            
            self.sidebar.addItem(item)

        # -- ADD SUMMARY STAR TAB --
        self.summary_prop = self._create_property_form(read_only=True)
        
        # Set unique object name and apply slate gray background
        self.summary_prop.setObjectName("summary_prop_widget")
        self.summary_prop.setStyleSheet("""
            QWidget#summary_prop_widget {
                background-color: #2C3E50;
            }
        """)
        
        self.stack.addWidget(self.summary_prop)
        
        star_item = QListWidgetItem("★")
        star_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        star_item.setFont(QFont("Segoe UI Symbol", 18))  # Slightly larger star
        star_item.setToolTip("Total Aggregates (Sum of All Layers)")
        # Style the star differently to denote its special status
        star_item.setForeground(QColor(COLORS['accent']))
        # Also apply slate gray to the sidebar item
        star_item.setBackground(QBrush(QColor("#2C3E50")))
        
        self.sidebar.addItem(star_item)
            
        # Connect sidebar to stack and update status
        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.currentRowChanged.connect(self._update_status_bar)
        
        # Select first item
        self.sidebar.setCurrentRow(0)
        
        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.stack)
        layout.addLayout(content_layout)
        
        return panel
    
    def _create_property_form(self, read_only: bool = False) -> QWidget:
        """Create a form with editable property fields (bidirectional)."""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(8)
        
        spinboxes = {}
        # Property icons and map
        property_map = [
            ("⬡ Edge Length", "edge_length"),
            ("⬢ Perimeter", "perimeter"),
            ("▣ Area", "area"),
            ("⬗ Short Diagonal", "short_diagonal"),
            ("⬖ Long Diagonal", "long_diagonal"),
            ("⊙ Inradius", "inradius"),
            ("⊚ Circumradius", "circumradius"),
            ("○ Incircle Circ.", "incircle_circumference"),
            ("⊙ Circumcircle Circ.", "circumcircle_circumference"),
        ]
        
        # Add group separators
        group_idx = 0
        for idx, (display_name, prop_key) in enumerate(property_map):
            # Add separator after Area (lengths/perimeters vs circles/radii)
            if idx == 2 or idx == 4:
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setStyleSheet("background-color: #3a3a5e; margin: 8px 0;")
                separator.setFixedHeight(1)
                layout.addRow(separator)
            
            spinbox = QDoubleSpinBox()
            spinbox.setRange(0.0001, 1e15)  # Essentially unbounded
            spinbox.setDecimals(self._decimal_precision)
            spinbox.setFont(QFont("Arial", 10))
            # Explicitly set color here to override any conflicting sheets
            spinbox.setStyleSheet(f"""
                QDoubleSpinBox {{
                    color: #e0e0e0; 
                    background-color: #1a1a2e;
                    border: 1px solid #3a3a5e;
                    border-radius: 4px;
                    padding: 4px;
                }}
            """)
            # Store property key as object property for later retrieval
            spinbox.setProperty("prop_key", prop_key)
            
            # Select all text on focus for better UX
            if not read_only:
                from PyQt6.QtCore import QTimer
                def on_focus_in(event, sb=spinbox):
                    QDoubleSpinBox.focusInEvent(sb, event)
                    QTimer.singleShot(0, lambda: sb.lineEdit().selectAll() if sb.lineEdit() else None)
                spinbox.focusInEvent = on_focus_in
            
            if read_only:
                spinbox.setReadOnly(True)
                spinbox.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
                spinbox.setStyleSheet(f"color: {COLORS['accent']}; font-weight: bold; background: transparent; border: none;")
            
            # Override context menu to show only "Send to Quadset Analysis"
            spinbox.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            spinbox.customContextMenuRequested.connect(
                lambda pos, sb=spinbox: self._show_spinbox_context_menu(sb)
            )
            
            # Also set policy on internal lineEdit as it intercepts mouse clicks
            if spinbox.lineEdit():
                spinbox.lineEdit().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                spinbox.lineEdit().customContextMenuRequested.connect(
                    lambda pos, sb=spinbox: self._show_spinbox_context_menu(sb)
                )
            
            
            # Create styled label with bright text
            label = QLabel(f"{display_name}:")
            label.setStyleSheet("color: #b8c0d0; font-weight: bold; font-family: 'Arial';")
            layout.addRow(label, spinbox)
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
        
        # Update all spinboxes in all layer tabs AND summary tab
        all_widgets = self.layer_props + [self.summary_prop]
        for layer_widget in all_widgets:
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
        self.canvas.show_short_diagonals = self.short_diagonals_check.isChecked()
        self.canvas.show_long_diagonals = self.long_diagonals_check.isChecked()
        self.canvas.show_labels = self.labels_check.isChecked()
        self.canvas.update()
    
    def _update_displays(self) -> None:
        """Update all property displays for all layers."""
        # Disconnect signals temporarily to prevent feedback loops
        for i in range(self.service.num_layers):
            layer = i + 1
            props = self.service.layer_properties(layer)
            self._update_property_display(self.layer_props[i], props, layer)
            
        # Update summary aggregates
        agg_props = self.service.get_aggregate_properties()
        # For summary, we pass layer=0 or -1, but it's read-only anyway so signals aren't connected
        self._update_property_display(self.summary_prop, agg_props, layer=-1, read_only=True)
            
        self.canvas.update()
    
    def _update_property_display(self, widget: QWidget, props, layer: int, read_only: bool = False) -> None:
        """Update a property form with new values and connect bidirectional signals."""
        spinboxes = widget.spinboxes  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
        
        # Temporarily block signals to prevent feedback loops
        for spinbox in spinboxes.values():
            spinbox.blockSignals(True)
        
        # Update values (use exact keys from _create_property_form display_name)
        spinboxes["⬡ Edge Length"].setValue(props.edge_length)
        spinboxes["⬢ Perimeter"].setValue(props.perimeter)
        spinboxes["▣ Area"].setValue(props.area)
        spinboxes["⬗ Short Diagonal"].setValue(props.short_diagonal)
        spinboxes["⬖ Long Diagonal"].setValue(props.long_diagonal)
        spinboxes["⊙ Inradius"].setValue(props.inradius)
        spinboxes["⊚ Circumradius"].setValue(props.circumradius)
        spinboxes["○ Incircle Circ."].setValue(props.incircle_circumference)
        spinboxes["⊙ Circumcircle Circ."].setValue(props.circumcircle_circumference)
        
        # Reconnect signals for bidirectional solving (ONLY if not read_only)
        if not read_only:
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
    
    def _show_spinbox_context_menu(self, spinbox) -> None:  # type: ignore[reportMissingParameterType]
        """Show custom context menu for spinboxes."""
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
        
        # Standard action for all spinboxes: Send single value to Quadset
        send_action = QAction("⬢ Send to Quadset Analysis", self)
        send_action.triggered.connect(lambda: self._send_to_quadsert(spinbox.value()))
        menu.addAction(send_action)
        
        # Special action for SUMMARY spinboxes (read-only): Send components to Transitions
        if spinbox.isReadOnly():
            hept_action = QAction("⬡ Send to Heptagon Transitions", self)
            hept_action.triggered.connect(lambda: self._send_to_heptagon_transitions(spinbox.property("prop_key")))
            menu.addAction(hept_action)
        
        from PyQt6.QtGui import QCursor
        menu.exec(QCursor.pos())
        
    def _send_to_heptagon_transitions(self, prop_key: str) -> None:
        """Send the 7 constituent values of a summary total to Geometric Transitions."""
        if not self.window_manager:
            print("⚠️ Cannot send to Transitions: No window manager available")
            return
            
        # Gather the 7 individual layer values that make up this total
        all_props = self.service.all_properties()
        values = []
        for prop in all_props:
            # Get value from dataclass by key
            val = getattr(prop, prop_key)
            # Round to integer for TQ analysis (Transition logic requires ints)
            values.append(int(round(val)))
            
        print(f"📤 Sending to Heptagon Transitions: {values} (source: {prop_key})")
            
        navigation_bus.request_window.emit(
            "geometric_transitions",
            {
                "window_manager": self.window_manager,
                "initial_values": values
            }
        )