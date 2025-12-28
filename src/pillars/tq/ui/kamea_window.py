"""
Kamea Window - The Unified Field Visualizer.
Main window for the 27x27 Kamea grid with 2D/3D view switching, dimension filtering, and side panel analysis.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QStatusBar,
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QStatusBar,
    QToolBar, QComboBox, QCheckBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from ..services.kamea_grid_service import KameaGridService
from .kamea_grid_view import KameaGridView
from .kamea_fractal_view import KameaFractalView
from .fractal_network_dialog import FractalNetworkDialog
from .nuclear_mutation_panel import NuclearMutationPanel
from .baphomet_panel import BaphometPanel
from PyQt6.QtWidgets import QStackedLayout

class KameaWindow(QMainWindow):
    """
    Main Window for the Kamea Visualizer.
    Orchestrates the Grid View and Control/Info Panels.
    """
    def __init__(self, service: KameaGridService, parent=None):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Kamea of Maut - The Unified Field")
        self.resize(1200, 900)
        self.setStyleSheet("background-color: #050510; color: white;")
        
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget) # Changed to HBox for Side Panel
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Grid Container (to hold View + potential header)
        grid_container = QWidget()
        
        # Toolbar
        self._setup_toolbar()
        
        # Header (Optional, for now just the grid)
        # We can add a "Cosmic Dashboard" later.
        
        # Grid Stack (Switch between 2D and 3D)
        self.grid_stack = QStackedLayout(grid_container)
        
        # 2D Grid
        self.grid_view = KameaGridView(self.service)
        self.grid_view.cell_selected.connect(self._on_cell_selected)
        self.grid_stack.addWidget(self.grid_view)
        
        self.fractal_view = None
        self.network_dialog = None
        
        # self.init_ui() # Removed invalid call
        main_layout.addWidget(grid_container, stretch=1)
        
        # Right Sidebar Frame
        right_sidebar_frame = QWidget()
        right_sidebar_frame.setStyleSheet("background-color: #050510; border-left: 1px solid #333;")
        right_sidebar_layout = QVBoxLayout(right_sidebar_frame)
        right_sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Conditional Panel Loading
        if hasattr(self.service, 'variant') and self.service.variant == "Baphomet":
             self.mutation_panel = BaphometPanel()
        else:
             self.mutation_panel = NuclearMutationPanel()
             
        right_sidebar_layout.addWidget(self.mutation_panel)
        main_layout.addWidget(right_sidebar_frame)
        
        # Status Bar (for quick info)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Kamea Grid Loaded. Hover over cells to inspect.")
        self.status_bar.setStyleSheet("background-color: #1a1a2e; color: #a0a0ff;")

    def _setup_toolbar(self):
        toolbar = QToolBar("Kamea Controls")
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #1a1a2e;
                border: none;
                border-bottom: 2px solid #555;
            }
            QLabel { color: #a0a0ff; font-weight: bold; margin-right: 10px; }
            QComboBox {
                background-color: #050510;
                color: white;
                border: 1px solid #555;
                padding: 5px;
            }
        """)
        self.addToolBar(toolbar)
        
        # View Mode Label
        toolbar.addWidget(QLabel("   View Mode:"))
        
        # View Mode Combo
        self.view_combo = QComboBox()
        self.view_combo.addItems(["Decimal", "Ternary"])
        self.view_combo.currentTextChanged.connect(self._on_view_mode_changed)
        toolbar.addWidget(self.view_combo)

        # Dimension Filter Label
        toolbar.addWidget(QLabel("   Hypercube Filter:"))

        # Dimension Combo
        self.dim_combo = QComboBox()
        self.dim_combo.addItem("All Dimensions", None)
        self.dim_combo.addItem("6D Core (Unique)", 6)
        self.dim_combo.addItem("5D Axis (12)", 5)
        self.dim_combo.addItem("4D Faces (60)", 4)
        self.dim_combo.addItem("3D Cells (160)", 3)
        self.dim_combo.addItem("2D Planes (240)", 2)
        self.dim_combo.addItem("1D Lines (192)", 1)
        self.dim_combo.addItem("0D Leaves (64)", 0)
        self.dim_combo.currentIndexChanged.connect(self._on_filter_changed)
        self.dim_combo.currentIndexChanged.connect(self._on_filter_changed)
        toolbar.addWidget(self.dim_combo)
        
        # 3D Toggle Action
        toolbar.addSeparator()
        self.toggle_3d_action = QAction("Switch to 3D", self)
        self.toggle_3d_action.setCheckable(True)
        self.toggle_3d_action.triggered.connect(self._toggle_view_stack)
        toolbar.addAction(self.toggle_3d_action)
        
        # Fractal Tree Toggle (Checkbox)
        self.tree_check = QCheckBox("Show Fractal Tree")
        self.tree_check.setStyleSheet("color: #a0a0ff; margin-left: 10px;")
        self.tree_check.toggled.connect(self._on_tree_toggled)
        self.tree_check.setEnabled(False) # Disabled in 2D mode
        toolbar.addWidget(self.tree_check)

    def _on_tree_toggled(self, checked):
        if self.fractal_view:
            self.fractal_view.set_show_connections(checked)

    def _toggle_view_stack(self, checked):
        if checked:
            if self.fractal_view is None:
                self.fractal_view = KameaFractalView()
                self.fractal_view.cell_clicked.connect(self._on_fractal_cell_selected)
                self.fractal_view.focus_changed.connect(self._on_focus_changed)
                if self.tree_check.isChecked():
                    self.fractal_view.set_show_connections(True)
                self.grid_stack.addWidget(self.fractal_view)
            
            self.grid_stack.setCurrentWidget(self.fractal_view)
            self.toggle_3d_action.setText("Switch to 2D")
            self.tree_check.setEnabled(True)
            self.dim_combo.setEnabled(False) # Filters apply to grid mostly, maybe disable for now
        else:
            self.grid_stack.setCurrentWidget(self.grid_view)
            self.toggle_3d_action.setText("Switch to 3D")
            self.tree_check.setEnabled(False)
            self.tree_check.setChecked(False) # Auto-off when going back to 2D
            self.dim_combo.setEnabled(True)

    def _on_filter_changed(self, index):
        data = self.dim_combo.currentData() # Returns int or None
        self.grid_view.set_dimension_filter(data)
        
    def _on_view_mode_changed(self, text):
        mode = text.lower()
        self.grid_view.set_view_mode(mode)

    def _on_cell_selected(self, cell):
        """Pass selection to the Reactor."""
        self.mutation_panel.analyze_cell(cell)

    def _on_fractal_cell_selected(self, ternary_value):
        """Handle selection from 3D View."""
        # Find cell data from service
        # Simple search (could be optimized)
        for cell in self.service.cells:
            if cell.ternary_value == ternary_value:
                self.mutation_panel.analyze_cell(cell)
                break

    def _on_focus_changed(self, ternary):
        """Handle focus updates from 3D view (open/update popup)."""
        if self.network_dialog is None:
            self.network_dialog = FractalNetworkDialog(self)
            
        if ternary:
            self.network_dialog.update_network(ternary)
            self.network_dialog.show()
            self.network_dialog.raise_()
        else:
            self.network_dialog.hide()
