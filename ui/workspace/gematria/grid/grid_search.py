from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLineEdit, QPushButton, QListWidget,
                            QComboBox, QLabel, QGroupBox, QSpinBox,
                            QAbstractItemView)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QBrush
from .els_search import ELSSearch, SearchDirection

class GridSearch(QWidget):
    # Change Signal to pyqtSignal
    searchResultsFound = pyqtSignal(list)  

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_panel = parent
        self.search_results = []
        self.setup_search_ui()
    def setup_search_ui(self):
        layout = QVBoxLayout()
        
        # Search controls
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search term...")
        self.search_type = QComboBox()
        self.search_type.addItems(["Character", "Pattern", "Position", "RegEx"])
        self.search_button = QPushButton("Search")
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_type)
        search_layout.addWidget(self.search_button)
        
        # Results navigation
        nav_layout = QHBoxLayout()
        self.results_dropdown = QComboBox()
        self.results_dropdown.setMinimumWidth(200)
        nav_layout.addWidget(QLabel("Jump to:"))
        nav_layout.addWidget(self.results_dropdown)
        
        # Results display
        self.results_list = QListWidget()
        self.results_counter = QLabel("Results: 0")
        
        # Add numerical grid button
        self.numerical_button = QPushButton("Show Numerical Grid")
        self.numerical_button.clicked.connect(self.parent().open_numerical_grid)        

        # Style the results list
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #ccc;
                font-family: monospace;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e6f3ff;
                color: black;
            }
        """)
        
        # Style the results dropdown
        self.results_dropdown.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 5px;
            }
        """)

        
        # Add all components to main layout
        layout.addLayout(search_layout)
        layout.addLayout(nav_layout)
        layout.addWidget(self.results_counter)
        layout.addWidget(self.results_list)
        layout.addWidget(self.setup_els_search())
        layout.addWidget(self.numerical_button)
        
        self.setLayout(layout)
        self.connect_signals()
        
    def connect_signals(self):
        self.search_button.clicked.connect(self.perform_search)
        self.search_input.returnPressed.connect(self.perform_search)
        self.search_type.currentTextChanged.connect(self.update_search_mode)
        self.results_dropdown.currentIndexChanged.connect(self.navigate_to_result)
        self.results_list.itemDoubleClicked.connect(self.center_on_result) 
        
    def perform_search(self):
        search_text = self.search_input.text()
        search_type = self.search_type.currentText()
        
        self.search_results.clear()
        self.results_list.clear()
        self.results_dropdown.clear()
        
        if search_text:
            if search_type == "Character":
                self.search_characters(search_text)
            elif search_type == "Pattern":
                self.search_pattern(search_text)
            elif search_type == "Position":
                self.search_position(search_text)
            elif search_type == "RegEx":
                self.search_regex(search_text)
                
        self.results_counter.setText(f"Results: {len(self.search_results)}")
        self.searchResultsFound.emit(self.search_results)
        
    def update_search_mode(self, mode):
        placeholders = {
            "Character": "Enter character to search...",
            "Pattern": "Enter pattern sequence...",
            "Position": "Enter row,col or position number...",
            "RegEx": "Enter regular expression..."
        }
        self.search_input.setPlaceholderText(placeholders.get(mode, "Enter search term..."))
        
    def search_characters(self, search_text):
        grid = self.grid_panel.grid_table
        for row in range(grid.rowCount()):
            for col in range(grid.columnCount()):
                item = grid.item(row, col)
                if item and item.text() == search_text:
                    self.search_results.append((row, col))
                    self.add_result_to_list(row, col, item.text())

    def search_pattern(self, pattern):
        grid = self.grid_panel.grid_table
        text = ""
        positions = []
        
        for row in range(grid.rowCount()):
            for col in range(grid.columnCount()):
                item = grid.item(row, col)
                if item:
                    text += item.text()
                    positions.append((row, col))
        
        start = 0
        while True:
            index = text.find(pattern, start)
            if index == -1:
                break
            self.search_results.extend(positions[index:index + len(pattern)])
            self.add_result_to_list(*positions[index], pattern)
            start = index + 1

    def search_position(self, position):
        try:
            if ',' in position:
                row, col = map(int, position.split(','))
                if self.is_valid_position(row-1, col-1):
                    self.search_results.append((row-1, col-1))
                    item = self.grid_panel.grid_table.item(row-1, col-1)
                    if item:
                        self.add_result_to_list(row-1, col-1, item.text())
            else:
                pos = int(position)
                row = (pos-1) // self.grid_panel.cols
                col = (pos-1) % self.grid_panel.cols
                if self.is_valid_position(row, col):
                    self.search_results.append((row, col))
                    item = self.grid_panel.grid_table.item(row, col)
                    if item:
                        self.add_result_to_list(row, col, item.text())
        except ValueError:
            pass

    def search_regex(self, pattern):
        import re
        grid = self.grid_panel.grid_table
        for row in range(grid.rowCount()):
            for col in range(grid.columnCount()):
                item = grid.item(row, col)
                if item and re.match(pattern, item.text()):
                    self.search_results.append((row, col))
                    self.add_result_to_list(row, col, item.text())

    def setup_els_search(self):
        """Setup ELS search controls in search widget"""
        els_group = QGroupBox("ELS Search")
        els_layout = QVBoxLayout()
        
        # Search term input
        self.els_input = QLineEdit()
        self.els_input.setPlaceholderText("Enter search term...")
        
        # Step size input
        step_layout = QHBoxLayout()
        self.step_size = QSpinBox()
        self.step_size.setRange(1, 1000)
        step_layout.addWidget(QLabel("Step Size:"))
        step_layout.addWidget(self.step_size)
        
        # Direction selector
        self.direction = QComboBox()
        self.direction.addItems(["Forward", "Backward", "Bidirectional"])
        
        # Search button
        self.els_search_btn = QPushButton("Search ELS")
        self.els_search_btn.clicked.connect(self.perform_els_search)
        
        
        els_layout.addWidget(self.els_input)
      
        els_layout.addLayout(step_layout)
        els_layout.addWidget(self.direction)
        els_layout.addWidget(self.els_search_btn)
        els_group.setLayout(els_layout)
        
        return els_group

    def perform_els_search(self):
        """Execute ELS search with current parameters"""
        search_term = self.els_input.text()
        step_size = self.step_size.value()
        direction = SearchDirection(self.direction.currentText().lower())
        
        # Clear previous results
        self.results_list.clear()
        self.results_dropdown.clear()
        self.search_results.clear()
        
        # Initialize ELS search
        els_searcher = ELSSearch(self.grid_panel)
        results = els_searcher.search_els(search_term, step_size, direction)
        
        # Process and display detailed results
        sequence_count = 1
        for step, positions in results:
            # Create individual entry for each sequence found
            sequence_info = []
            start_pos = positions[0]
            start_row = start_pos // self.grid_panel.cols + 1
            start_col = start_pos % self.grid_panel.cols + 1
            
            for pos in positions:
                row = pos // self.grid_panel.cols
                col = pos % self.grid_panel.cols
                self.search_results.append((row, col))
                sequence_info.append(f"({row+1},{col+1})")
            
            # Add detailed formatted result
            result_text = (f"=== Sequence #{sequence_count} ===\n"
                         f"Term: '{search_term}'\n"
                         f"Starting Position: ({start_row},{start_col})\n"
                         f"Step Size: {step}\n"
                         f"Direction: {direction.value}\n"
                         f"Complete Path: {' → '.join(sequence_info)}\n"
                         f"{'=' * 20}")
            
            self.results_list.addItem(result_text)
            self.results_dropdown.addItem(
                f"Sequence #{sequence_count} - Start: ({start_row},{start_col})", 
                positions
            )
            sequence_count += 1
                
        self.results_counter.setText(f"Sequences Found: {len(results)}")
        self.searchResultsFound.emit(self.search_results)



    def add_result_to_list(self, row, col, value):
        result_text = f"Row {row+1}, Col {col+1}: {value}"
        self.results_list.addItem(result_text)
        self.results_dropdown.addItem(result_text, (row, col))

    def navigate_to_result(self, index):
        """Enhanced navigation with path highlighting for ELS results"""
        if index >= 0:
            positions = self.results_dropdown.itemData(index)
            
            # Clear previous highlights
            self.grid_panel.clear_highlights()
            
            from PyQt5.QtGui import QColor, QBrush
            sequence_color = QColor(255, 255, 0, 100)  # Yellow for letters
            path_color = QColor(173, 216, 230, 100)    # Light blue for path
            
            # Highlight sequence and path
            for i in range(len(positions)-1):
                current_pos = positions[i]
                next_pos = positions[i+1]
                
                # Highlight current letter
                row = current_pos // self.grid_panel.cols
                col = current_pos % self.grid_panel.cols
                item = self.grid_panel.grid_table.item(row, col)
                if item:
                    item.setBackground(QBrush(sequence_color))
                    item.setToolTip(f"Sequence Position: {i+1}")
                
                # Highlight path cells between letters
                start_row = current_pos // self.grid_panel.cols
                start_col = current_pos % self.grid_panel.cols
                end_row = next_pos // self.grid_panel.cols
                end_col = next_pos % self.grid_panel.cols
                
                # Highlight cells in path
                self.highlight_path(start_row, start_col, end_row, end_col, path_color)
            
            # Highlight last letter
            last_pos = positions[-1]
            row = last_pos // self.grid_panel.cols
            col = last_pos % self.grid_panel.cols
            item = self.grid_panel.grid_table.item(row, col)
            if item:
                item.setBackground(QBrush(sequence_color))
                item.setToolTip(f"Sequence Position: {len(positions)}")
            
            # Focus on first letter
            first_row = positions[0] // self.grid_panel.cols
            first_col = positions[0] % self.grid_panel.cols
            self.grid_panel.grid_table.setCurrentCell(first_row, first_col)
            self.grid_panel.grid_table.scrollToItem(
                self.grid_panel.grid_table.item(first_row, first_col)
            )

    def highlight_path(self, start_row, start_col, end_row, end_col, color):
        """Highlight cells in the path between two sequence letters.
        
        Args:
            start_row (int): Starting position row
            start_col (int): Starting position column
            end_row (int): Ending position row
            end_col (int): Ending position column
            color (QColor): Color to use for path highlighting
        """
        from PyQt5.QtGui import QBrush
        
        # Calculate step sizes
        row_step = 1 if end_row >= start_row else -1
        col_step = 1 if end_col >= start_col else -1
        
        # Highlight row path
        for row in range(start_row, end_row + row_step, row_step):
            item = self.grid_panel.grid_table.item(row, start_col)
            if item:
                current_color = item.background().color()
                if current_color != color:  # Only highlight if not already highlighted
                    item.setBackground(QBrush(color))
                    item.setToolTip("Path")
        
        # Highlight column path
        for col in range(start_col, end_col + col_step, col_step):
            item = self.grid_panel.grid_table.item(end_row, col)
            if item:
                current_color = item.background().color()
                if current_color != color:
                    item.setBackground(QBrush(color))
                    item.setToolTip("Path")


    def is_valid_position(self, row, col):
        return (0 <= row < self.grid_panel.rows and 
                0 <= col < self.grid_panel.cols)

    def center_on_result(self, item):
        """Centers the grid view on the double-clicked result"""
        index = self.results_list.row(item)
        positions = self.results_dropdown.itemData(index)
        if positions:
            # Get the center position of the sequence
            if isinstance(positions, tuple):
                row, col = positions
            else:
                # For ELS results, center on first position in sequence
                first_pos = positions[0]
                row = first_pos // self.grid_panel.cols
                col = first_pos % self.grid_panel.cols
            
            # Center and highlight the result
            self.grid_panel.grid_table.setCurrentCell(row, col)
            self.grid_panel.grid_table.scrollToItem(
                self.grid_panel.grid_table.item(row, col),
                QAbstractItemView.PositionAtCenter
            )