"""
Kamea Fractal View - The 3D Canopy Visualizer.
A native QGraphicsView-based 3D projection of the Kamea's 729 Ditrunes arranged by dimensional hierarchy.
"""

import math
import math
from ..services.kamea_math_service import KameaMathService
from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem,
    QToolTip, QLabel, QWidget, QVBoxLayout, QMenu
)
from PyQt6.QtGui import QBrush, QPen, QColor, QPainter, QTransform, QFont, QAction
from PyQt6.QtCore import Qt, QPointF, QTimer, pyqtSignal

class KameaFractalView(QGraphicsView):
    """
    Native 3D Fractal Canopy Visualization.
    Uses software projection (3D -> 2D) on a QGraphicsScene to avoid OpenGL context issues.
    """
    cell_clicked = pyqtSignal(str) # Emits the ternary value string
    focus_changed = pyqtSignal(object) # Emits ternary (str) or None
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Visual Settings
        self.setBackgroundBrush(QBrush(QColor('#050510')))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        self.math_service = KameaMathService()
        
        # Camera / Interaction State
        self.rotation_x = 0.5  # Pitch
        self.rotation_y = 0.5  # Yaw
        self.last_mouse_pos = None
        self.base_scale = 15.0 # Zoom
        
        # Data Storage
        self.points_3d = [] # List of tuples (x, y, z, color, size, pyx_count, ditrune)
        self.graphic_items = [] # List of QGraphicsEllipseItem
        
        # Mapping ternary -> list of (line_item, start_vec, end_vec)
        self.tree_paths = {} 
        
        # Options
        self.show_connections = False
        self.focused_ditrune = None # If set, show only this tree
        
        # Generate Data
        self._generate_data()
        
        # Initial Draw
        self._update_projection()
        
        # HUD Legend (Key)
        self._create_legend()

    def _create_legend(self):
        """Creates an overlay widget for the Legend."""
        legend_widget = QWidget(self)
        legend_widget.setStyleSheet("background-color: rgba(10, 10, 20, 0.8); color: #ddd; border-radius: 5px; padding: 5px;")
        layout = QVBoxLayout(legend_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        title = QLabel("DIMENSIONAL KEY")
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #fff; margin-bottom: 5px;")
        layout.addWidget(title)
        
        items = [
            ("Singularity (6D)", "#ff3333"),
            ("Axis (5D)", "#ff8000"),
            ("Faces (4D)", "#ffff00"),
            ("Cells (3D)", "#00ff00"),
            ("Planes (2D)", "#00ffff"),
            ("Lines (1D)", "#0080ff"),
            ("Leaves (0D)", "#9600ff"),
        ]
        
        for text, color_hex in items:
            lbl = QLabel(f"■ {text}")
            lbl.setStyleSheet(f"color: {color_hex}; font-family: monospace;")
            layout.addWidget(lbl)
            
        legend_widget.adjustSize()
        legend_widget.move(20, 20) # Top Left
        
    def _generate_data(self):
        """Generates the 729 points and creates their graphic items."""
    def _calculate_coord(self, ternary: str):
        """Calculates 3D world coordinate for any ternary string."""
        # Use Service
        gx, gy, gz, pyx_count = self.math_service.calculate_coord(ternary)
        
        # Map to 3D Vector Tuple (X, Y, Z) instead of numpy array
        return (gx, gy, gz), pyx_count, self._get_spectral_color(pyx_count)


    def _generate_data(self):
        """Generates the 729 points and creates their graphic items."""
        
        for i in range(729):
            ternary = self._to_ternary(i)
            
            # Leaf Position
            pos_vec, pyx_count, color = self._calculate_coord(ternary)
            
            # Size logic
            size = 4.0 if pyx_count == 6 else 2.0
            
            self.points_3d.append({
                'vec': pos_vec,
                'color': color,
                'size': size,
                'info': f"Ditrune: {ternary}\nDim: {pyx_count}"
            })
            
            # --- Tree Generation (6 Segments) ---
            # 6D (Root) -> 5D -> 4D -> 3D -> 2D -> 1D -> 0D (Leaf)
            
            self.tree_paths[ternary] = []
            
            steps = []
            # Calculate coordinates for all 7 levels
            for level in range(7):
                # Mask: First i digits, rest 0
                val = ternary[:level] + "0" * (6-level)
                v_pos, v_pyx, v_col = self._calculate_coord(val)
                steps.append( (v_pos, v_col) )
            
            # Create Lines between steps
            # Step 0 is 6D (Root), Step 6 is 0D (Leaf)
            # We connect Step i to Step i-1
            
            # Colors for lines: use the color of the CHILD node?
            # Or a fixed visibility color.
            
            for lvl in range(1, 7):
                start = steps[lvl-1][0] # Parent
                end = steps[lvl][0]     # Child
                
                line = QGraphicsLineItem()
                line.setPen(QPen(Qt.GlobalColor.transparent)) # Hidden by default
                self.scene.addItem(line)
                
                # Store tuple: (item, start_vec, end_vec)
                self.tree_paths[ternary].append( (line, start, end) )

            # Create Item (hidden initially, pos updated in projection)
            item = QGraphicsEllipseItem(0, 0, size, size)
            item.setBrush(QBrush(color))
            item.setPen(QPen(Qt.PenStyle.NoPen))
            item.setToolTip(f"Ditrune: {ternary}\nPyx: {pyx_count}")
            item.setData(0, ternary) 
            self.scene.addItem(item)
            self.graphic_items.append(item)
            
        # Add Central Axis Line
        self.axis_item = QGraphicsLineItem()
        pen = QPen(QColor(255, 255, 255, 50))
        pen.setWidth(1)
        self.axis_item.setPen(pen)
        self.scene.addItem(self.axis_item)

    def _update_projection(self):
        """Projects 3D points to 2D scene based on rotation."""
        
        # 1. Update Points
        # Collect all points to project in batch
        all_vecs = [pt['vec'] for pt in self.points_3d]
        
        # Project using Service (returns rotated x, y, z tuples)
        projected = self.math_service.project_points(all_vecs, self.rotation_x, self.rotation_y)
        
        # Update Graphic Items
        for i, (px, py, pz) in enumerate(projected):
             point_data = self.points_3d[i]
             item = self.graphic_items[i]
             
             # Screen Coords (Isometric-ish)
             sx = px * self.base_scale
             sy = -py * self.base_scale
             
             # Visibility / Opacity Logic
             ternary = point_data['info'].split('\n')[0].split(': ')[1]
             opacity = 1.0
             
             if self.focused_ditrune:
                 # Check descendant
                 # Re-implement simple check or use service if needed
                 # keeping local helper for now or moving it
                 if not self._is_descendant(self.focused_ditrune, ternary):
                     opacity = 0.10
             
             item.setOpacity(opacity)
             item.setPos(sx - (point_data['size']/2), sy - (point_data['size']/2))
             item.setZValue(pz) # Z-depth
        
        # 2. Update Lines (Separately for now, could also batch project)
        visible_lines = self._get_visible_lines()
        
        if visible_lines:
             starts = [start for _, start, end in visible_lines]
             ends = [end for _, start, end in visible_lines]
             
             proj_starts = self.math_service.project_points(starts, self.rotation_x, self.rotation_y)
             proj_ends = self.math_service.project_points(ends, self.rotation_x, self.rotation_y)
             
             pen_std = QPen(QColor(255, 255, 255, 20))
             pen_std.setWidthF(0.5)
             if self.focused_ditrune:
                 pen_std = QPen(QColor(255, 255, 255, 150))
                 pen_std.setWidthF(2.0)
             
             for idx, (line_item, _, _) in enumerate(visible_lines):
                 s = proj_starts[idx]
                 e = proj_ends[idx]
                 
                 line_item.setLine(
                     s[0]*self.base_scale, -s[1]*self.base_scale,
                     e[0]*self.base_scale, -e[1]*self.base_scale
                 )
                 line_item.setPen(pen_std)
                 line_item.setVisible(True)

        # 3. Update Axis
        axis_pts = [(0,0,0), (0,30,0)]
        proj_axis = self.math_service.project_points(axis_pts, self.rotation_x, self.rotation_y)
        self.axis_item.setLine(
             proj_axis[0][0]*self.base_scale, -proj_axis[0][1]*self.base_scale,
             proj_axis[1][0]*self.base_scale, -proj_axis[1][1]*self.base_scale
        )
             
    def _is_descendant(self, focus: str, candidate: str) -> bool:
        if focus == '000000': return True
        prefix = focus.rstrip('0')
        if not prefix: return True
        return candidate.startswith(prefix)

    def _get_visible_lines(self):
        visible = []
        if self.focused_ditrune:
             for ternary, lines in self.tree_paths.items():
                 if self._is_descendant(self.focused_ditrune, ternary):
                     visible.extend(lines)
        elif self.show_connections:
            for sublist in self.tree_paths.values():
                visible.extend(sublist)
        return visible

    def _unused_old_update(self):
        # Placeholder to replace the old giant method body 
        pass
            
    def mousePressEvent(self, event):
        """
        Mousepressevent logic.
        
        Args:
            event: Description of event.
        
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.pos()
            self.mouse_press_start_pos = event.pos() # For click detection
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Mousemoveevent logic.
        
        Args:
            event: Description of event.
        
        """
        if self.last_mouse_pos and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.pos() - self.last_mouse_pos
            
            # Update rotation
            self.rotation_y += delta.x() * 0.01
            self.rotation_x += delta.y() * 0.01
            
            self.last_mouse_pos = event.pos()
            self._update_projection()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Click Detection
        """
        Mousereleaseevent logic.
        
        Args:
            event: Description of event.
        
        """
        if event.button() == Qt.MouseButton.LeftButton and self.mouse_press_start_pos:
            diff = (event.pos() - self.mouse_press_start_pos).manhattanLength()
            if diff < 5: # Threshold for click vs drag
                # It's a click
                item = self.itemAt(event.pos())
                if isinstance(item, QGraphicsEllipseItem):
                    ditrune = item.data(0)
                    if ditrune:
                        self.cell_clicked.emit(ditrune)
                        
        self.last_mouse_pos = None
        self.mouse_press_start_pos = None
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        """
        Contextmenuevent logic.
        
        Args:
            event: Description of event.
        
        """
        item = self.itemAt(event.pos())
        
        menu = QMenu(self)
        
        clicked_ditrune = None
        if isinstance(item, QGraphicsEllipseItem):
             clicked_ditrune = item.data(0)
             
        if clicked_ditrune:
            action_focus = QAction(f"Focus Tree: {clicked_ditrune}", self)
            action_focus.triggered.connect(lambda: self.set_focused_ditrune(clicked_ditrune))
            menu.addAction(action_focus)
            
        if self.focused_ditrune is not None:
            action_clear = QAction("Clear Focus", self)
            action_clear.triggered.connect(lambda: self.set_focused_ditrune(None))
            menu.addAction(action_clear)
            
        if not menu.isEmpty():
            menu.exec(event.globalPos())
            
    def set_focused_ditrune(self, ternary: str):
        """
        Configure focused ditrune logic.
        
        Args:
            ternary: Description of ternary.
        
        """
        self.focused_ditrune = ternary
        self.focus_changed.emit(ternary)
        
        # Hide all lines first to clean slate
        # (This is inefficient but safe)
        for sublist in self.tree_paths.values():
            for line_item, _, _ in sublist:
                line_item.setVisible(False)
                
        self._update_projection()
        
    def wheelEvent(self, event):
        # Zoom
        """
        Wheelevent logic.
        
        Args:
            event: Description of event.
        
        """
        angle = event.angleDelta().y()
        factor = 1.1 if angle > 0 else 0.9
        self.scale(factor, factor) 
        # Alternatively adjust base_scale
        
    def _to_ternary(self, n: int) -> str:
        return self.math_service.to_ternary(n)

    def _get_spectral_color(self, pyx: int) -> QColor:
        if pyx == 6: return QColor(255, 50, 50)   # Red
        if pyx == 5: return QColor(255, 128, 0)   # Orange
        if pyx == 4: return QColor(255, 255, 0)   # Yellow
        if pyx == 3: return QColor(0, 255, 0)     # Green
        if pyx == 2: return QColor(0, 255, 255)   # Cyan
        if pyx == 1: return QColor(0, 128, 255)   # Azure
        if pyx == 0: return QColor(150, 0, 255)   # Violet
        return QColor(255, 255, 255)

    def set_show_connections(self, show: bool):
        """
        Configure show connections logic.
        
        Args:
            show: Description of show.
        
        """
        self.show_connections = show
        self._update_projection()