"""Geometry pillar hub - launcher interface for geometry tools.

Redesigned following the Visual Liturgy principles with tool-launcher grid pattern.
"""
from __future__ import annotations

import os
from typing import Callable, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QGraphicsDropShadowEffect, QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap, QPainter, QBrush

from shared.ui import WindowManager
from .advanced_scientific_calculator_window import AdvancedScientificCalculatorWindow
from .calculator.calculator_window import GeometryCalculatorWindow
from .polygonal_number_window import PolygonalNumberWindow
from .experimental_star_window import ExperimentalStarWindow
from .figurate_3d_window import Figurate3DWindow
from .geometry_definitions import CATEGORY_DEFINITIONS, SOLID_VIEWER_CONFIG
from .geometry3d.window3d import Geometry3DWindow
from .esoteric_wisdom_window import EsotericWisdomWindow
from .shape_picker_dialog import ShapePickerDialog


class GeometryHub(QWidget):
    """Hub widget for Geometry pillar - displays available tools.
    
    Follows the Visual Liturgy principles with clean tool-launcher grid.
    """
    
    def __init__(self, window_manager: WindowManager):
        """Initialize the Geometry hub.
        
        Args:
            window_manager: Shared window manager instance
        """
        super().__init__()
        self.window_manager = window_manager
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the hub interface with tool-launcher grid."""
        # Apply Nano Banana background texture to the main widget
        self.setObjectName("GeometryHub")
        self._apply_background_texture(self)
        
        # Main scroll area with transparent background
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("GeometryScroll")
        scroll.setStyleSheet("""
            QScrollArea#GeometryScroll { 
                border: none; 
                background: transparent; 
            }
            QScrollArea#GeometryScroll > QWidget > QWidget {
                background: transparent;
            }
        """)
        
        # Container (transparent to show parent's background)
        container = QWidget()
        container.setObjectName("GeometryContainer")
        container.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(container)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 32, 40, 40)

        # Header section (The Sigil)
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Geometry")
        title_label.setStyleSheet("""
            QLabel {
                color: #0f172a;
                font-size: 28pt;
                font-weight: 900;
                letter-spacing: -1px;
                background: transparent;
            }
        """)
        header_layout.addWidget(title_label)

        desc_label = QLabel("Sacred shapes, from perfect circles to multidimensional solids")
        desc_label.setStyleSheet("""
            QLabel {
                color: #334155;
                font-size: 11pt;
                background: transparent;
            }
        """)
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header)

        # Tools grid (The Catalyst Array)
        tools = [
            # 2D Shapes
            ("◯", "Circles & Curves", "Circle, Ellipse, Annulus, Crescent, Rose", "#3b82f6", 
             lambda: self._open_category_picker("Circles")),
            ("△", "Triangles", "All triangle types and general solver", "#10b981", 
             lambda: self._open_category_picker("Triangles")),
            ("▭", "Quadrilaterals", "Squares, rectangles, and beyond", "#f97316", 
             lambda: self._open_category_picker("Quadrilaterals")),
            ("⬢", "Regular Polygons", "Pentagon through Dodecagon and n-gon solver", "#06b6d4", 
             lambda: self._open_category_picker("Polygons")),
            ("☥", "Sacred Geometry", "Vesica Piscis, Seed of Life, Vault of Hestia", "#8b5cf6", 
             lambda: self._open_category_picker("Sacred Geometry")),
            # 3D Solids
            ("⌂", "Pyramids", "Tapered solids from sacred bases", "#ec4899", 
             lambda: self._open_category_picker("Pyramids")),
            ("▱", "Prisms", "Uniform cross-section solids", "#14b8a6", 
             lambda: self._open_category_picker("Prisms")),
            ("⧖", "Antiprisms", "Twisted twin-base solids", "#f43f5e", 
             lambda: self._open_category_picker("Antiprisms")),
            ("◆", "Platonic Solids", "Five perfect 3D symmetries", "#eab308", 
             lambda: self._open_category_picker("Platonic Solids")),
            ("⬡", "Archimedean Solids", "Truncated and snub polyhedra", "#a855f7", 
             lambda: self._open_category_picker("Archimedean Solids")),
            ("🌐", "Curves & Surfaces", "Sphere, Cylinder, Cone, Torus", "#0ea5e9", 
             lambda: self._open_category_picker("Curves & Surfaces")),
            # Tools
            ("∑", "Scientific Calculator", "Advanced mathematical calculator", "#64748b", 
             self._open_advanced_scientific_calculator),
            ("▲", "Polygonal Numbers", "Figurate number visualizer", "#f59e0b", 
             self._open_polygonal_number_visualizer),
            ("☆", "Star Numbers", "Experimental star polygon viewer", "#7c3aed", 
             self._open_experimental_star_visualizer),
            ("🎲", "3D Figurate", "Three-dimensional figurate numbers", "#0d9488", 
             self._open_figurate_3d_visualizer),
            # Wisdom
            ("📜", "Esoteric Wisdom", "Sacred meanings of geometric forms", "#9333ea", 
             self._open_esoteric_wisdom),
        ]

        grid = QGridLayout()
        grid.setSpacing(16)
        
        for i, (icon, title, desc, color, callback) in enumerate(tools):
            card = self._create_tool_card(icon, title, desc, color, callback)
            grid.addWidget(card, i // 3, i % 3)
        
        layout.addLayout(grid)
        
        # Coming soon section
        coming_soon = QLabel("Coming Soon: Net Explorer • Shape Detection • Golden Ratio Analyzer")
        coming_soon.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 10pt;
                padding: 20px;
                background: transparent;
            }
        """)
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(coming_soon)
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _apply_background_texture(self, widget: QWidget):
        """Apply the Nano Banana substrate texture at 15% opacity."""
        # Get the path to the background image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(current_dir, "assets", "geometry_background.png")
        
        if os.path.exists(bg_path):
            # Apply as stylesheet - the image is the substrate (Level 0)
            widget.setStyleSheet(f"""
                QWidget#GeometryHub {{
                    background-color: #f8fafc;
                    background-image: url("{bg_path}");
                    background-repeat: repeat;
                    background-position: center;
                }}
            """)
        else:
            # Fallback to solid Cloud Slate
            widget.setStyleSheet("""
                QWidget#GeometryHub {
                    background-color: #f8fafc;
                }
            """)
    
    def _create_tool_card(self, icon: str, title: str, description: str, 
                          accent_color: str, callback) -> QFrame:
        """Create a modern tool card following Visual Liturgy.
        
        The card is a Marble Tablet (Level 1) floating above the substrate.
        """
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #cbd5e1;
                border-radius: 24px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f5f9);
                border-color: {accent_color};
            }}
        """)
        card.setMinimumSize(200, 140)
        card.setMaximumHeight(160)
        
        # Liturgical shadow (Aura)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 25))  # Black @ 10%
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        
        # Icon with accent background
        icon_container = QLabel(icon)
        icon_container.setFixedSize(48, 48)
        icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.setStyleSheet(f"""
            QLabel {{
                background: {accent_color}20;
                border-radius: 10px;
                font-size: 22pt;
            }}
        """)
        layout.addWidget(icon_container)
        
        # Title (The Command - H3)
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #0f172a;
                font-size: 13pt;
                font-weight: 800;
                background: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # Description (The Scripture)
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #334155;
                font-size: 9pt;
                background: transparent;
            }
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # Click handler
        card.mousePressEvent = lambda e: callback()
        
        return card
    
    def _open_category_picker(self, category_name: str):
        """Open a shape picker window for the given category.
        
        Uses a custom Visual Liturgy-styled dialog with shape cards.
        """
        # Find the category definition
        category = None
        for cat in CATEGORY_DEFINITIONS:
            if cat['name'] == category_name:
                category = cat
                break
        
        if not category:
            return
        
        # Open the custom shape picker dialog
        dialog = ShapePickerDialog(category, parent=self)
        dialog.shape_selected.connect(self._launch_shape)
        dialog.exec()
    
    def _launch_shape(self, shape_definition: dict):
        """Launch the appropriate window for a shape definition."""
        shape_type = shape_definition.get('type')
        factory = shape_definition.get('factory')
        polygon_sides = shape_definition.get('polygon_sides')
        solid_id = shape_definition.get('solid_id')
        status = shape_definition.get('status')
        
        # Handle "Coming Soon" items
        if status and not factory and not polygon_sides and shape_type not in {'regular_polygon', 'solid_viewer'}:
            return
        
        # Regular polygon by sides
        if polygon_sides:
            self._open_polygon_calculator(polygon_sides)
            return
        
        # Solid viewer
        if shape_type == 'solid_viewer' and solid_id:
            self._open_solid_viewer(solid_id)
            return
        
        # Custom polygon prompt
        if shape_type == 'regular_polygon_custom':
            self._prompt_custom_polygon()
            return
        
        # Polygonal numbers
        if shape_type == 'polygonal_numbers':
            self._open_polygonal_number_visualizer()
            return
        
        # Star numbers
        if shape_type == 'star_numbers':
            self._open_experimental_star_visualizer()
            return
        
        # Default factory shape
        if factory:
            self._open_shape_calculator(factory())
    
    def _open_shape_calculator(self, shape):
        """Open geometry calculator for a shape."""
        self.window_manager.open_window(
            window_type=f"geometry_{shape.name.lower().replace(' ', '_')}",
            window_class=GeometryCalculatorWindow,
            allow_multiple=True,
            shape=shape,
            window_manager=self.window_manager,
        )

    
    def _open_polygon_calculator(self, sides: int):
        """Open geometry calculator for regular polygon."""
        from ..services.polygon_shape import RegularPolygonShape
        shape = RegularPolygonShape(sides)
        self._open_shape_calculator(shape)
    
    def _prompt_custom_polygon(self):
        """Prompt for custom polygon sides and open calculator."""
        sides, ok = QInputDialog.getInt(
            self,
            "Regular n-gon",
            "Number of sides (n ≥ 3):",
            value=6,
            min=3,
            max=200,
        )
        if ok:
            self._open_polygon_calculator(sides)
    
    def _open_solid_viewer(self, solid_id: str):
        """Open 3D viewer for a solid."""
        config = SOLID_VIEWER_CONFIG.get(solid_id)
        if not config:
            return
        
        builder = config.get('builder')
        calculator_cls = config.get('calculator')
        calculator = calculator_cls() if calculator_cls else None
        payload = None
        
        if calculator is None and builder:
            result = builder()
            payload = getattr(result, 'payload', result)

        window = self.window_manager.open_window(
            window_type=f"geometry_{solid_id}_viewer",
            window_class=Geometry3DWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )
        
        if window:
            window.setWindowTitle(f"{config.get('title', solid_id.title())} • 3D Viewer")
            window.set_solid_context(title=config.get('title'), summary=config.get('summary'))
            if calculator is not None:
                window.set_calculator(calculator)
            else:
                window.set_payload(payload)
    
    def _open_advanced_scientific_calculator(self):
        """Open the standalone scientific calculator."""
        self.window_manager.open_window(
            window_type="advanced_scientific_calculator",
            window_class=AdvancedScientificCalculatorWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )
    
    def _open_polygonal_number_visualizer(self):
        """Open polygonal/centered polygonal number visualizer."""
        self.window_manager.open_window(
            window_type="polygonal_numbers",
            window_class=PolygonalNumberWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )
    
    def _open_experimental_star_visualizer(self):
        """Open generalized experimental star visualizer."""
        self.window_manager.open_window(
            window_type="experimental_stars",
            window_class=ExperimentalStarWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )
    
    def _open_figurate_3d_visualizer(self):
        """Open 3D figurate numbers visualizer."""
        self.window_manager.open_window(
            window_type="figurate_3d",
            window_class=Figurate3DWindow,
            allow_multiple=True,
            window_manager=self.window_manager,
        )
    
    def _open_esoteric_wisdom(self):
        """Open the Esoteric Wisdom window."""
        self.window_manager.open_window(
            window_type="esoteric_wisdom",
            window_class=EsotericWisdomWindow,
            allow_multiple=False,
            window_manager=self.window_manager,
        )
