from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLineEdit, QPushButton, QListWidget,
                            QComboBox, QLabel, QGroupBox, QSpinBox,
                            QAbstractItemView)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor, QBrush, QFont, QLinearGradient
import math

class NumericalGridSearch(QWidget):
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
        self.search_input.setPlaceholderText("Enter search value...")
        
        self.search_type = QComboBox()
        self.search_type.addItems([
            "Exact Value",
            "Value Range",
            "Greater/Less Than",
            "Multiples",
            "Prime Numbers",
            "Perfect Numbers",
            "Numerical Clusters",
        ])
        
        self.comparison_type = QComboBox()
        self.comparison_type.addItems([">", "<", ">=", "<="])
        self.comparison_type.hide()  # Only show for Greater/Less Than
        
        self.range_end = QLineEdit()
        self.range_end.setPlaceholderText("End value...")
        self.range_end.hide()  # Only show for Range search
        
        self.perfect_type = QComboBox()
        self.perfect_type.addItems(["Squares", "Cubes"])
        self.perfect_type.hide()  # Only show for Perfect Numbers
        
        # Add cluster size control
        self.cluster_size = QSpinBox()
        self.cluster_size.setRange(2, 13) # Reasonable range for cluster sizes
        self.cluster_size.hide()  # Only show for cluster search
            
        self.search_button = QPushButton("Search")
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.comparison_type)
        search_layout.addWidget(self.range_end)
        search_layout.addWidget(self.perfect_type)
        search_layout.addWidget(self.search_type)
        search_layout.addWidget(self.search_button)
        
        # Results display
        self.results_list = QListWidget()
        self.results_counter = QLabel("Results: 0")
        
        # Add components to layout
        layout.addLayout(search_layout)
        layout.addWidget(self.results_counter)
        layout.addWidget(self.results_list)
        
        self.setLayout(layout)
        self.connect_signals()
        self.style_widgets()

    def style_widgets(self):
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

    def connect_signals(self):
        self.search_button.clicked.connect(self.perform_search)
        self.search_input.returnPressed.connect(self.perform_search)
        self.search_type.currentTextChanged.connect(self.update_search_mode)
        self.results_list.itemDoubleClicked.connect(self.center_on_result)

    def update_search_mode(self, mode):
        # Show/hide relevant widgets based on search type
        self.comparison_type.hide()
        self.range_end.hide()
        self.perfect_type.hide()
        self.search_input.show()
        
        if mode == "Greater/Less Than":
            self.comparison_type.show()
        elif mode == "Value Range":
            self.range_end.show()
        elif mode == "Perfect Numbers":
            self.perfect_type.show()
        elif mode == "Prime Numbers":
            self.search_input.hide()

        if mode == "Numerical Clusters":
            self.search_input.setPlaceholderText("Enter target sum...")
            self.cluster_size.show()
        else:
            self.cluster_size.hide()
            
    def perform_search(self):
        self.search_results.clear()
        self.results_list.clear()
        
        search_type = self.search_type.currentText()
        
        if search_type == "Exact Value":
            self.search_exact_value()
        elif search_type == "Value Range":
            self.search_value_range()
        elif search_type == "Greater/Less Than":
            self.search_greater_less()
        elif search_type == "Multiples":
            self.search_multiples()
        elif search_type == "Prime Numbers":
            self.search_primes()
        elif search_type == "Perfect Numbers":
            self.search_perfect_numbers()
        elif search_type == "Numerical Clusters":
            self.search_clusters()
            
        self.results_counter.setText(f"Results: {len(self.search_results)}")
        self.searchResultsFound.emit(self.search_results)

    def search_exact_value(self):
        try:
            target = int(self.search_input.text())
            for row in range(self.grid_panel.rows):
                for col in range(self.grid_panel.cols):
                    item = self.grid_panel.grid_table.item(row, col)
                    if item and int(item.text()) == target:
                        self.search_results.append((row, col))
                        self.add_result_to_list(row, col, item.text(), "Exact Match")
        except ValueError:
            pass

    def search_value_range(self):
        try:
            start = int(self.search_input.text())
            end = int(self.range_end.text())
            for row in range(self.grid_panel.rows):
                for col in range(self.grid_panel.cols):
                    item = self.grid_panel.grid_table.item(row, col)
                    if item:
                        value = int(item.text())
                        if start <= value <= end:
                            self.search_results.append((row, col))
                            self.add_result_to_list(row, col, item.text(), f"In range [{start}-{end}]")
        except ValueError:
            pass

    def search_greater_less(self):
        try:
            target = int(self.search_input.text())
            comp = self.comparison_type.currentText()
            for row in range(self.grid_panel.rows):
                for col in range(self.grid_panel.cols):
                    item = self.grid_panel.grid_table.item(row, col)
                    if item:
                        value = int(item.text())
                        if self.compare_values(value, target, comp):
                            self.search_results.append((row, col))
                            self.add_result_to_list(row, col, item.text(), f"{comp} {target}")
        except ValueError:
            pass

    def search_multiples(self):
        try:
            base = int(self.search_input.text())
            for row in range(self.grid_panel.rows):
                for col in range(self.grid_panel.cols):
                    item = self.grid_panel.grid_table.item(row, col)
                    if item:
                        value = int(item.text())
                        if value % base == 0:
                            self.search_results.append((row, col))
                            self.add_result_to_list(row, col, item.text(), f"Multiple of {base}")
        except ValueError:
            pass

    def search_primes(self):
        for row in range(self.grid_panel.rows):
            for col in range(self.grid_panel.cols):
                item = self.grid_panel.grid_table.item(row, col)
                if item:
                    value = int(item.text())
                    if self.is_prime(value):
                        self.search_results.append((row, col))
                        self.add_result_to_list(row, col, item.text(), "Prime")

    def search_perfect_numbers(self):
        perfect_type = self.perfect_type.currentText()
        for row in range(self.grid_panel.rows):
            for col in range(self.grid_panel.cols):
                item = self.grid_panel.grid_table.item(row, col)
                if item:
                    value = int(item.text())
                    if perfect_type == "Squares":
                        root = math.isqrt(value)
                        if root * root == value:
                            self.search_results.append((row, col))
                            self.add_result_to_list(row, col, item.text(), f"Perfect Square")
                    else:  # Cubes
                        cube_root = round(value ** (1/3))
                        if cube_root ** 3 == value:
                            self.search_results.append((row, col))
                            self.add_result_to_list(row, col, item.text(), f"Perfect Cube")

    def compare_values(self, value, target, comparison):
        if comparison == ">":
            return value > target
        elif comparison == "<":
            return value < target
        elif comparison == ">=":
            return value >= target
        elif comparison == "<=":
            return value <= target

    def is_prime(self, n):
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True

    def add_result_to_list(self, row, col, value, pattern_type):
        result_text = f"Row {row+1}, Col {col+1}: {value} ({pattern_type})"
        self.results_list.addItem(result_text)

    def center_on_result(self, item):
        index = self.results_list.row(item)
        if index >= 0 and index < len(self.search_results):
            row, col = self.search_results[index]
            self.grid_panel.grid_table.setCurrentCell(row, col)
            self.grid_panel.grid_table.scrollToItem(
                self.grid_panel.grid_table.item(row, col),
                QAbstractItemView.PositionAtCenter
            )
            
    def search_clusters(self):
        try:
            target_sum = int(self.search_input.text())
            max_size = self.cluster_size.value()
            clusters = self.find_all_clusters(target_sum, max_size)
            
            for cluster_id, cluster in enumerate(clusters, 1):
                self.highlight_cluster(cluster, cluster_id)
                self.add_cluster_to_results(cluster, cluster_id)
                
            self.results_counter.setText(f"Clusters Found: {len(clusters)}")
        except ValueError:
            pass

    def get_grid_values(self):
        """Convert grid to numerical values for analysis"""
        values = []
        for row in range(self.grid_panel.rows):
            row_values = []
            for col in range(self.grid_panel.cols):
                item = self.grid_panel.grid_table.item(row, col)
                if item:
                    try:
                        row_values.append(int(item.text()))
                    except ValueError:
                        row_values.append(0)  # Handle non-numeric values
                else:
                    row_values.append(0)  # Handle empty cells
            values.append(row_values)
        return values

    def find_all_clusters(self, target_sum, max_size):
        clusters = []
        grid_values = self.get_grid_values()
        
        # Search in all directions
        for row in range(self.grid_panel.rows):
            for col in range(self.grid_panel.cols):
                # Horizontal clusters
                self.check_direction(row, col, 0, 1, target_sum, max_size, [], clusters, grid_values)
                # Vertical clusters
                self.check_direction(row, col, 1, 0, target_sum, max_size, [], clusters, grid_values)
                # Diagonal clusters
                self.check_direction(row, col, 1, 1, target_sum, max_size, [], clusters, grid_values)
        
        return clusters

    def check_direction(self, row, col, row_delta, col_delta, target, max_size, current, clusters, values):
        if len(current) > max_size:
            return
            
        if not self.is_valid_position(row, col):
            return
            
        current_sum = sum(values[r][c] for r, c in current)
        current.append((row, col))
        
        if current_sum + values[row][col] == target:
            clusters.append(current.copy())
        elif current_sum + values[row][col] < target:
            self.check_direction(row + row_delta, col + col_delta, 
                            row_delta, col_delta, target, max_size, 
                            current.copy(), clusters, values)
        
        current.pop()

    def is_valid_position(self, row, col):
        """Check if given row and column are within grid boundaries"""
        return (0 <= row < self.grid_panel.rows and 
                0 <= col < self.grid_panel.cols)

    def highlight_cluster(self, cluster, cluster_id):
        base_color = QColor.fromHsv((cluster_id * 50) % 360, 200, 250)
        
        for row, col in cluster:
            item = self.grid_panel.grid_table.item(row, col)
            current_clusters = item.data(Qt.UserRole) or set()
            
            if isinstance(current_clusters, set):
                current_clusters.add(cluster_id)
            else:
                current_clusters = {cluster_id}
                
            item.setData(Qt.UserRole, current_clusters)
            
            if len(current_clusters) > 1:
                # Create diagonal gradient for overlapping clusters
                gradient = QLinearGradient(0, 0, 1, 1)
                for i, cid in enumerate(current_clusters):
                    color = QColor.fromHsv((cid * 50) % 360, 200, 250)
                    gradient.setColorAt(i / (len(current_clusters) - 1), color)
                brush = QBrush(gradient)
            else:
                brush = QBrush(base_color)
                
            item.setBackground(brush)
            
            # Add bold border
            item.setForeground(QBrush(Qt.black))
            item.setFont(QFont("Arial", 10, QFont.Bold))

    def add_cluster_to_results(self, cluster, cluster_id):
        values = self.get_grid_values()
        cluster_sum = sum(values[row][col] for row, col in cluster)
        cells = [f"({row+1},{col+1})" for row, col in cluster]
        
        result_text = f"Cluster {cluster_id}\n"
        result_text += f"Sum: {cluster_sum}\n"
        result_text += f"Cells: {', '.join(cells)}"
        
        self.results_list.addItem(result_text)
