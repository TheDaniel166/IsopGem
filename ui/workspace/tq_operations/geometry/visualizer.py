from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QToolBar, QPushButton, 
                            QColorDialog, QSpinBox, QLabel, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QDateTime
from PyQt5.QtGui import QIcon, QColor, QPainter, QImage
from .scene import GeometryScene
from .view import GeometryView
from .items import GeometryPoint, GeometryLine
import os

class GeometryVisualizer(QWidget):
    """Main widget for geometry visualization and interaction."""
    
    # Signals
    selectionChanged = pyqtSignal()  # Emitted when selection changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        
        # Initialize state
        self.custom_lines = []
        self.pattern_lines = []
        self.sides = 0  # Store current polygon sides
        self.layers = 0  # Store current number of layers
        
    def setup_ui(self):
        """Create and arrange UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create toolbar
        self.toolbar = QToolBar()
        self.setup_toolbar()
        layout.addWidget(self.toolbar)
        
        # Create scene and view
        self.scene = GeometryScene()
        self.view = GeometryView(self.scene)
        layout.addWidget(self.view)
        
        # Set initial scene rect
        self.scene.setSceneRect(-200, -200, 400, 400)
        
    def setup_toolbar(self):
        """Create toolbar buttons and actions."""
        # Drawing mode toggle
        self.draw_mode_btn = QPushButton("Drawing Mode")
        self.draw_mode_btn.setCheckable(True)
        self.draw_mode_btn.setChecked(True)
        self.draw_mode_btn.clicked.connect(self.toggle_drawing_mode)
        self.toolbar.addWidget(self.draw_mode_btn)
        
        self.toolbar.addSeparator()
        
        # Point customization
        point_size_label = QLabel("Point Size:")
        self.toolbar.addWidget(point_size_label)
        self.point_size_spin = QSpinBox()
        self.point_size_spin.setRange(2, 20)
        self.point_size_spin.setValue(5)
        self.point_size_spin.valueChanged.connect(self.change_point_size)
        self.toolbar.addWidget(self.point_size_spin)
        
        # Point color button
        self.point_color_btn = QPushButton("Point Color")
        self.point_color_btn.clicked.connect(self.change_point_color)
        self.toolbar.addWidget(self.point_color_btn)
        
        self.toolbar.addSeparator()
        
        # Line customization
        line_width_label = QLabel("Line Width:")
        self.toolbar.addWidget(line_width_label)
        self.line_width_spin = QSpinBox()
        self.line_width_spin.setRange(1, 10)
        self.line_width_spin.setValue(2)
        self.line_width_spin.valueChanged.connect(self.change_line_width)
        self.toolbar.addWidget(self.line_width_spin)
        
        # Line color button
        self.line_color_btn = QPushButton("Line Color")
        self.line_color_btn.clicked.connect(self.change_line_color)
        self.toolbar.addWidget(self.line_color_btn)
        
        self.toolbar.addSeparator()
        
        # Label customization
        label_size_label = QLabel("Label Size:")
        self.toolbar.addWidget(label_size_label)
        self.label_size_spin = QSpinBox()
        self.label_size_spin.setRange(6, 16)
        self.label_size_spin.setValue(8)
        self.label_size_spin.valueChanged.connect(self.change_label_size)
        self.toolbar.addWidget(self.label_size_spin)
        
        # Label color button
        self.label_color_btn = QPushButton("Label Color")
        self.label_color_btn.clicked.connect(self.change_label_color)
        self.toolbar.addWidget(self.label_color_btn)
        
        self.toolbar.addSeparator()
        
        # Export button
        self.export_btn = QPushButton("Export PNG")
        self.export_btn.clicked.connect(self.export_to_png)
        self.toolbar.addWidget(self.export_btn)
        
        # Delete and Clear buttons
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected)
        self.toolbar.addWidget(self.delete_btn)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_scene)
        self.toolbar.addWidget(self.clear_btn)
        
    def setup_connections(self):
        """Connect signals and slots."""
        self.scene.selectionChanged.connect(self.handle_selection_changed)
        
    def toggle_drawing_mode(self, checked):
        """Toggle between drawing and selection modes."""
        self.view.set_drawing_mode(checked)
        self.draw_mode_btn.setText(
            "Drawing Mode (On)" if checked else "Drawing Mode (Off)"
        )
        
    def delete_selected(self):
        """Delete selected items from the scene."""
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if item in self.custom_lines:
                self.custom_lines.remove(item)
            elif item in self.pattern_lines:
                self.pattern_lines.remove(item)
            self.scene.removeItem(item)
            
    def clear_scene(self):
        """Clear all items from the scene."""
        self.scene.clear()
        self.custom_lines.clear()
        self.pattern_lines.clear()
        
    def handle_selection_changed(self):
        """Handle changes in item selection."""
        self.selectionChanged.emit()
        
    def create_centered_polygon(self, sides: int, layers: int):
        """Create a centered polygonal number visualization."""
        self.scene.clear()
        return self.scene.create_centered_polygon(sides, layers)
        
    def create_point(self, x: float, y: float, number: int):
        """Create a new point at the specified position."""
        point = GeometryPoint(x, y, number)
        self.scene.addItem(point)
        return point
        
    def create_line(self, start_point, end_point, line_type):
        """Create a new line between two points."""
        line = GeometryLine(start_point, end_point, line_type)
        self.scene.addItem(line)
        
        if line_type == GeometryLine.Type.CUSTOM:
            self.custom_lines.append(line)
        elif line_type == GeometryLine.Type.PATTERN:
            self.pattern_lines.append(line)
            
        return line 

    def create_polygon(self, sides: int):
        """Convenience method for backward compatibility."""
        return self.create_centered_polygon(sides, 1) 

    def change_point_size(self, size):
        """Change size of all points."""
        for item in self.scene.items():
            if isinstance(item, GeometryPoint):
                item.set_size(size)

    def change_point_color(self):
        """Change color of points."""
        color = QColorDialog.getColor()
        if color.isValid():
            for item in self.scene.items():
                if isinstance(item, GeometryPoint):
                    item.set_color(color)

    def change_line_width(self, width):
        """Change width of all lines."""
        for item in self.scene.items():
            if isinstance(item, GeometryLine):
                item.set_width(width)

    def change_line_color(self):
        """Change color of lines."""
        color = QColorDialog.getColor()
        if color.isValid():
            for item in self.scene.items():
                if isinstance(item, GeometryLine):
                    item.set_color(color)

    def change_label_size(self, size):
        """Change size of point labels."""
        for item in self.scene.items():
            if isinstance(item, GeometryPoint):
                item.set_label_size(size)

    def change_label_color(self):
        """Change color of labels."""
        color = QColorDialog.getColor()
        if color.isValid():
            for item in self.scene.items():
                if isinstance(item, GeometryPoint):
                    item.set_label_color(color)

    def export_to_png(self):
        """Export the current view to a PNG file with metadata."""
        # Get save location
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd_hh-mm-ss")
        default_name = f"centered_{self.sides}gon_{self.layers}layers_{timestamp}.png"
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Image", 
            os.path.join(os.path.expanduser("~"), default_name),
            "PNG Images (*.png)"
        )
        
        if filename:
            # Create image from scene
            scene_rect = self.scene.itemsBoundingRect()
            # Add padding
            scene_rect.adjust(-50, -50, 50, 50)
            image = QImage(scene_rect.size().toSize(), QImage.Format_ARGB32)
            image.fill(Qt.white)
            
            # Setup painter
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Render scene
            self.scene.render(painter, image.rect(), scene_rect)
            
            # Add metadata text
            painter.setPen(Qt.black)
            metadata = [
                f"Date: {QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')}",
                f"Type: Centered {self.sides}-gonal Number",
                f"Layers: {self.layers}",
                f"Total Points: {self.get_total_points()}",
                f"Total Lines: {self.get_total_lines()}"
            ]
            
            y = 20
            for text in metadata:
                painter.drawText(10, y, text)
                y += 20
                
            painter.end()
            
            # Save image
            image.save(filename)

    def get_total_points(self):
        """Get total number of points in the scene."""
        return len([item for item in self.scene.items() if isinstance(item, GeometryPoint)])

    def get_total_lines(self):
        """Get total number of lines in the scene."""
        return len([item for item in self.scene.items() if isinstance(item, GeometryLine)])

    def create_polygonal_number(self, sides: int, n: int):
        """Create a polygonal number visualization."""
        self.scene.clear()
        return self.scene.create_polygonal_number(sides, n)

    def create_star_number(self, points: int, position: int):
        """Create a star number visualization."""
        self.scene.clear()
        return self.scene.create_star_number(points, position) 