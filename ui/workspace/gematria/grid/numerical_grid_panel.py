from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QTableWidget, QTableWidgetItem, QLabel, QPushButton,
                            QDockWidget, QHeaderView, QComboBox, QApplication)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QColor, QBrush
from core.gematria.calculator import GematriaCalculator
from .grid_panel_properties import GridPanelProperties

class NumericalGridPanel(QMainWindow):
    def __init__(self, original_grid, option_name):
        super().__init__()
        
        # Store references
        self.calculator = GematriaCalculator()
        self.original_grid = original_grid
        self.rows = original_grid.rows
        self.cols = original_grid.cols
        self.option_name = option_name
        self.zoom_level = 1.0
        self.zoom_factor = 0.1

        # Calculate initial cell sizes based on viewport
        screen_rect = QApplication.primaryScreen().availableGeometry()
        initial_cell_width = min(600 // self.cols, screen_rect.width() // self.cols)
        initial_cell_height = min(400 // self.rows, screen_rect.height() // self.rows)

        # Current properties initialization
        self.current_properties = {
            'cell_width': max(40, initial_cell_width),
            'cell_height': max(25, initial_cell_height),
            'line_color': '#000000',
            'bg_color': '#FFFFFF',
            'text_color': '#000000',
            'line_thickness': 1,
            'auto_fit': False,
            'square_cells': False
        }

        # Window setup
        self.setWindowTitle(f"Numerical Grid - {option_name}")
        self.setMinimumSize(650, 450)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Setup components
        self.setup_ui()
        self.setup_cipher_selection()
        self.setup_numerical_search()
        self.setup_numerical_functions()
        self.convert_and_update_grid()
        self.apply_grid_properties(self.current_properties)
        
        self.grid_table.viewport().installEventFilter(self)

    def setup_ui(self):
        # Create header layout
        header_layout = QHBoxLayout()

        # Configure header label
        header = QLabel(f"{self.option_name} - {self.rows}x{self.cols} Grid")
        header.setAlignment(Qt.AlignCenter)
        
        # Setup settings button
        settings_button = QPushButton("⚙")
        settings_button.setFixedSize(30, 30)
        settings_button.clicked.connect(self.show_properties)
        
        # Add header components
        header_layout.addWidget(header)
        header_layout.addWidget(settings_button)
        self.layout.addLayout(header_layout)

        # Initialize grid table
        self.grid_table = QTableWidget(self.rows, self.cols)
        self.grid_table.setMinimumWidth(800)

        # Configure scrollbars
        self.grid_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.grid_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Configure headers
        header = self.grid_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setDefaultSectionSize(40)
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignLeft)

        vertical_header = self.grid_table.verticalHeader()
        vertical_header.setSectionResizeMode(QHeaderView.Fixed)
        vertical_header.setDefaultSectionSize(25)
        vertical_header.setFixedWidth(30)

        # Generate and set headers
        horizontal_headers = [str(i+1) for i in range(self.cols)]
        vertical_headers = [str(i+1) for i in range(self.rows)]
        self.grid_table.setHorizontalHeaderLabels(horizontal_headers)
        self.grid_table.setVerticalHeaderLabels(vertical_headers)

        # Optimize performance
        self.grid_table.setWordWrap(False)
        self.grid_table.setTextElideMode(Qt.ElideNone)
        self.grid_table.setShowGrid(True)
        self.grid_table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.grid_table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)

        # Configure tooltips
        self.grid_table.setToolTipDuration(5000)
        self.grid_table.setMouseTracking(True)
        self.grid_table.viewport().setMouseTracking(True)

        # Create empty grid
        for row in range(self.rows):
            for col in range(self.cols):
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignCenter)
                self.grid_table.setItem(row, col, item)

        # Add grid to layout
        self.layout.addWidget(self.grid_table)
        
    def show_properties(self):
        props_dialog = GridPanelProperties(self)
        props_dialog.propertiesChanged.connect(self.apply_grid_properties)
        props_dialog.exec_()

    def apply_grid_properties(self, properties):
        self.current_properties.update(properties)
        
        # Apply cell sizes
        for col in range(self.cols):
            self.grid_table.setColumnWidth(col, self.current_properties['cell_width'])
        for row in range(self.rows):
            self.grid_table.setRowHeight(row, self.current_properties['cell_height'])
        
        # Apply styling
        style = f"""
            QTableWidget {{
                gridline-color: {self.current_properties['line_color']};
                background-color: {self.current_properties['bg_color']};
            }}
            QTableWidget::item {{
                color: {self.current_properties['text_color']};
                padding: 2px;
            }}
        """
        self.grid_table.setStyleSheet(style)

          
    def setup_cipher_selection(self):
        toolbar_layout = QHBoxLayout()
        self.cipher_combo = QComboBox()
        self.cipher_combo.addItems([
            'TQ English',
            'Hebrew Standard', 
            'Hebrew Gadol',
            'Greek'
        ])
        self.cipher_combo.currentIndexChanged.connect(self.update_values)
        toolbar_layout.addWidget(QLabel("Cipher:"))
        toolbar_layout.addWidget(self.cipher_combo)
        
    def setup_numerical_search(self):
        from .numerical_grid_search import NumericalGridSearch
        self.search_widget = NumericalGridSearch(self)
        search_dock = QDockWidget("Numerical Search", self)
        search_dock.setWidget(self.search_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, search_dock)
        
    def setup_numerical_functions(self):
        from .numerical_grid_functions import NumericalGridFunctions
        self.functions_widget = NumericalGridFunctions(self)
        functions_dock = QDockWidget("Grid Analysis", self)
        functions_dock.setWidget(self.functions_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, functions_dock)
        
    def convert_and_update_grid(self):
        for row in range(self.rows):
            for col in range(self.cols):
                original_item = self.original_grid.grid_table.item(row, col)
                if original_item:
                    char = original_item.text()
                    if char.isspace() or not char.isalnum():
                        value = '0'
                    else:
                        value = str(self.calculator.calculate(char, 
                                  self.cipher_combo.currentText()))
                    self.grid_table.item(row, col).setText(value)
                    
    def update_values(self):
        self.convert_and_update_grid()
        
