"""Geometry pillar hub - launcher interface for geometry tools."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QFrame, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shared.ui import WindowManager
from .geometry_calculator_window import GeometryCalculatorWindow
from ..services import (
    CircleShape,
    SquareShape,
    RectangleShape,
    EquilateralTriangleShape,
    RightTriangleShape,
    RegularPolygonShape
)


class GeometryHub(QWidget):
    """Hub widget for Geometry pillar - displays available tools."""
    
    def __init__(self, window_manager: WindowManager):
        """
        Initialize the Geometry hub.
        
        Args:
            window_manager: Shared window manager instance
        """
        super().__init__()
        self.window_manager = window_manager
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the hub interface."""
        # Set white background
        self.setStyleSheet("background-color: #ffffff;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title section
        title_label = QLabel("📐 Geometry")
        title_label.setStyleSheet("""
            color: #000000;
            font-size: 32pt;
            font-weight: 700;
            letter-spacing: -1px;
            background-color: transparent;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Calculate properties of geometric shapes with interactive visualizations"
        )
        desc_label.setStyleSheet("""
            color: #374151;
            font-size: 13pt;
            margin-top: 4px;
            margin-bottom: 16px;
            background-color: transparent;
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        layout.addSpacing(20)
        
        # Shapes section
        shapes_label = QLabel("Select a Shape")
        shapes_label.setStyleSheet("""
            color: #000000;
            font-size: 18pt;
            font-weight: 700;
            margin-bottom: 12px;
            background-color: transparent;
        """)
        layout.addWidget(shapes_label)
        
        # Shape buttons grid
        shapes_grid = QGridLayout()
        shapes_grid.setSpacing(20)
        shapes_grid.setContentsMargins(0, 0, 0, 0)
        
        # Row 0: Basic Shapes
        circle_btn = self._create_shape_button(
            "⭕ Circle",
            "Radius, diameter, circumference, area",
            lambda: self._open_shape_calculator(CircleShape())
        )
        shapes_grid.addWidget(circle_btn, 0, 0)
        
        square_btn = self._create_shape_button(
            "🟦 Square",
            "Side, perimeter, area, diagonal",
            lambda: self._open_shape_calculator(SquareShape())
        )
        shapes_grid.addWidget(square_btn, 0, 1)
        
        rectangle_btn = self._create_shape_button(
            "▭ Rectangle",
            "Length, width, perimeter, area, diagonal",
            lambda: self._open_shape_calculator(RectangleShape())
        )
        shapes_grid.addWidget(rectangle_btn, 0, 2)
        
        # Row 1: Triangles & Polygons
        eq_triangle_btn = self._create_shape_button(
            "🔺 Equilateral Triangle",
            "Side, height, area, perimeter, radii",
            lambda: self._open_shape_calculator(EquilateralTriangleShape())
        )
        shapes_grid.addWidget(eq_triangle_btn, 1, 0)
        
        right_triangle_btn = self._create_shape_button(
            "📐 Right Triangle",
            "Base, height, hypotenuse, area",
            lambda: self._open_shape_calculator(RightTriangleShape())
        )
        shapes_grid.addWidget(right_triangle_btn, 1, 1)
        
        polygon_btn = self._create_polygon_button()
        shapes_grid.addWidget(polygon_btn, 1, 2)
        
        layout.addLayout(shapes_grid)
        
        # Spacer to push everything to top
        layout.addStretch()
        
        # Status bar at bottom
        status_label = QLabel("Ready • Bidirectional calculations • Interactive viewport")
        status_label.setStyleSheet("""
            color: #64748b;
            font-size: 10pt;
            font-style: italic;
            background-color: transparent;
        """)
        layout.addWidget(status_label)
    
    def _create_shape_button(self, title: str, description: str, callback) -> QWidget:
        """Create a shape launcher button."""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                border-bottom: 4px solid #e2e8f0;
            }
            QFrame:hover {
                border-color: #3b82f6;
                border-bottom-color: #3b82f6;
                background-color: #f8fafc;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #1e293b;
            font-size: 14pt;
            font-weight: 700;
            border: none;
            background: transparent;
        """)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            color: #64748b;
            font-size: 10pt;
            border: none;
            background: transparent;
        """)
        desc_label.setMaximumHeight(40)
        layout.addWidget(desc_label)
        
        # Spacer
        layout.addStretch()
        
        # Launch button
        button = QPushButton("Open Calculator")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(callback)
        button.setStyleSheet("""
            QPushButton {
                background-color: #eff6ff;
                color: #2563eb;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: 600;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #dbeafe;
                color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #bfdbfe;
                color: #1e40af;
            }
        """)
        layout.addWidget(button)
        
        frame.setMinimumHeight(160)
        frame.setMaximumHeight(180)
        
        return frame
    
    def _create_polygon_button(self) -> QWidget:
        """Create special polygon button with sides selector."""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                border-bottom: 4px solid #e2e8f0;
            }
            QFrame:hover {
                border-color: #3b82f6;
                border-bottom-color: #3b82f6;
                background-color: #f8fafc;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("⬢ Regular Polygon")
        title_label.setStyleSheet("""
            color: #1e293b;
            font-size: 14pt;
            font-weight: 700;
            border: none;
            background: transparent;
        """)
        layout.addWidget(title_label)
        
        # Sides selector
        sides_layout = QHBoxLayout()
        sides_layout.setSpacing(8)
        
        sides_label = QLabel("Sides:")
        sides_label.setStyleSheet("""
            color: #64748b;
            font-size: 10pt;
            border: none;
            background: transparent;
        """)
        sides_layout.addWidget(sides_label)
        
        self.polygon_sides_spin = QSpinBox()
        self.polygon_sides_spin.setMinimum(3)
        self.polygon_sides_spin.setMaximum(20)
        self.polygon_sides_spin.setValue(6)
        self.polygon_sides_spin.setStyleSheet("""
            QSpinBox {
                padding: 4px 8px;
                font-size: 11pt;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                background: white;
                min-width: 60px;
            }
            QSpinBox:focus {
                border-color: #3b82f6;
            }
        """)
        sides_layout.addWidget(self.polygon_sides_spin)
        sides_layout.addStretch()
        layout.addLayout(sides_layout)
        
        # Spacer
        layout.addStretch()
        
        # Launch button
        button = QPushButton("Open Calculator")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(self._open_polygon_calculator)
        button.setStyleSheet("""
            QPushButton {
                background-color: #eff6ff;
                color: #2563eb;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #dbeafe;
                color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #bfdbfe;
                color: #1e40af;
            }
        """)
        layout.addWidget(button)
        
        frame.setMinimumHeight(160)
        frame.setMaximumHeight(180)
        
        return frame
    
    def _open_shape_calculator(self, shape):
        """Open geometry calculator for a shape."""
        self.window_manager.open_window(
            window_type=f"geometry_{shape.name.lower().replace(' ', '_')}",
            window_class=GeometryCalculatorWindow,
            allow_multiple=True,
            shape=shape
        )
    
    def _open_polygon_calculator(self):
        """Open geometry calculator for regular polygon."""
        sides = self.polygon_sides_spin.value()
        shape = RegularPolygonShape(num_sides=sides)
        self._open_shape_calculator(shape)
