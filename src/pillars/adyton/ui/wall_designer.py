import sys
import os
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QPushButton, QLabel, QFrame, QFileDialog, QMessageBox,
    QScrollArea, QComboBox, QCheckBox, QMenu, QTextEdit
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QPainter, QPixmap, QAction

class ConstellationGrid(QFrame):
    """
    A container for the grid that overlays visual asterism lines (MST).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #222;")
        self.lattice = None
        self.mst_edges = [] # List of tuples ((r1,c1), (r2,c2))
        self.cell_size = 50
        
    def set_lattice(self, lattice, cells_layout_list):
        """
        Calculates the Minimum Spanning Tree for each constellation group
        to generate 'Asterism' lines.
        """
        self.lattice = lattice
        self.mst_edges = []
        if not lattice:
            self.update()
            return
            
        rows = len(lattice)
        cols = len(lattice[0])
        
        # Group cells
        groups = {} # id -> list of (r,c)
        for r in range(rows):
            for c in range(cols):
                gid = lattice[r][c]
                if gid not in groups: groups[gid] = []
                groups[gid].append((r,c))
                
        # Calculate MST for each group
        import math
        
        for gid, cells in groups.items():
            if len(cells) < 2: continue
            
            # Prim's Algorithm for MST on the grid graph
            # Nodes: cells. Edges: adjacent cells (dist 1).
            # If not adjacent, we don't connect (strict grid adjacency).
            # Actually, we want visual "stick figures".
            # Prioritize orthogonal connections, then diagonal?
            # Or just standard MST on Euclidean dist?
            # Standard MST on Euclidean dist ensures close stars connect.
            
            connected = set()
            connected.add(cells[0])
            unconnected = set(cells[1:])
            
            while unconnected:
                # Find shortest edge from connected to unconnected
                best_edge = None
                min_dist = 9999
                best_node = None
                
                for u in connected:
                    for v in unconnected:
                        # Dist sq
                        d = (u[0]-v[0])**2 + (u[1]-v[1])**2
                        if d < min_dist:
                            min_dist = d
                            best_edge = (u, v)
                            best_node = v
                            
                if best_edge:
                    self.mst_edges.append(best_edge)
                    connected.add(best_node)
                    unconnected.remove(best_node)
                else:
                    # Disconnected component? Should not happen if generated correctly.
                    # Pick arbitrary remaining to restart (forest)
                    if unconnected:
                        start = list(unconnected)[0]
                        connected.add(start)
                        unconnected.remove(start)
                        
        self.update() # Trigger repaint

    def paintEvent(self, event):
        # Draw children (cells) first
        # But wait, children draw on top of parent?
        # Standard QFrame draws background. Then children.
        # If we want lines ON TOP of cells, we need an overlay or paintAfterChildren?
        # Easier: Draw lines on parent, but Z-order?
        # If cells are widgets, they cover the parent.
        # We need a transparent overlay widget on TOP of the grid layout?
        # OR: Just let the user "See through" the cells?
        # NO.
        # BEST APPROACH: Transparent Overlay Widget using `raise_()`.
        super().paintEvent(event)

class AsterismOverlay(QWidget):
    """Transparent overlay to draw lines on top of the grid."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.mst_edges = []
        self.cell_size = 50
        self.grid_margins = 20
        self.grid_spacing = 1
        
    def set_edges(self, edges):
        self.mst_edges = edges
        self.update()
        
    def paintEvent(self, event):
        if not self.mst_edges: return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Pen for Asterisms (Glowing Star Lines)
        # Gold/White
        color = QColor(255, 255, 200, 180) # Semi-transparent gold
        pen = painter.pen()
        pen.setColor(color)
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Calculate offsets
        # Grid logic: Margin + (Index * (Size + Spacing)) + HalfSize
        m = self.grid_margins
        s = self.cell_size
        sp = self.grid_spacing
        
        def get_center(r, c):
            x = m + (c * (s + sp)) + (s // 2)
            y = m + (r * (s + sp)) + (s // 2)
            return x, y
            
        for (u, v) in self.mst_edges:
            x1, y1 = get_center(u[0], u[1])
            x2, y2 = get_center(v[0], v[1])
            painter.drawLine(x1, y1, x2, y2)

class WallCell(QFrame):
    """
    A single cell in the Wall Designer grid.
    """
    clicked = pyqtSignal(int, int)
    right_clicked = pyqtSignal(int, int, object)
    def __init__(self, row, col, size=40, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.size = size
        self.value = 0
        self.overlay_tint = None
        self.group_id = -1
        self.is_seed = False
        
        self.setFixedSize(size, size)
        self.setFrameShape(QFrame.Shape.Box)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        
        # Star Label
        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background: transparent; color: #FFF; font-size: 14pt;")
        self.label.resize(size, size)
        
        self.update_style()
        
    def _on_context_menu(self, pos):
        global_pos = self.mapToGlobal(pos)
        self.right_clicked.emit(self.row, self.col, global_pos)

    def set_overlay(self, group_id, tint_color, is_seed=False):
        self.group_id = group_id
        self.overlay_tint = tint_color
        self.is_seed = is_seed
        
        # Set Star
        if group_id >= 0:
            self.label.setText("★")
        else:
            self.label.setText("")
            
        self.update_style()

    def update_style(self):
        """Updates the background color and border."""
        style = ""
        
        if self.overlay_tint:
             # Brighter border and brighter star for seed
             if self.is_seed:
                 style += f"background-color: {self.overlay_tint};"
                 style += f" border: 2px solid #FFD700;" # Gold border for seed
                 # Brighter, larger star
                 self.label.setStyleSheet("background: transparent; color: #FFFFFF; font-size: 14pt; font-weight: bold;")
             else:
                 style += f"background-color: {self.overlay_tint};"
                 style += f" border: 1px solid {self.overlay_tint};"
                 # Dimmer star
                 self.label.setStyleSheet("background: transparent; color: rgba(255,255,255,0.7); font-size: 10pt;")
        else:
             # Empty cell
             style += "background-color: #1a1a1a;"
             style += " border: 1px solid #333;"
             self.label.setStyleSheet("background: transparent; color: transparent; font-size: 14pt;")
             
        self.setStyleSheet(style)


    def mousePressEvent(self, event):
        self.clicked.emit(self.row, self.col)
        super().mousePressEvent(event)

class WallDesignerWindow(QMainWindow):
    """
    A tool to design/visualize a Planetary Wall (104 Cells: 13 Columns x 8 Rows).
    """
    def __init__(self, window_manager=None, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager
        self.setWindowTitle("Adyton Constellation Map")
        self.resize(1000, 700)
        
        self.cells = [] # List of list
        self.planetary_lattices = {}
        self.current_wall_lattice = None
        
        # Load Lattices
        self.load_lattices()
        
        # Load Mythos (Grimoire) Data
        self.mythos_data = self._load_mythos_data()
        
        self.init_ui()
    
    def _load_mythos_data(self):
        """Load constellation mythos from JSON file."""
        json_path = os.path.join(os.path.dirname(__file__), "..", "data", "constellation_mythos.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARN] Could not load mythos data: {e}")
        return {}

    def load_lattices(self):
        import json
        import os
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "mods", "data", "planetary_lattices.json"))
        print(f"[DEBUG] Loading lattices from: {path}")
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    self.planetary_lattices = json.load(f)
                print(f"[DEBUG] Loaded {len(self.planetary_lattices)} planetary lattices.")
            except Exception as e:
                print(f"[ERROR] Failed to load JSON: {e}")
        else:
            print("[ERROR] Planetary lattices file not found!")

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        h_layout = QHBoxLayout(main_widget) # Main layout horizontal
        
        # Left container (Grid + Toolbar)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        # --- Toolbar ---
        toolbar = QHBoxLayout()
        
        # Wall Selector
        toolbar.addWidget(QLabel("Wall:"))
        self.wall_selector = QComboBox()
        self.wall_selector.addItems(["None", "Sun", "Mercury", "Moon", "Venus", "Jupiter", "Mars", "Saturn"])
        self.wall_selector.currentTextChanged.connect(self.on_wall_changed)
        toolbar.addWidget(self.wall_selector)
        
        toolbar.addSpacing(10)
        
        # Overlay Toggle
        self.chk_overlay = QCheckBox("Show Constellations")
        self.chk_overlay.setChecked(True)
        self.chk_overlay.toggled.connect(self.update_grid_overlay)
        toolbar.addWidget(self.chk_overlay)
        
        toolbar.addStretch()
        
        # Export
        btn_export = QPushButton("Export Snapshot")
        btn_export.clicked.connect(self.export_snapshot)
        toolbar.addWidget(btn_export)
        
        left_layout.addLayout(toolbar)
        
        # --- Grid Area ---
        self.grid_frame = QFrame()
        self.grid_frame.setStyleSheet("background-color: #222;")
        grid_layout = QGridLayout(self.grid_frame)
        grid_layout.setSpacing(1)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        
        self.cells = []
        cell_size = 50
        
        for r in range(8):
            row_cells = []
            for c in range(13):
                cell = WallCell(r, c, size=cell_size)
                cell.clicked.connect(self.on_cell_clicked) # Connect signal
                cell.right_clicked.connect(self.on_cell_right_clicked)
                grid_layout.addWidget(cell, r, c)
                row_cells.append(cell)
            self.cells.append(row_cells)
            
        left_layout.addStretch()
        left_layout.addWidget(self.grid_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        left_layout.addStretch()
        
        # Overlay
        self.overlay = AsterismOverlay(self.grid_frame)
        
        original_resize = self.grid_frame.resizeEvent
        def on_grid_resize(event):
            self.overlay.resize(event.size())
            if original_resize: original_resize(event)
        self.grid_frame.resizeEvent = on_grid_resize

        h_layout.addWidget(left_container, stretch=3)

        # --- Right Panel (Info + Grimoire) ---
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.Shape.StyledPanel)
        right_panel.setStyleSheet("background-color: #2a2a2a; color: white; border-radius: 8px;")
        right_panel.setFixedWidth(380)
        r_layout = QVBoxLayout(right_panel)
        r_layout.setContentsMargins(12, 12, 12, 12)
        r_layout.setSpacing(8)
        
        # Header
        header = QLabel("CONSTELLATION DATA")
        header.setStyleSheet("font-size: 10pt; color: #888; font-weight: bold; letter-spacing: 2px;")
        r_layout.addWidget(header)
        
        # Constellation Name (from Grimoire)
        self.lbl_name = QLabel("Select a constellation...")
        self.lbl_name.setStyleSheet("font-size: 16pt; font-weight: bold; color: #d4af37;")
        self.lbl_name.setWordWrap(True)
        r_layout.addWidget(self.lbl_name)
        
        # Greek Key
        self.lbl_greek = QLabel("")
        self.lbl_greek.setStyleSheet("font-size: 10pt; font-style: italic; color: #aaa;")
        self.lbl_greek.setWordWrap(True)
        r_layout.addWidget(self.lbl_greek)
        
        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("background-color: #444;")
        r_layout.addWidget(sep1)
        
        # Values & Total
        val_layout = QHBoxLayout()
        val_layout.addWidget(QLabel("Values:"))
        self.txt_values = QLabel("-")
        self.txt_values.setWordWrap(True)
        self.txt_values.setStyleSheet("color: #ccc;")
        val_layout.addWidget(self.txt_values, stretch=1)
        r_layout.addLayout(val_layout)
        
        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel("Total:"))
        self.lbl_total = QLabel("0")
        self.lbl_total.setStyleSheet("font-size: 18pt; font-weight: bold; color: #00FF00;")
        total_layout.addWidget(self.lbl_total)
        total_layout.addStretch()
        r_layout.addLayout(total_layout)
        
        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: #444;")
        r_layout.addWidget(sep2)
        
        # Grimoire Text Area (Mythos, Texture, Mantra)
        self.txt_grimoire = QTextEdit()
        self.txt_grimoire.setReadOnly(True)
        self.txt_grimoire.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ddd;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
            }
        """)
        self.txt_grimoire.setPlaceholderText("Click a constellation to view its Grimoire entry...")
        r_layout.addWidget(self.txt_grimoire, stretch=1)
        
        h_layout.addWidget(right_panel)

    def on_wall_changed(self, wall_name):
        if wall_name == "None":
            self.current_wall_lattice = None
            self.current_wall_values = None
        else:
            self.current_wall_lattice = self.planetary_lattices.get(wall_name)
            self.load_wall_values(wall_name)
            
        self.update_grid_overlay()
        # Reset info panel
        self.lbl_name.setText("Select a constellation...")
        self.lbl_greek.setText("")
        self.lbl_total.setText("0")
        self.txt_values.setText("-")
        self.txt_grimoire.clear()

    def load_wall_values(self, wall_name):
        # Map Name to Filename
        fname_map = {
            "Sun": "sun_wall.csv",
            "Mercury": "mercury_wall.csv",
            "Moon": "luna_wall.csv",
            "Venus": "venus_wall.csv",
            "Mars": "mars_wall.csv",
            "Jupiter": "jupiter_wall.csv",
            "Saturn": "saturn_wall.csv"
        }
        fname = fname_map.get(wall_name)
        if not fname: return

        # Path: Docs/adyton_walls/
        import csv
        # src/pillars/adyton/ui/wall_designer.py -> ... -> isopgem/Docs
        # 1: ui -> adyton, 2: adyton -> pillars, 3: pillars -> src, 4: src -> isopgem
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "Docs", "adyton_walls", fname))
        print(f"[DEBUG] Loading wall values from: {path}")
        
        self.current_wall_values = []
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        # Parse ints
                        int_row = [int(x) for x in row if x.strip()]
                        self.current_wall_values.append(int_row)
            except Exception as e:
                print(f"Error loading wall values: {e}")
        
        # Verify 8x13
        # Assign to cells? Or just keep in memory lookup?
        # Update cells to hold value for tooltips?
        if self.current_wall_values:
            for r in range(min(8, len(self.current_wall_values))):
                for c in range(min(13, len(self.current_wall_values[r]))):
                   self.cells[r][c].value = self.current_wall_values[r][c]
                   self.cells[r][c].setToolTip(f"Value: {self.current_wall_values[r][c]}")

    def on_cell_clicked(self, row, col):
        # Inspect Mode Logic (Always Active)
        if not self.current_wall_lattice or not self.current_wall_values:
             return
             
        # Identify Group
        try:
            gid = self.current_wall_lattice[row][col]
        except:
            return
            
        # Find all cells in this group
        group_cells = []
        values = []
        total = 0
        
        for r in range(8):
            for c in range(13):
                if self.current_wall_lattice[r][c] == gid:
                    val = self.current_wall_values[r][c]
                    values.append(val)
                    group_cells.append((r,c)) # Populate Coords
                    total += val
                    
        # Determine Growth Order
        ordered_values = self.get_growth_order(group_cells, gid)
        if not ordered_values:
             ordered_values = values # Fallback
             
        # Update UI - Values
        self.txt_values.setText(", ".join(map(str, ordered_values)))
        self.lbl_total.setText(str(total))
        
        # Update Grimoire Display
        wall_name = self.wall_selector.currentText()
        gid_str = str(gid)
        
        if wall_name in self.mythos_data and gid_str in self.mythos_data[wall_name]:
            entry = self.mythos_data[wall_name][gid_str]
            self.lbl_name.setText(entry.get("Name", f"Constellation #{gid}"))
            self.lbl_greek.setText(entry.get("GreekKey", ""))
            
            # Format HTML for Grimoire text
            html = self._format_grimoire_html(entry)
            self.txt_grimoire.setHtml(html)
        else:
            # Fallback if no Grimoire entry
            sym = str(gid)
            if gid == 10: sym = "A"
            if gid == 11: sym = "B"
            if gid == 12: sym = "C"
            self.lbl_name.setText(f"Constellation {sym}")
            self.lbl_greek.setText("")
            self.txt_grimoire.setPlainText("No Grimoire entry found for this constellation.")
    
    def _format_grimoire_html(self, entry):
        """Format Grimoire entry as styled HTML."""
        mythos = entry.get("Mythos", "").replace("\n", "<br>")
        texture = entry.get("Texture", "").replace("\n", "<br>")
        mantra = entry.get("Mantra", "")
        
        html = f"""
        <p style='color: #ccc; line-height: 1.6;'>
            <b style='color: #d4af37;'>⸭ THE MYTHOS ⸭</b><br><br>
            {mythos}
        </p>
        <hr style='border-color: #444;'>
        <p style='color: #aaa; line-height: 1.6;'>
            <b style='color: #888;'>⸭ THE TEXTURE ⸭</b><br><br>
            {texture}
        </p>
        <hr style='border-color: #444;'>
        <p style='color: #d4af37; font-style: italic; text-align: center; font-size: 11pt;'>
            {mantra}
        </p>
        """
        return html

    def on_cell_right_clicked(self, row, col, global_pos):
        """Handle right click on a cell to show context menu."""
        if not self.current_wall_lattice or not self.current_wall_values:
            return

        # Identify Group
        try:
            gid = self.current_wall_lattice[row][col]
        except:
            return
            
        if gid < 0:
            return # Empty space

        # Gather data
        group_cells = []
        values = []
        total = 0
        
        for r in range(8):
            for c in range(13):
                if self.current_wall_lattice[r][c] == gid:
                    val = self.current_wall_values[r][c]
                    values.append(val)
                    total += val
        
        # Determine Constellation Name
        sym = str(gid)
        if gid == 10: sym = "A"
        if gid == 11: sym = "B"
        if gid == 12: sym = "C"
        name = f"Constellation {sym}"

        # Create Menu
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
            }
            QMenu::item:selected {
                background-color: #e0e7ff;
                color: #1d4ed8;
            }
        """)
        
        # Header (Disabled Action)
        header = QAction(f"{name} (Σ {total})", self)
        header.setEnabled(False)
        menu.addAction(header)
        menu.addSeparator()

        # Action: Send Total to Quadset
        act_quadset = QAction("Send Total to Quadset Analysis", self)
        act_quadset.triggered.connect(lambda: self._send_to_quadset(total))
        menu.addAction(act_quadset)

        # Action: Send to Geometric Transitions (Octagon) -- only if 8 cells?
        # Adyton constellations are typically Octagons (8 stars).
        if len(values) == 8:
            act_geo = QAction("Send to Geometric Transitions (Octagon)", self)
            act_geo.triggered.connect(lambda: self._send_to_octagon(values))
            menu.addAction(act_geo)
        
        menu.exec(global_pos)

    def _send_to_quadset(self, total):
        if not self.window_manager:
            QMessageBox.warning(self, "Unavailable", "Window Manager not available.")
            return

        from pillars.tq.ui.quadset_analysis_window import QuadsetAnalysisWindow
        
        window = self.window_manager.open_window(
            "tq_quadset_analysis",
            QuadsetAnalysisWindow,
            allow_multiple=False,
            window_manager=self.window_manager
        )
        if window and hasattr(window, "input_field"):
            window.input_field.setText(str(total))
            window.raise_()
            window.activateWindow()

    def _send_to_octagon(self, values):
        if not self.window_manager:
            QMessageBox.warning(self, "Unavailable", "Window Manager not available.")
            return

        from pillars.tq.ui.geometric_transitions_window import GeometricTransitionsWindow
        
        window = self.window_manager.open_window(
            "tq_geometric_transitions",
            GeometricTransitionsWindow,
            allow_multiple=False,
            window_manager=self.window_manager
        )
        
        if window:
            # Set to Octagon (8 sides)
            # Find data=8
            idx = window.shape_combo.findData(8)
            if idx >= 0:
                window.shape_combo.setCurrentIndex(idx)
            
            # Populate inputs
            # Force refresh inputs just in case (though combo change triggers it usually)
            window._refresh_value_inputs()
            
            for i, val in enumerate(values):
                if i < len(window.value_inputs):
                    window.value_inputs[i].setText(str(val))
            
            # Raise
            window.raise_()
            window.activateWindow()
        

        
    def update_grid_overlay(self):
        show = self.chk_overlay.isChecked()
        grid = self.current_wall_lattice
        
        # Overlay colors for 13 groups
        tints = [
            "#330000", "#003300", "#000033", "#333300", "#330033", "#003333",
            "#442200", "#004422", "#220044", "#440022", "#224400", "#002244",
            "#222222"
        ]
        
        mst_edges = []
        
        if grid and show:
            # Calculate MST Edges
            mst_edges = self.calculate_mst_edges(grid)

        # Update Overlay with edges
        self.overlay.set_edges(mst_edges)
        
        # Identify Seeds
        seeds_map = {} # gid -> (r,c)
        if grid and show:
            seeds_map = self.calculate_seeds(grid)

        for r, row_list in enumerate(self.cells):
            for c, cell in enumerate(row_list):
                group_id = -1
                if grid and show:
                    try:
                        group_id = grid[r][c]
                    except:
                        pass
                
                # Update cell visual
                tint = tints[group_id % 13] if group_id >= 0 else None
                is_seed = (group_id >= 0 and seeds_map.get(group_id) == (r,c))
                cell.set_overlay(group_id, tint, is_seed)

    def calculate_seeds(self, lattice):
        """Calculates Geometric Center (Seed) for each group."""
        import collections
        groups = collections.defaultdict(list)
        rows, cols = 8, 13
        for r in range(rows):
            for c in range(cols):
                gid = lattice[r][c]
                if gid >= 0:
                    groups[gid].append((r,c))
        
        seeds = {}
        for gid, cells in groups.items():
            if not cells: continue
            
            # Adjacency
            adj = {cell: [] for cell in cells}
            cell_set = set(cells)
            for r, c in cells:
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r+dr, c+dc
                    if (nr, nc) in cell_set:
                        adj[(r,c)].append((nr,nc))
            
            # Eccentricity
            min_ecc = 999
            candidates = []
            for start_node in cells:
                q = collections.deque([(start_node, 0)])
                visited = {start_node}
                max_dist = 0
                while q:
                    curr, dist = q.popleft()
                    max_dist = max(max_dist, dist)
                    for nxt in adj[curr]:
                        if nxt not in visited:
                            visited.add(nxt)
                            q.append((nxt, dist+1))
                if max_dist < min_ecc:
                    min_ecc = max_dist
                    candidates = [start_node]
                elif max_dist == min_ecc:
                    candidates.append(start_node)
            
            seeds[gid] = sorted(candidates)[0]
        return seeds

    def get_growth_order(self, group_cells, gid):
        """Returns values ordered by distance from seed."""
        if not group_cells or not self.current_wall_values:
            return []
            
        import collections
        
        # 1. Build Adjacency
        adj = {cell: [] for cell in group_cells}
        cell_set = set(group_cells)
        for r, c in group_cells:
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r+dr, c+dc
                if (nr, nc) in cell_set:
                    adj[(r,c)].append((nr,nc))
                    
        # 2. Find Seed (Re-calculate ecc)
        min_ecc = 999
        candidates = []
        for start_node in group_cells:
            q = collections.deque([(start_node, 0)])
            visited = {start_node}
            max_dist = 0
            while q:
                curr, dist = q.popleft()
                max_dist = max(max_dist, dist)
                for nxt in adj[curr]:
                    if nxt not in visited:
                        visited.add(nxt)
                        q.append((nxt, dist+1))
            if max_dist < min_ecc:
                min_ecc = max_dist
                candidates = [start_node]
            elif max_dist == min_ecc:
                candidates.append(start_node)
        
        # Seed
        if not candidates: return []
        seed = sorted(candidates)[0]
        
        # 3. BFS for Order
        ordered_values = []
        q = collections.deque([(seed, 0)])
        visited = {seed}
        
        while q:
            curr, dist = q.popleft()
            val = self.current_wall_values[curr[0]][curr[1]]
            ordered_values.append(val)
            
            # Neighbors sorted for deterministic order
            neighbors = sorted(adj[curr])
            for nxt in neighbors:
                if nxt not in visited:
                    visited.add(nxt)
                    q.append((nxt, dist+1))
                    
        return ordered_values

    def calculate_mst_edges(self, lattice):
        """Calculates edges for Minimum Spanning Trees of clusters."""
        rows = 8
        cols = 13
        groups = {} 
        for r in range(rows):
            for c in range(cols):
                gid = lattice[r][c]
                if gid not in groups: groups[gid] = []
                groups[gid].append((r,c))
                
        edges = []
        for gid, cells in groups.items():
            if len(cells) < 2: continue
            
            connected = {cells[0]}
            unconnected = set(cells[1:])
            
            while unconnected:
                best_edge = None
                min_dist = 9999
                best_node = None
                
                for u in connected:
                    for v in unconnected:
                        d = (u[0]-v[0])**2 + (u[1]-v[1])**2
                        if d < min_dist:
                            min_dist = d
                            best_edge = (u, v)
                            best_node = v
                            
                if best_edge:
                    edges.append(best_edge)
                    connected.add(best_node)
                    unconnected.remove(best_node)
                else:
                    if unconnected:
                        start = list(unconnected)[0]
                        connected.add(start)
                        unconnected.remove(start)
        return edges


    def export_snapshot(self):
        """Grabs the grid frame and saves as PNG."""
        pixmap = self.grid_frame.grab()
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Snapshot", os.path.expanduser("~/wall_design.png"), "PNG Files (*.png)"
        )
        
        if filename:
            if not filename.endswith(".png"):
                filename += ".png"
            pixmap.save(filename)
            QMessageBox.information(self, "Export Successful", f"Saved directly to:\n{filename}")


