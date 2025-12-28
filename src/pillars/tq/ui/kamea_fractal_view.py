"""
Kamea Fractal View - The 3D Canopy Visualizer.
A native QGraphicsView-based 3D projection of the Kamea's 729 Ditrunes arranged by dimensional hierarchy.
"""

import math
import numpy as np
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
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Visual Settings
        self.setBackgroundBrush(QBrush(QColor('#050510')))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        
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
        offsets = {
            '00': (0, 0),
            '10': (-1, 1), '21': (0, 1), '02': (1, 1),
            '22': (-1, 0), '11': (1, 0),
            '01': (-1, -1), '12': (0, -1), '20': (1, -1)
        }
        
        # Parse Quadset Bigrams
        macro = ternary[2:4]
        meso = ternary[1] + ternary[4]
        micro = ternary[0] + ternary[5]
        
        off1 = offsets.get(macro, (0,0))
        off2 = offsets.get(meso, (0,0))
        off3 = offsets.get(micro, (0,0))
        
        # Logic Coords (2D Grid)
        gx = (off1[0] * 9) + (off2[0] * 3) + (off3[0] * 1)
        gy = (off1[1] * 9) + (off2[1] * 3) + (off3[1] * 1)
        
        pyx_count = ternary.count('0')
        
        # Map to 3D: X=gx, Y=Height(pyx), Z=gy
        return np.array([gx, pyx_count * 4.0, gy]), pyx_count, self._get_spectral_color(pyx_count)


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
        # Rotation Matrices
        cx, sx = math.cos(self.rotation_x), math.sin(self.rotation_x)
        cy, sy = math.cos(self.rotation_y), math.sin(self.rotation_y)
        
        # Rotate around Y then X
        # R_y = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
        # R_x = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
        
        # Combined Rotation (simplified for speed)
        # We'll just rotate vector manually or use np
        
        rot_mat = np.array([
            [cy, 0, sy],
            [sx*sy, cx, -sx*cy],
            [-cx*sy, sx, cx*cy]
        ])
        
        # Center of scene
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        # Center of scene
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        # 1. Hide/Show Lines & Points based on Focus
        visible_lines = []
        
        # Helper for Descendant Check
        def is_descendant(focus: str, candidate: str) -> bool:
            if focus == '000000': return True
            
            # Generalized Prefix Matching
            # Mask: Remove trailing zeros to get the "Path Header"
            # distinct from "Value 0". A 5D Node "100000" means Prefix "1".
            # A 5D Node "120000" (Wait, 12 is 4D).
            
            # We want to match hierarchy.
            # If Focus is '220000', we want all '22xxxx'.
            # strip('0') removes internal zeros if we are not careful (e.g. 101000).
            # We only want to strip *Trailing* zeros.
            
            prefix = focus.rstrip('0')
            if not prefix: 
                # Case 000000 was handled, but what if focus is '000'?
                # If focus is effectively root, return True
                return True
                
            return candidate.startswith(prefix)

        if self.focused_ditrune:
             # Focus Mode: Iterate all tree paths and check if they belong to a descendant
             for ternary, lines in self.tree_paths.items():
                 if is_descendant(self.focused_ditrune, ternary):
                     visible_lines.extend(lines)
        elif self.show_connections:
            # Show All
            for sublist in self.tree_paths.values():
                visible_lines.extend(sublist)
        
        # Hide all lines first (optimization needed? lots of items...)
        # Better: iterate all known lines and hide, then show visible?
        # Or just: 
        # For simplicity in this logic:
        # We need to know which lines are ACTUALLY active.
        
        # OPTIMIZATION:
        # If showing ALL:
        #    Use a shared set of lines?
        #    Actually, since multiple cells share lines (e.g. Area -> Region), we have duplicates in self.tree_paths.
        #    This is fine for "Focus Mode" (we want that specific branch).
        #    For "All Mode", we are drawing 3x lines per cell.
        #    Let's just update the visible ones.
        
        # Reset all pens to transparent?
        # That's slow (2100 items).
        # We rely on previous state? No.
        
        # Let's just Loop All lines if we changed mode... but here we just loop visible for POS updates.
        # Visibility setting should happen on state change.
        
        # Current Logic: Just update positions of visible lines.
        # Ensure we set Pen for visible, clear Pen for others?
        
        pen_std = QPen(QColor(255, 255, 255, 20))
        pen_std.setWidthF(0.5)
        
        if self.focused_ditrune:
             pen_std = QPen(QColor(255, 255, 255, 150)) # Bright for focused
             pen_std.setWidthF(2.0)
        
        # Hacky Cleanup: If we transitioned, we might have old lines visible.
        # Ideally we track "currently_visible_items" list.
        
        pass # To be handled inside data gen or state set.
             
        # Just iterate what we intend to draw
        for line_item, start, end in visible_lines:
             # Rotate
             rs = rot_mat @ start
             re = rot_mat @ end
             
             line_item.setLine(
                 rs[0]*self.base_scale, -rs[1]*self.base_scale,
                 re[0]*self.base_scale, -re[1]*self.base_scale
             )
             line_item.setPen(pen_std)
             line_item.setVisible(True)
             
        # Hide lines that shouldn't be valid?
        # This update loop is complex without tracking state.
        # Let's simplify: reset all lines to hidden at start of update?
        # Or just rely on set_focus / set_show to trigger a full clear.
        
        # 2. Update Points
        for i, point in enumerate(self.points_3d):
            item = self.graphic_items[i]
            ternary = point['info'].split('\n')[0].split(': ')[1]
            
            # Context Logic:
            if self.focused_ditrune:
                # Use shared descendant logic
                is_target = is_descendant(self.focused_ditrune, ternary)
                
                if is_target:
                    item.setOpacity(1.0)
                    # item.setZValue(100) # Ensure on top
                else:
                    item.setOpacity(0.10) # Ghosted context (fainter)
            else:
                item.setOpacity(1.0)
            
            item.setVisible(True) # Always visible now
            
            vec = point['vec']
            # Rotate
            rotated = rot_mat @ vec
            
            # Project (Orthographic/Perspective mix)
            # Simple Orthographic with scale for now, maybe add perspective later
            # Screen X = Rotated X * scale
            # Screen Y = Rotated Y * scale (invert Y for screen coords)
            
            # Isometric-like projection
            px = rotated[0] * self.base_scale
            py = -rotated[1] * self.base_scale # Y is up in 3D, down in 2D screen
            
            # Add Z-depth parallax?
            # For "3D" feel, we map rotated Z to depth, but QGraphicsScene is 2D.
            # We just project X and Y (after rotation steps which put Z into view).
            
            # Actually, standard 3D to 2D project:
            # x' = x, y' = y.  (Orthographic)
            # Since we rotated, 'z' is depth. 'y' is vertical. 'x' is horizontal.
            
            item = self.graphic_items[i]
            # Center it
            item.setPos(px - (point['size']/2), py - (point['size']/2))
            
            # Z-sorting? 
            # QGraphicsItem zValue. Higher Z is on top.
            # Rotated Z is depth (positive towards viewer?).
            # In our matrix: Row 2 is Z.
            z_depth = rotated[2]
            item.setZValue(z_depth)
            
        # Draw Axis
        # 0,0,0 -> 0,30,0
        start = np.array([0,0,0])
        end = np.array([0,30,0])
        r_start = rot_mat @ start
        r_end = rot_mat @ end
        
        self.axis_item.setLine(
            r_start[0]*self.base_scale, -r_start[1]*self.base_scale,
            r_end[0]*self.base_scale, -r_end[1]*self.base_scale
        )
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.pos()
            self.mouse_press_start_pos = event.pos() # For click detection
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
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
        angle = event.angleDelta().y()
        factor = 1.1 if angle > 0 else 0.9
        self.scale(factor, factor) 
        # Alternatively adjust base_scale
        
    def _to_ternary(self, n: int) -> str:
        if n == 0: return "000000"
        nums = []
        while n:
            n, r = divmod(n, 3)
            nums.append(str(r))
        return ''.join(reversed(nums)).zfill(6)

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
        self.show_connections = show
        self._update_projection()
