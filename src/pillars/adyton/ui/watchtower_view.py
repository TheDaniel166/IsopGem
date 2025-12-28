"""
Watchtower View - The Enochian Tablet Visualizer.
Displays a 156-cell Watchtower using flattened pyramids with multiple view modes for wall, Kerubic, and hexameric analysis.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QHBoxLayout, 
    QComboBox, QLabel, QPushButton, QSlider
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from typing import List, Dict

from pillars.adyton.services.kamea_loader_service import KameaLoaderService
from pillars.adyton.services.kamea_color_service import KameaColorService
from pillars.adyton.ui.kamea_pyramid_cell import KameaPyramidCell
from pillars.adyton.models.kamea_cell import KameaCell

class WatchtowerView(QWidget):
    """
    Displays the 156 cells of an Enochian Watchtower using
    Flattened Truncated Pyramid cells.
    """
    
    def __init__(self, loader_service: KameaLoaderService, parent=None):
        """
          init   logic.
        
        Args:
            loader_service: Description of loader_service.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.loader = loader_service
        # Initialize Color Service
        # Loader has project_root, let's assume availability or pass it
        self.color_service = KameaColorService(self.loader.project_root)
        
        self.cells_map = self.loader.load_grid()
        
        self.current_scale = 70
        self.current_cell_size = 60
        self.current_tablet_cells = []
        self.current_octants = []
        
        self.init_ui()

        
    def init_ui(self):
        # Main Layout (Vertical) containing Toolbar and Content Area
        """
        Initialize ui logic.
        
        """
        self.main_layout = QVBoxLayout(self)
        
        # --- Toolbar ---
        toolbar = QHBoxLayout()
        self.tablet_selector = QComboBox()
        self.tablet_selector.addItems(["Air (East)", "Water (West)", "Earth (North)", "Fire (South)"])
        self.tablet_selector.currentTextChanged.connect(self.load_tablet)
        
        toolbar.addWidget(QLabel("Watchtower:"))
        toolbar.addWidget(self.tablet_selector)
        
        # Zoom Slider
        toolbar.addSpacing(20)
        toolbar.addWidget(QLabel("Zoom:"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(30)
        self.zoom_slider.setMaximum(150)
        self.zoom_slider.setValue(70)
        self.zoom_slider.setSingleStep(5)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        toolbar.addWidget(self.zoom_slider)
        
        # View Mode Selector
        toolbar.addSpacing(20)
        toolbar.addWidget(QLabel("View:"))
        self.view_selector = QComboBox()
        self.view_selector.addItems(["Standard", "Wall Distribution", "Kerubic Squares", "Hexameric Lattice", "Hexameric Clusters"])
        self.view_selector.currentTextChanged.connect(self.on_view_mode_changed)
        toolbar.addWidget(self.view_selector)
        
        # Cluster Algorithm Selector (Visible only in Hexameric Clusters mode effectively)
        toolbar.addSpacing(20)
        toolbar.addWidget(QLabel("Algo:"))
        self.cluster_algo_selector = QComboBox()
        self.cluster_algo_selector.addItems(["Sunburst", "Gnomonic", "Serpentine"])
        self.cluster_algo_selector.currentTextChanged.connect(self.rebuild_widgets)
        toolbar.addWidget(self.cluster_algo_selector)
        
        toolbar.addStretch()
        
        self.main_layout.addLayout(toolbar)
        
        # --- Content Area (Splitter or HBox) ---
        content_layout = QHBoxLayout()
        
        # Left: Scroll Area for the massive tablet
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True) 
        self.tablet_container = QWidget()
        self.tablet_container.setMinimumSize(2000, 2000) 
        self.scroll.setWidget(self.tablet_container)
        
        # Right: Detail Panel
        self.detail_panel = QFrame()
        self.detail_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.detail_panel.setMinimumWidth(250)
        self.detail_panel.setMaximumWidth(300)
        
        self._init_detail_panel()
        
        content_layout.addWidget(self.scroll, stretch=1)
        content_layout.addWidget(self.detail_panel, stretch=0)
        
        self.main_layout.addLayout(content_layout)
        
        # Wall Colors (Planetary)
        self.wall_colors = [
            QColor("#f59e0b"), # 0: Sun
            QColor("#64748b"), # 1: Mercury
            QColor("#94a3b8"), # 2: Moon
            QColor("#ec4899"), # 3: Venus
            QColor("#8b5cf6"), # 4: Jupiter
            QColor("#dc2626"), # 5: Mars
            QColor("#1e293b"), # 6: Saturn
        ]
        
        # Load Authentic Wall Map
        self.wall_map = self.loader.load_wall_map()
        
        # Initial Load
        self.load_tablet("Air (East)")
        
    def on_view_mode_changed(self, mode: str):
        """
        Handle view mode changed logic.
        
        Args:
            mode: Description of mode.
        
        """
        self.rebuild_widgets()

    def _init_detail_panel(self):
        layout = QVBoxLayout(self.detail_panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Header
        self.lbl_header = QLabel("Cell Details")
        self.lbl_header.setStyleSheet("font-weight: bold; font-size: 14pt; color: #8FBC8F;")
        
        # Attributes
        self.lbl_ditrune = QLabel("Ditrune: -")
        self.lbl_decimal = QLabel("Decimal: -")
        self.lbl_coords = QLabel("Coords: -")
        self.lbl_octant = QLabel("Octant: -")
        self.lbl_tablet = QLabel("Tablet: -")
        self.lbl_wall = QLabel("Wall: -") # New
        
        self.lbl_ditrune.setStyleSheet("font-family: monospace; font-size: 12pt;")
        
        # Add to layout
        layout.addWidget(self.lbl_header)
        layout.addSpacing(10)
        layout.addWidget(self.lbl_ditrune)
        layout.addWidget(self.lbl_decimal)
        layout.addWidget(self.lbl_coords)
        layout.addWidget(self.lbl_octant)
        layout.addWidget(self.lbl_tablet)
        layout.addWidget(self.lbl_wall)
        
        layout.addStretch()

    def on_zoom_changed(self, value):
        """
        Handle zoom changed logic.
        
        Args:
            value: Description of value.
        
        """
        self.current_scale = value
        # Adjust cell size proportional to scale (approx 85% of grid unit)
        self.current_cell_size = int(value * 0.85)
        self.refresh_layout()

    def load_tablet(self, tablet_name: str):
        # Determine Target Octants based on Name
        """
        Load tablet logic.
        
        Args:
            tablet_name: Description of tablet_name.
        
        """
        target_octants = []
        if "Air" in tablet_name: target_octants = [1, 5]
        elif "Water" in tablet_name: target_octants = [3, 7]
        elif "Fire" in tablet_name: target_octants = [2, 6]
        elif "Earth" in tablet_name: target_octants = [4, 8]
        
        # Filter Cells
        cells = [c for c in self.cells_map.values() if c.octant_id in target_octants]
        
        self.render_tablet(cells, target_octants)

    def render_tablet(self, cells: List[KameaCell], octants: List[int]):
        # Store cells and octants
        """
        Render tablet logic.
        
        Args:
            cells: Description of cells.
            octants: Description of octants.
        
        """
        self.current_tablet_cells = cells
        self.current_octants = octants
        
        # Partition cells into two sets: Upward Triangle and Downward Triangle
        # We assume the first octant in the list is the "Positive" (Upward) one, 
        # and the second is the "Negative" (Downward).
        # e.g. Air: [1, 5]. 1 is Up, 5 is Down.
        
        self.triangle_up_cells = [c for c in cells if c.octant_id == octants[0]]
        self.triangle_down_cells = [c for c in cells if c.octant_id == octants[1]]
        
        # Sort each set by "Shell" (Radius)
        # Shell = max(abs(x), abs(y))
        # For Octant 1: x is the shell index (2..13). y is the sub-index.
        # We want row 0 to be the tip (Shell 2).
        self.triangle_up_cells.sort(key=lambda c: (max(abs(c.x), abs(c.y)), c.y)) # y varies within x shell
        self.triangle_down_cells.sort(key=lambda c: (max(abs(c.x), abs(c.y)), c.y))
        
        self.rebuild_widgets()
        self.refresh_layout()

    def rebuild_widgets(self):
        # Clear previous cells
        """
        Rebuild widgets logic.
        
        """
        for child in self.tablet_container.children():
            if isinstance(child, KameaPyramidCell):
                child.deleteLater()
        
        self.active_widgets = []
        mode = self.view_selector.currentText()
        
        # --- Hexameric Clusters Mode Pre-calculation ---
        cluster_map = {}
        if mode == "Hexameric Clusters":
            algo = self.cluster_algo_selector.currentText()
            
            # Helper to sort and assign groups
            def assign_groups(cells_list):
                """
                Assign groups logic.
                
                Args:
                    cells_list: Description of cells_list.
                
                """
                if not cells_list: return
                
                # Sort based on Algo
                if algo == "Sunburst":
                    # Angular sort: slope = abs(y/x)
                    def key_func(c):
                        """
                        Key func logic.
                        
                        Args:
                            c: Description of c.
                        
                        """
                        if c.x == 0: return 99.0
                        return abs(c.y / c.x)
                    cells_list.sort(key=key_func)
                    
                elif algo == "Gnomonic":
                    # Shell sort: (shell, y)
                    # Expands from center outwards
                    cells_list.sort(key=lambda c: (max(abs(c.x), abs(c.y)), abs(c.y)))
                    
                elif algo == "Serpentine":
                    # Diagonal sort: (x+y, x)
                    # Scans across the octant
                    cells_list.sort(key=lambda c: (abs(c.x) + abs(c.y), abs(c.x)))
                
                # Assign 0, 1, 2
                # 78 cells -> 26 per group
                for i, c in enumerate(cells_list):
                    grp = 0
                    if i >= 26: grp = 1
                    if i >= 52: grp = 2
                    cluster_map[c.decimal_value] = grp
            
            # Process Octant 1 (Upward)
            oct1 = [c for c in self.current_tablet_cells if c.octant_id == self.current_octants[0]]
            assign_groups(oct1)
            
            # Process Octant 5 (Downward)
            oct5 = [c for c in self.current_tablet_cells if c.octant_id == self.current_octants[1]]
            assign_groups(oct5)

        # Helper to create widget
        def create_widget(cell: KameaCell):
            """
            Create widget logic.
            
            Args:
                cell: Description of cell.
            
            """
            widget = KameaPyramidCell(cell.ditrune, cell.decimal_value, size=self.current_cell_size, parent=self.tablet_container)
            
            # Resolve Colors (default)
            c_top, c_bot, c_left, c_right, c_cap = self.color_service.resolve_colors(cell)
            
            # --- APPLY VIEW MODES ---
            
            # Initialize wall_idx for click handler
            wall_idx_for_click = -1

            # 1. Kerubic
            if mode == "Kerubic Squares":
                # Geometry: Octant 1 (Up) & Octant 5 (Down)
                # Split each into Upper/Lower Wedge
                
                # Default
                c_base = QColor("#444444")
                
                if cell.octant_id == 1:
                    # Upward Triangle (East)
                    if cell.y > (cell.x / 2):
                        c_base = QColor("#fde047") # Yellow (Air of Air)
                    else:
                        c_base = QColor("#3b82f6") # Blue (Water of Air)
                elif cell.octant_id == 5:
                    # Downward Triangle (West? but mapped to Air Tablet here)
                    # Note: x, y are negative. 
                    # Logic: Upper Wedge vs Lower Wedge in visual space?
                    # Script said: y > x/2 was "Upper Half" (C).
                    if cell.y > (cell.x / 2):
                        c_base = QColor("#10b981") # Green (Earth of Air)
                    else:
                        c_base = QColor("#ef4444") # Red (Fire of Air)
                
                # Apply Base
                c_top = c_base
                c_bot = c_base.darker(110)
                c_left = c_base.darker(115)
                c_right = c_base.darker(120)
                c_cap = c_base.lighter(130)
                
                # Kerubic Highlight (Outermost Shells)
                shell = max(abs(cell.x), abs(cell.y))
                if shell >= 11:
                    c_cap = QColor("#FFFFFF") # White Cap for Kerubim
                    c_top = c_top.lighter(120)

            # 2. Lattice
            elif mode == "Hexameric Lattice":
                # Logic: (x + y) % 3
                # Creates 3 interlaced groups of 26 cells per Octant.
                mod = (cell.x + cell.y) % 3
                
                c_base = QColor("#444444")
                
                if cell.octant_id == 1:
                    # Upward
                    if mod == 0: c_base = QColor("#06b6d4") # Cyan
                    elif mod == 1: c_base = QColor("#d946ef") # Magenta
                    elif mod == 2: c_base = QColor("#eab308") # Yellow
                elif cell.octant_id == 5:
                    # Downward
                    if mod == 0: c_base = QColor("#ef4444") # Red
                    elif mod == 1: c_base = QColor("#22c55e") # Green
                    elif mod == 2: c_base = QColor("#3b82f6") # Blue
                    
                c_top = c_base
                c_bot = c_base.darker(110)
                c_left = c_base.darker(115)
                c_right = c_base.darker(120)
                c_cap = c_base.lighter(130)

            # 3. Clusters (Dynamic Algo)
            elif mode == "Hexameric Clusters":
                group = cluster_map.get(cell.decimal_value, 0)
                
                c_base = QColor("#444444")
                if cell.octant_id == self.current_octants[0]: # Upward
                    if group == 0: c_base = QColor("#06b6d4") # Cyan (Inner/Bot)
                    elif group == 1: c_base = QColor("#d946ef") # Magenta (Mid)
                    elif group == 2: c_base = QColor("#eab308") # Yellow (Outer/Top)
                elif cell.octant_id == self.current_octants[1]: # Downward
                    if group == 0: c_base = QColor("#ef4444") # Red
                    elif group == 1: c_base = QColor("#22c55e") # Green
                    elif group == 2: c_base = QColor("#3b82f6") # Blue
                    
                c_top = c_base
                c_bot = c_base.darker(110)
                c_left = c_base.darker(115)
                c_right = c_base.darker(120)
                c_cap = c_base.lighter(130)

            # 4. Wall Distribution
            elif mode == "Wall Distribution":
                val = cell.decimal_value
                if val == 364 or val == 0: # Axis Mundi
                    c_wall = QColor("#FFFFFF")
                    wall_idx_for_click = 99
                else:
                    wall_idx_for_click = self.wall_map.get(val, -1)
                    if 0 <= wall_idx_for_click < len(self.wall_colors):
                        c_wall = self.wall_colors[wall_idx_for_click]
                    else:
                        c_wall = QColor("#555555") # Fallback
                
                # Apply Solid Color
                c_top = c_wall
                c_bot = c_wall.darker(110)
                c_left = c_wall.darker(115)
                c_right = c_wall.darker(120)
                c_cap = c_wall.lighter(130)

            widget.set_side_colors(c_top, c_bot, c_left, c_right)
            widget.set_cap_color(c_cap)
            
            # Connect Click
            widget.clicked.connect(lambda c=cell, w=widget, widx=wall_idx_for_click: self.on_cell_clicked(c, w, widx))
            
            widget.show()
            return widget

        # Create widgets for Up Triangle
        self.up_widgets = []
        for cell in self.triangle_up_cells:
            w = create_widget(cell)
            self.up_widgets.append((cell, w))
            
        # Create widgets for Down Triangle
        self.down_widgets = []
        for cell in self.triangle_down_cells:
            w = create_widget(cell)
            self.down_widgets.append((cell, w))
            
        # Unified list for general access if needed
        self.active_widgets = self.up_widgets + self.down_widgets

    def on_cell_clicked(self, cell: KameaCell, widget: KameaPyramidCell, wall_idx: int = -1):
        # Update Detail Panel
        """
        Handle cell clicked logic.
        
        Args:
            cell: Description of cell.
            widget: Description of widget.
            wall_idx: Description of wall_idx.
        
        """
        self.lbl_ditrune.setText(f"Ditrune: {cell.ditrune}")
        self.lbl_decimal.setText(f"Decimal: {cell.decimal_value}")
        self.lbl_coords.setText(f"Coords: ({cell.x}, {cell.y})")
        self.lbl_octant.setText(f"Octant: {cell.octant_id}")
        self.lbl_tablet.setText(f"Tablet: {cell.tablet_id}")
        
        if wall_idx == 99:
            self.lbl_wall.setText("Wall: Axis Mundi")
        elif wall_idx != -1:
            self.lbl_wall.setText(f"Wall: {wall_idx} (Planetary)")
        else:
            # Calculate it anyway for standard mode
            val = cell.decimal_value
            if val in self.wall_map:
                 w_idx = self.wall_map[val]
                 self.lbl_wall.setText(f"Wall: {w_idx}")
            else:
                 self.lbl_wall.setText("Wall: -")
        
        # Reset Selection visual (if we implement selection state on widgets)
        for _, w in self.active_widgets:
            w.set_selected(False)
        widget.set_selected(True)

    def refresh_layout(self):
        """
        Lays out the two triangles to form a Diamond (Base-to-Base).
        """
        scale = self.current_scale
        cell_size = self.current_cell_size
        spacing = 0 # No gaps as per user request
        row_height = cell_size + spacing
        
        # Center of Canvas
        cx = 1000
        cy = 1000
        
        # Height of a triangle (Shells 2 to 13 = 12 Rows)
        # Distance from Tip to Base Row CENTER is 11 * row_height
        tri_h = 11 * row_height
        
        # We want the BASES to meet at cy.
        # Up Triangle Base (Row 11) Bottom Edge = cy
        # Down Triangle Base (Row 11) Top Edge = cy
        
        base_gap = 0 # Bases touch perfectly
        
        # --- Up Triangle (Points Up) ---
        # Tip (Row 0) is roughly at top. Base (Row 11) is at bottom.
        # Top-Left Y of Base Row = start_y_up + 11*row_height
        # Bottom Edge of Base Row = start_y_up + 11*row_height + cell_size
        
        # Equation: start_y_up + 11*row_height + cell_size = cy - (base_gap / 2)
        start_y_up = cy - (base_gap / 2) - cell_size - (11 * row_height)
        
        # --- Down Triangle (Points Down) ---
        # Tip (Row 0) is roughly at bottom. Base (Row 11) is at top.
        # Top-Left Y of Base Row = start_y_down - 11*row_height
        # Top Edge of Base Row = start_y_down - 11*row_height (since it's Top-Left)
        
        # Equation: start_y_down - 11*row_height = cy + (base_gap / 2)
        start_y_down = cy + (base_gap / 2) + (11 * row_height)
        
        # Adjust container if zoomed
        total_h = (12 * row_height) * 2.5 + 500
        self.tablet_container.setMinimumSize(2000, int(total_h))
        
        # Helper: Layout a single triangle
        # direction: 1 for Point Up (Rows go down Y), -1 for Point Down (Rows go up Y)
        def layout_triangle(widgets, start_y, direction):
            """
            Layout triangle logic.
            
            Args:
                widgets: Description of widgets.
                start_y: Description of start_y.
                direction: Description of direction.
            
            """
            current_idx = 0
            for row_idx in range(12): # 12 rows
                num_in_row = row_idx + 1
                row_widgets = widgets[current_idx : current_idx + num_in_row]
                current_idx += num_in_row
                
                # Y Position (Top-Left corner of the cell)
                y_pos = start_y + (direction * row_idx * row_height)
                
                # X Position: Center the row
                row_width = (num_in_row * cell_size) + ((num_in_row - 1) * spacing)
                start_x = cx - (row_width / 2)
                
                for i, (cell, widget) in enumerate(row_widgets):
                    x_pos = start_x + (i * (cell_size + spacing))
                    widget.setFixedSize(cell_size, cell_size)
                    widget.move(int(x_pos), int(y_pos))
                    widget.raise_()
                    
        # Apply Layouts
        layout_triangle(self.up_widgets, start_y_up, 1)     # Up Triangle (Base at bottom)
        layout_triangle(self.down_widgets, start_y_down, -1) # Down Triangle (Base at top)