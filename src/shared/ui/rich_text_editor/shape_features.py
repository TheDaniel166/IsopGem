"""Shape insertion feature for the Rich Text Editor."""
from PyQt6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QColorDialog, QSpinBox, QGroupBox,
    QDialogButtonBox, QToolButton, QMenu, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
import qtawesome as qta

from .shape_item import (
    RectShapeItem, EllipseShapeItem, TriangleShapeItem,
    LineShapeItem, ArrowShapeItem, BaseShapeItem, PolygonShapeItem
)
from .shape_overlay import ShapeOverlay
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .editor import RichTextEditor


class ShapeButton(QPushButton):
    """A button showing a shape preview."""
    
    def __init__(self, shape_name: str, shape_class: type, parent=None):
        """
          init   logic.
        
        Args:
            shape_name: Description of shape_name.
            shape_class: Description of shape_class.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.shape_name = shape_name
        self.shape_class = shape_class
        self.setFixedSize(60, 50)
        self.setToolTip(shape_name)
        self._create_icon()
    
    def _create_icon(self):
        """Create a preview icon for the shape."""
        pixmap = QPixmap(50, 40)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor("#2563eb"))
        painter.setBrush(QColor("#dbeafe"))
        
        if self.shape_class == RectShapeItem:
            painter.drawRect(5, 5, 40, 30)
        elif self.shape_class == EllipseShapeItem:
            painter.drawEllipse(5, 5, 40, 30)
        elif self.shape_class == TriangleShapeItem:
            from PyQt6.QtGui import QPolygonF
            from PyQt6.QtCore import QPointF
            triangle = QPolygonF([
                QPointF(25, 5),
                QPointF(45, 35),
                QPointF(5, 35)
            ])
            painter.drawPolygon(triangle)
        elif self.shape_class == LineShapeItem:
            painter.drawLine(5, 20, 45, 20)
        elif self.shape_class == ArrowShapeItem:
            painter.drawLine(5, 20, 35, 20)
            # Arrow head
            from PyQt6.QtGui import QPainterPath
            path = QPainterPath()
            path.moveTo(45, 20)
            path.lineTo(35, 15)
            path.lineTo(35, 25)
            path.closeSubpath()
            painter.fillPath(path, QColor("#2563eb"))
        
        painter.end()
        self.setIcon(QIcon(pixmap))
        self.setIconSize(pixmap.size())


class PolygonConfigDialog(QDialog):
    """Dialog for configuring a polygon shape (n-gon or n-gram)."""
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Create Polygon")
        self.setModal(True)
        self._sides = 5
        self._skip = 1
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Preview area
        from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
        from PyQt6.QtCore import QRectF
        
        self.preview_scene = QGraphicsScene()
        self.preview_view = QGraphicsView(self.preview_scene)
        self.preview_view.setFixedSize(200, 200)
        self.preview_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(self.preview_view)
        
        # Sides control
        form = QGridLayout()
        form.addWidget(QLabel("Number of Sides:"), 0, 0)
        self.spin_sides = QSpinBox()
        self.spin_sides.setRange(3, 100)
        self.spin_sides.setValue(5)
        self.spin_sides.valueChanged.connect(self._on_sides_changed)
        form.addWidget(self.spin_sides, 0, 1)
        
        # Quick preset buttons
        presets_layout = QHBoxLayout()
        for n, name in [(3, "△"), (4, "□"), (5, "⬠"), (6, "⬡"), (7, "7"), (8, "8")]:
            btn = QPushButton(name)
            btn.setFixedWidth(35)
            btn.clicked.connect(lambda checked, sides=n: self._set_sides(sides))
            presets_layout.addWidget(btn)
        form.addLayout(presets_layout, 1, 0, 1, 2)
        
        # Star polygon (n-gram) controls
        form.addWidget(QLabel("Star Skip:"), 2, 0)
        self.spin_skip = QSpinBox()
        self.spin_skip.setRange(1, 2)
        self.spin_skip.setValue(1)
        self.spin_skip.setToolTip("1 = regular polygon, 2+ = star polygon")
        self.spin_skip.valueChanged.connect(self._on_skip_changed)
        form.addWidget(self.spin_skip, 2, 1)
        
        self.label_type = QLabel("Regular Pentagon")
        form.addWidget(self.label_type, 3, 0, 1, 2)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self._update_preview()
    
    def _set_sides(self, n: int):
        self.spin_sides.setValue(n)
    
    def _on_sides_changed(self, n: int):
        self._sides = n
        max_skip = (n - 1) // 2
        self.spin_skip.setMaximum(max(1, max_skip))
        if self._skip > max_skip:
            self.spin_skip.setValue(1)
        self._update_preview()
    
    def _on_skip_changed(self, k: int):
        self._skip = k
        self._update_preview()
    
    def _update_preview(self):
        """Update the preview polygon."""
        import math
        from PyQt6.QtGui import QPen, QBrush, QPainterPath
        from PyQt6.QtCore import QPointF
        from PyQt6.QtGui import QPolygonF
        
        self.preview_scene.clear()
        
        # Calculate vertices
        cx, cy = 100, 100
        radius = 80
        vertices = []
        for i in range(self._sides):
            angle = -math.pi / 2 + (2 * math.pi * i / self._sides)
            vx = cx + radius * math.cos(angle)
            vy = cy + radius * math.sin(angle)
            vertices.append(QPointF(vx, vy))
        
        if self._skip == 1:
            polygon = QPolygonF(vertices)
            self.preview_scene.addPolygon(
                polygon, 
                QPen(QColor("#2563eb"), 2),
                QBrush(QColor("#dbeafe"))
            )
        else:
            # Star polygon
            path = QPainterPath()
            n = len(vertices)
            visited = [False] * n
            start = 0
            
            while not all(visited):
                if not visited[start]:
                    path.moveTo(vertices[start])
                    current = start
                    while True:
                        visited[current] = True
                        next_idx = (current + self._skip) % n
                        path.lineTo(vertices[next_idx])
                        current = next_idx
                        if current == start:
                            break
                for i in range(n):
                    if not visited[i]:
                        start = i
                        break
            
            path.closeSubpath()
            self.preview_scene.addPath(
                path,
                QPen(QColor("#2563eb"), 2),
                QBrush(QColor("#dbeafe"))
            )
        
        # Update label
        names = {
            3: "Triangle", 4: "Square", 5: "Pentagon", 6: "Hexagon",
            7: "Heptagon", 8: "Octagon", 9: "Nonagon", 10: "Decagon",
            11: "Hendecagon", 12: "Dodecagon"
        }
        base_name = names.get(self._sides, f"{self._sides}-gon")
        if self._skip > 1:
            self.label_type.setText(f"Star {base_name} ({self._sides}/{self._skip})")
        else:
            self.label_type.setText(f"Regular {base_name}")
    
    def get_config(self) -> tuple[int, int]:
        """Return (sides, skip) configuration."""
        return (self._sides, self._skip)


class ShapePickerDialog(QDialog):
    """Dialog for selecting a shape to insert."""
    
    shape_selected = pyqtSignal(type)  # Emits shape class
    
    SHAPES = [
        ("Rectangle", RectShapeItem),
        ("Ellipse", EllipseShapeItem),
        ("Triangle", TriangleShapeItem),
        ("Line", LineShapeItem),
        ("Arrow", ArrowShapeItem),
    ]
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Insert Shape")
        self.setModal(True)
        self._selected_type: Optional[type] = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Shape grid
        grid = QGridLayout()
        grid.setSpacing(10)
        
        for i, (name, shape_class) in enumerate(self.SHAPES):
            btn = ShapeButton(name, shape_class)
            btn.clicked.connect(lambda checked, sc=shape_class: self._on_shape_clicked(sc))
            grid.addWidget(btn, i // 3, i % 3)
        
        layout.addLayout(grid)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _on_shape_clicked(self, shape_class: type):
        """Handle shape button click."""
        self._selected_type = shape_class
        self.accept()
    
    def get_selected_type(self) -> Optional[type]:
        """Return the selected shape type."""
        return self._selected_type


class ShapePropertiesDialog(QDialog):
    """Dialog for editing shape properties."""
    
    def __init__(self, shape: BaseShapeItem, parent=None):
        """
          init   logic.
        
        Args:
            shape: Description of shape.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.shape = shape
        self.setWindowTitle("Shape Properties")
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Colors group
        colors_group = QGroupBox("Colors")
        colors_layout = QGridLayout(colors_group)
        
        # Fill color
        colors_layout.addWidget(QLabel("Fill:"), 0, 0)
        self.btn_fill = QPushButton()
        self.btn_fill.setFixedSize(60, 25)
        self._update_color_button(self.btn_fill, self.shape.fill_color)
        self.btn_fill.clicked.connect(self._choose_fill_color)
        colors_layout.addWidget(self.btn_fill, 0, 1)
        
        # Stroke color
        colors_layout.addWidget(QLabel("Stroke:"), 1, 0)
        self.btn_stroke = QPushButton()
        self.btn_stroke.setFixedSize(60, 25)
        self._update_color_button(self.btn_stroke, self.shape.stroke_color)
        self.btn_stroke.clicked.connect(self._choose_stroke_color)
        colors_layout.addWidget(self.btn_stroke, 1, 1)
        
        # Stroke width
        colors_layout.addWidget(QLabel("Width:"), 2, 0)
        self.spin_width = QSpinBox()
        self.spin_width.setRange(1, 20)
        self.spin_width.setValue(int(self.shape.stroke_width))
        colors_layout.addWidget(self.spin_width, 2, 1)
        
        layout.addWidget(colors_group)
        
        # Buttons
        from PyQt6.QtWidgets import QDialogButtonBox
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _update_color_button(self, btn: QPushButton, color: QColor):
        """Update button to show color."""
        btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
    
    def _pick_color(self, current: QColor, title: str) -> QColor:
        """Show non-native color picker."""
        dialog = QColorDialog(current, self)
        dialog.setWindowTitle(title)
        dialog.setOptions(
            QColorDialog.ColorDialogOption.ShowAlphaChannel |
            QColorDialog.ColorDialogOption.DontUseNativeDialog
        )
        if dialog.exec():
            return dialog.currentColor()
        return None
    
    def _choose_fill_color(self):
        """Open color picker for fill."""
        color = self._pick_color(self.shape.fill_color, "Choose Fill Color")
        if color:
            self.shape.fill_color = color
            self._update_color_button(self.btn_fill, color)
    
    def _choose_stroke_color(self):
        """Open color picker for stroke."""
        color = self._pick_color(self.shape.stroke_color, "Choose Stroke Color")
        if color:
            self.shape.stroke_color = color
            self._update_color_button(self.btn_stroke, color)
    
    def accept(self):
        """Apply changes and close."""
        self.shape.stroke_width = self.spin_width.value()
        super().accept()