def show_properties(self):
    props_dialog = GridPanelProperties(self)
    props_dialog.propertiesChanged.connect(self.apply_grid_properties)
    props_dialog.exec_()

def apply_grid_properties(self, properties):
    self.current_properties.update(properties)
    # Apply cell sizes
    for col in range(self.cols):
        self.grid_table.setColumnWidth(col, self.current_properties['cell_width'])
    for row in range(self.rows):
        self.grid_table.setRowHeight(row, self.current_properties['cell_height'])
    
    # Apply styling
    self.apply_grid_styling()

def apply_grid_styling(self):
    style = f"""
        QTableWidget {{
            gridline-color: {self.current_properties['line_color']};
            background-color: {self.current_properties['bg_color']};
        }}
        QTableWidget::item {{
            color: {self.current_properties['text_color']};
            padding: 2px;
        }}
    """
    self.grid_table.setStyleSheet(style)

def eventFilter(self, source, event):
    if source is self.grid_table.viewport() and event.type() == QEvent.Wheel:
        if event.modifiers() == Qt.ControlModifier:
            self.handle_zoom(event)
            return True
    return super().eventFilter(source, event)

def handle_zoom(self, event):
    delta = event.angleDelta().y()
    if delta > 0:
        self.zoom_level += self.zoom_factor
    else:
        self.zoom_level = max(0.1, self.zoom_level - self.zoom_factor)
    
    new_width = int(self.current_properties['cell_width'] * self.zoom_level)
    new_height = int(self.current_properties['cell_height'] * self.zoom_level)
    
    for col in range(self.cols):
        self.grid_table.setColumnWidth(col, new_width)
    for row in range(self.rows):
        self.grid_table.setRowHeight(row, new_height)

def resizeEvent(self, event):
    super().resizeEvent(event)
    if self.current_properties['auto_fit']:
        self.optimize_grid_display()

def optimize_grid_display(self):
    viewport_width = self.grid_table.viewport().width()
    viewport_height = self.grid_table.viewport().height()
    
    optimal_col_width = max(40, (viewport_width - 50) // self.cols)
    optimal_row_height = max(25, (viewport_height - 50) // self.rows)
    
    for col in range(self.cols):
        self.grid_table.setColumnWidth(col, optimal_col_width)
    for row in range(self.rows):
        self.grid_table.setRowHeight(row, optimal_row_height)

