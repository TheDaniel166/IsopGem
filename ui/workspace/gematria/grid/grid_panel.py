from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QTableWidget, QTableWidgetItem, QLabel, QPushButton,
                            QDockWidget, QHeaderView, QScrollArea, QApplication)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QWheelEvent, QColor, QBrush 
from .grid_panel_properties import GridPanelProperties
from .grid_search import GridSearch

class GridPanel(QMainWindow):
    def __init__(self, text, rows, cols, option_name):
        super().__init__()

        # Ensure minimum dimensions
        self.rows = max(1, rows)
        self.cols = max(1, cols)
        self.text = text or ""  # Handle None case
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
        self.setWindowTitle(f"Grid View - {option_name}")
        self.setMinimumSize(650, 450)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.setup_ui()
        self.create_grid()
        self.apply_grid_properties(self.current_properties)
        
        self.grid_table.viewport().installEventFilter(self)

    def setup_ui(self):
        """Initialize and configure the user interface components."""
        # Create header layout
        header_layout = QHBoxLayout()

        # Configure header label
        header = QLabel(f"{self.option_name} - {self.rows}x{self.cols} Grid")
        header.setAlignment(Qt.AlignCenter)
        
        # Setup settings button
        settings_button = QPushButton("⚙")
        settings_button.setFixedSize(30, 30)
        settings_button.clicked.connect(self.show_properties)
        
        # Setup numerical grid button
        numerical_button = QPushButton("Show Numerical Grid")
        numerical_button.clicked.connect(self.open_numerical_grid)        
        
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

        # Setup search
        self.search_widget = GridSearch(self)
        search_dock = QDockWidget("Search", self)
        search_dock.setWidget(self.search_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, search_dock)
        self.search_widget.searchResultsFound.connect(self.highlight_search_results)

        # Add grid to layout
        self.layout.addWidget(self.grid_table)

    def create_grid(self):
        char_index = 0
        for i in range(self.rows):
            for j in range(self.cols):
                # Always create an item, even if no character
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignCenter)
                
                if char_index < len(self.text):
                    item.setText(self.text[char_index])
                    position_info = f"Character: {self.text[char_index]}\nPosition: {char_index + 1}\nRow: {i + 1}\nColumn: {j + 1}"
                    item.setToolTip(position_info)
                    char_index += 1
                
                self.grid_table.setItem(i, j, item)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.optimize_grid_display()

    def optimize_grid_display(self):
        """Optimize grid display for current dimensions"""
        viewport_width = self.grid_table.viewport().width()
        viewport_height = self.grid_table.viewport().height()
        
        # Calculate minimum sizes while maintaining visibility
        min_col_width = 40
        min_row_height = 25
        
        # Calculate optimal sizes
        optimal_col_width = max(min_col_width, (viewport_width - 50) // self.cols)
        optimal_row_height = max(min_row_height, (viewport_height - 50) // self.rows)
        
        # Apply sizes
        for col in range(self.cols):
            self.grid_table.setColumnWidth(col, optimal_col_width)
        for row in range(self.rows):
            self.grid_table.setRowHeight(row, optimal_row_height)
        
        # Force update
        self.grid_table.viewport().update()

    def highlight_search_results(self, positions):
        """Highlight cells in the grid that match search criteria."""
        self.clear_highlights()
        highlight_color = QColor(255, 255, 0, 100)
        for row, col in positions:
            item = self.grid_table.item(row, col)
            if item:
                item.setBackground(QBrush(highlight_color))

    def clear_highlights(self):
        """Remove all highlighting from grid cells."""
        for row in range(self.rows):
            for col in range(self.cols):
                item = self.grid_table.item(row, col)
                if item:
                    item.setBackground(QBrush(QColor(self.current_properties['bg_color'])))

    def eventFilter(self, source, event):
        if source is self.grid_table.viewport() and event.type() == QEvent.Wheel:
            if event.modifiers() == Qt.ControlModifier:
                delta = event.angleDelta().y()
                if delta > 0:
                    self.zoom_level += self.zoom_factor
                else:
                    self.zoom_level = max(0.1, self.zoom_level - self.zoom_factor)
                
                new_width = int(600 * self.zoom_level)
                new_height = int(400 * self.zoom_level)
                
                # Update cell sizes with zoom
                cell_width = max(40, new_width // min(self.cols, 20))
                cell_height = max(25, new_height // min(self.rows, 40))
                
                for col in range(self.cols):
                    self.grid_table.setColumnWidth(col, cell_width)
                for row in range(self.rows):
                    self.grid_table.setRowHeight(row, cell_height)
                    
                return True
        return super().eventFilter(source, event)

    def show_properties(self):
        props_dialog = GridPanelProperties(self)
        props_dialog.propertiesChanged.connect(self.apply_grid_properties)
        props_dialog.exec_()

    def apply_grid_properties(self, properties):
        self.current_properties.update(properties)
        
        # Enhanced column width handling
        default_width = self.current_properties['cell_width']
        visible_width = self.grid_table.viewport().width()
        column_width = min(default_width, max(40, visible_width // min(self.cols, 20)))
        
        # Apply optimized cell sizes
        for col in range(self.cols):
            self.grid_table.setColumnWidth(col, column_width)
        
        row_height = self.current_properties['cell_height']
        for row in range(self.rows):
            self.grid_table.setRowHeight(row, row_height)
        
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
            QHeaderView::section {{
                background-color: #f0f0f0;
                padding: 2px;
                border: 1px solid #d0d0d0;
            }}
        """
        self.grid_table.setStyleSheet(style)
        
        if self.current_properties['auto_fit']:
            self.optimize_grid_display()
        
        self.update_cell_colors()

    def update_cell_colors(self):
        """Update all cell colors efficiently"""
        bg_color = QColor(self.current_properties['bg_color'])
        text_color = QColor(self.current_properties['text_color'])
        
        for row in range(self.rows):
            for col in range(self.cols):
                if item := self.grid_table.item(row, col):
                    item.setBackground(bg_color)
                    item.setForeground(text_color)
                    
    def open_numerical_grid(self):
        from .numerical_grid_panel import NumericalGridPanel
        numerical_grid = NumericalGridPanel(self, self.option_name)
        numerical_grid.show()