class ShapeFeature(QObject):
    """Manages shape operations for the RichTextEditor."""
    
    def __init__(self, editor: "RichTextEditor"):
        """
          init   logic.
        
        Args:
            editor: Description of editor.
        
        """
        super().__init__(editor)  # QObject parent
        self.editor = editor
        self.overlay: Optional[ShapeOverlay] = None
        self._init_overlay()
        self._init_actions()
    
    def _init_overlay(self):
        """Create and position the shape overlay."""
        # The overlay will be parented to the editor widget
        self.overlay = ShapeOverlay(self.editor.editor)
        self.overlay.setGeometry(self.editor.editor.rect())
        self.overlay.show()
        
        # Connect signals
        self.overlay.shape_selected.connect(self._on_shape_selected)
        
        # Update overlay size when editor resizes
        self.editor.editor.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Handle editor resize to update overlay."""
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.Resize:
            if self.overlay:
                self.overlay.setGeometry(self.editor.editor.rect())
        return False
    
    def _init_actions(self):
        """Create actions for the ribbon."""
        self.action_insert_shape = QAction("Shapes", self.editor)
        self.action_insert_shape.setToolTip("Insert a shape")
        self.action_insert_shape.triggered.connect(self.show_shape_picker)
        
        self.action_shape_props = QAction("Properties", self.editor)
        self.action_shape_props.setToolTip("Edit shape properties")
        self.action_shape_props.triggered.connect(self.show_properties)
        self.action_shape_props.setEnabled(False)
    
    def _on_shape_selected(self, shape: Optional[BaseShapeItem]):
        """Handle shape selection."""
        self.action_shape_props.setEnabled(shape is not None)
    
    def create_toolbar_button(self) -> QToolButton:
        """Create a toolbar button with shape menu."""
        btn = QToolButton()
        btn.setText("Shapes")
        btn.setIcon(qta.icon("fa5s.shapes", color="#1e293b"))
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        btn.setToolTip("Insert a shape")
        btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        menu = QMenu(btn)
        
        for name, shape_class in ShapePickerDialog.SHAPES:
            action = menu.addAction(name)
            action.triggered.connect(
                lambda checked, sc=shape_class: self._insert_shape(sc)
            )
        
        menu.addSeparator()
        polygon_action = menu.addAction("Polygon...")
        polygon_action.triggered.connect(self._show_polygon_dialog)
        
        btn.setMenu(menu)
        return btn
    
    def _show_polygon_dialog(self):
        """Show polygon configuration dialog."""
        dialog = PolygonConfigDialog(self.editor)
        if dialog.exec():
            sides, skip = dialog.get_config()
            self._insert_polygon(sides, skip)
    
    def _insert_polygon(self, sides: int, skip: int):
        """Insert a polygon shape with the given configuration."""
        if self.overlay:
            # Create a partially applied function that creates the polygon
            self._pending_polygon_config = (sides, skip)
            self.overlay.start_insert_mode(PolygonShapeItem)
            # Override the insert to use our config
            original_press = self.overlay.mousePressEvent
            def custom_press(event):
                """
                Custom press logic.
                
                Args:
                    event: Description of event.
                
                """
                if self.overlay._insert_mode and self.overlay._insert_shape_type == PolygonShapeItem:
                    scene_pos = self.overlay.mapToScene(event.position().toPoint())
                    shape = PolygonShapeItem(scene_pos.x(), scene_pos.y(), 100, 100, sides, skip)
                    self.overlay.add_shape(shape)
                    shape.setSelected(True)
                    self.overlay._insert_mode = False
                    self.overlay._insert_shape_type = None
                    from PyQt6.QtCore import Qt
                    self.overlay.setCursor(Qt.CursorShape.ArrowCursor)
                    event.accept()
                    self.overlay.mousePressEvent = original_press  # Restore
                    return
                original_press(event)
            self.overlay.mousePressEvent = custom_press
    
    def show_shape_picker(self):
        """Show the shape picker dialog."""
        dialog = ShapePickerDialog(self.editor)
        if dialog.exec():
            shape_type = dialog.get_selected_type()
            if shape_type:
                self._insert_shape(shape_type)
    
    def _insert_shape(self, shape_class: type):
        """Enter insert mode for the given shape type."""
        if self.overlay:
            self.overlay.start_insert_mode(shape_class)
    
    def show_properties(self):
        """Show properties dialog for selected shape."""
        if not self.overlay:
            return
        
        selected = self.overlay.get_selected_shapes()
        if not selected:
            return
        
        dialog = ShapePropertiesDialog(selected[0], self.editor)
        dialog.exec()
    
    def get_shapes_data(self) -> list:
        """Get serialized shapes data."""
        if self.overlay:
            return self.overlay.to_list()
        return []
    
    def load_shapes_data(self, data: list):
        """Load shapes from serialized data."""
        if self.overlay:
            self.overlay.from_list(data)
    
    def clear_shapes(self):
        """Remove all shapes."""
        if self.overlay:
            self.overlay.clear_shapes()