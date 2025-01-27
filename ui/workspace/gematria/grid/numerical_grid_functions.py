from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QGroupBox,
                            QComboBox, QSpinBox, QColorDialog, QDialog, QListWidget)
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class NumericalGridFunctions(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_panel = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Analysis Tools Group
        analysis_group = QGroupBox("Analysis Tools")
        analysis_layout = QVBoxLayout()
        
        # Row/Column Analysis
        self.row_sum_btn = QPushButton("Calculate Row Sums")
        self.col_sum_btn = QPushButton("Calculate Column Sums")
        self.diag_product_btn = QPushButton("Calculate Diagonal Products")
        
        # Region Analysis
        region_layout = QHBoxLayout()
        self.region_size = QSpinBox()
        self.region_size.setRange(2, min(self.grid_panel.rows, self.grid_panel.cols))
        region_layout.addWidget(QLabel("Region Size:"))
        region_layout.addWidget(self.region_size)
        self.region_avg_btn = QPushButton("Calculate Region Averages")
        
        # Statistical Analysis
        self.stats_btn = QPushButton("Show Statistical Analysis")
        self.distribution_btn = QPushButton("Show Distribution Pattern")
        
        analysis_layout.addWidget(self.row_sum_btn)
        analysis_layout.addWidget(self.col_sum_btn)
        analysis_layout.addWidget(self.diag_product_btn)
        analysis_layout.addLayout(region_layout)
        analysis_layout.addWidget(self.region_avg_btn)
        analysis_layout.addWidget(self.stats_btn)
        analysis_layout.addWidget(self.distribution_btn)
        analysis_group.setLayout(analysis_layout)
        
        # Visualization Options Group
        visual_group = QGroupBox("Visualization Options")
        visual_layout = QVBoxLayout()
        
        # Heat Map Controls
        heat_layout = QHBoxLayout()
        self.heat_map_btn = QPushButton("Generate Heat Map")
        self.heat_range = QComboBox()
        self.heat_range.addItems(["Full Range", "Custom Range", "Percentile"])
        heat_layout.addWidget(self.heat_map_btn)
        heat_layout.addWidget(self.heat_range)
        
        # Sequence Highlighting
        self.sequence_type = QComboBox()
        self.sequence_type.addItems([
            "Arithmetic",
            "Geometric",
            "Fibonacci-like",
            "Custom Pattern"
        ])
        self.highlight_sequence_btn = QPushButton("Highlight Sequence")
        
        # Pattern Color Coding
        self.pattern_type = QComboBox()
        self.pattern_type.addItems([
            "Value Ranges",
            "Multiples",
            "Relationships",
            "Custom"
        ])
        self.color_code_btn = QPushButton("Apply Color Coding")
        
        # Frequency Display
        self.freq_display_btn = QPushButton("Show Value Frequencies")
        
        # Relationship Mapping
        self.relation_type = QComboBox()
        self.relation_type.addItems([
            "Adjacent Values",
            "Diagonal Relations",
            "Custom Distance"
        ])
        self.map_relations_btn = QPushButton("Map Relationships")
        
        visual_layout.addLayout(heat_layout)
        visual_layout.addWidget(self.sequence_type)
        visual_layout.addWidget(self.highlight_sequence_btn)
        visual_layout.addWidget(self.pattern_type)
        visual_layout.addWidget(self.color_code_btn)
        visual_layout.addWidget(self.freq_display_btn)
        visual_layout.addWidget(self.relation_type)
        visual_layout.addWidget(self.map_relations_btn)
        visual_group.setLayout(visual_layout)
        
        # Add groups to main layout
        layout.addWidget(analysis_group)
        layout.addWidget(visual_group)
        self.setLayout(layout)
        
        self.connect_signals()
        
    def connect_signals(self):
        # Analysis connections
        self.row_sum_btn.clicked.connect(self.calculate_row_sums)
        self.col_sum_btn.clicked.connect(self.calculate_column_sums)
        self.diag_product_btn.clicked.connect(self.calculate_diagonal_products)
        self.region_avg_btn.clicked.connect(self.calculate_region_averages)
        self.stats_btn.clicked.connect(self.show_statistics)
        self.distribution_btn.clicked.connect(self.show_distribution)
        
        # Visualization connections
        self.heat_map_btn.clicked.connect(self.generate_heat_map)
        self.highlight_sequence_btn.clicked.connect(self.highlight_sequence)
        self.color_code_btn.clicked.connect(self.apply_color_coding)
        self.freq_display_btn.clicked.connect(self.show_frequency_display)
        self.map_relations_btn.clicked.connect(self.map_relationships)
        
    def get_grid_values(self):
        """Convert grid to numpy array for analysis"""
        values = []
        for row in range(self.grid_panel.rows):
            row_values = []
            for col in range(self.grid_panel.cols):
                item = self.grid_panel.grid_table.item(row, col)
                row_values.append(int(item.text()) if item else 0)
            values.append(row_values)
        return np.array(values)
        
    def calculate_row_sums(self):
        values = self.get_grid_values()
        row_sums = values.sum(axis=1)
        self.display_results("Row Sums", row_sums)
        
    def calculate_column_sums(self):
        values = self.get_grid_values()
        col_sums = values.sum(axis=0)
        self.display_results("Column Sums", col_sums)
        
    def calculate_diagonal_products(self):
        values = self.get_grid_values()
        main_diag = np.prod(np.diag(values))
        anti_diag = np.prod(np.diag(np.fliplr(values)))
        self.display_results("Diagonal Products", [main_diag, anti_diag])
        
    def calculate_region_averages(self):
        values = self.get_grid_values()
        size = self.region_size.value()
        averages = []
        for i in range(0, values.shape[0] - size + 1):
            for j in range(0, values.shape[1] - size + 1):
                region = values[i:i+size, j:j+size]
                averages.append((i, j, np.mean(region)))
        self.display_region_results("Region Averages", averages)
        
    def show_statistics(self):
        values = self.get_grid_values()
        stats = {
            'Mean': np.mean(values),
            'Median': np.median(values),
            'Std Dev': np.std(values),
            'Min': np.min(values),
            'Max': np.max(values)
        }
        self.display_statistics(stats)
        
    def show_distribution(self):
        values = self.get_grid_values().flatten()
        fig = Figure(figsize=(6, 4))
        canvas = FigureCanvasQTAgg(fig)
        ax = fig.add_subplot(111)
        ax.hist(values, bins='auto')
        ax.set_title('Value Distribution')
        self.show_plot(canvas)
        
    def generate_heat_map(self):
        values = self.get_grid_values()
        range_type = self.heat_range.currentText()
        
        if range_type == "Custom Range":
            # Implement custom range dialog
            pass
        elif range_type == "Percentile":
            values = (values - np.min(values)) / (np.max(values) - np.min(values))
            
        self.apply_heat_map(values)
        
    def highlight_sequence(self):
        sequence_type = self.sequence_type.currentText()
        values = self.get_grid_values()
        
        if sequence_type == "Arithmetic":
            self.find_arithmetic_sequences(values)
        elif sequence_type == "Geometric":
            self.find_geometric_sequences(values)
        elif sequence_type == "Fibonacci-like":
            self.find_fibonacci_sequences(values)
            
    def apply_color_coding(self):
        pattern_type = self.pattern_type.currentText()
        values = self.get_grid_values()
        
        if pattern_type == "Value Ranges":
            self.color_code_ranges(values)
        elif pattern_type == "Multiples":
            self.color_code_multiples(values)
        elif pattern_type == "Relationships":
            self.color_code_relationships(values)
            
    def show_frequency_display(self):
        values = self.get_grid_values()
        unique, counts = np.unique(values, return_counts=True)
        fig = Figure(figsize=(6, 4))
        canvas = FigureCanvasQTAgg(fig)
        ax = fig.add_subplot(111)
        ax.bar(unique, counts)
        ax.set_title('Value Frequencies')
        self.show_plot(canvas)
        
    def map_relationships(self):
        relation_type = self.relation_type.currentText()
        values = self.get_grid_values()
        
        if relation_type == "Adjacent Values":
            self.map_adjacent_relations(values)
        elif relation_type == "Diagonal Relations":
            self.map_diagonal_relations(values)
            
    # Helper methods for visualization
    def apply_heat_map(self, values):
        cmap = plt.cm.RdYlBu
        normalized = (values - values.min()) / (values.max() - values.min())
        
        for i in range(self.grid_panel.rows):
            for j in range(self.grid_panel.cols):
                color = cmap(normalized[i, j])
                item = self.grid_panel.grid_table.item(i, j)
                if item:
                    item.setBackground(QBrush(QColor.fromRgbF(*color)))
                    
    def find_arithmetic_sequences(self, values):
        # Implementation for finding arithmetic sequences
        pass
        
    def find_geometric_sequences(self, values):
        # Implementation for finding geometric sequences
        pass
        
    def find_fibonacci_sequences(self, values):
        # Implementation for finding Fibonacci-like sequences
        pass
        
    def color_code_ranges(self, values):
        # Implementation for color coding value ranges
        pass
        
    def color_code_multiples(self, values):
        # Implementation for color coding multiples
        pass
        
    def color_code_relationships(self, values):
        # Implementation for color coding relationships
        pass
        
    def map_adjacent_relations(self, values):
        # Implementation for mapping adjacent value relationships
        pass
        
    def map_diagonal_relations(self, values):
        # Implementation for mapping diagonal relationships
        pass
        
    def display_results(self, title, results):
        """Display analysis results with color coding"""
        # Create results window
        results_dialog = QDialog(self)
        results_dialog.setWindowTitle(title)
        layout = QVBoxLayout()
        
        # Create results list
        results_list = QListWidget()
        
        if title == "Row Sums":
            for i, sum_val in enumerate(results):
                results_list.addItem(f"Row {i+1}: {sum_val}")
                self.highlight_row(i, sum_val)
        
        elif title == "Column Sums":
            for i, sum_val in enumerate(results):
                results_list.addItem(f"Column {i+1}: {sum_val}")
                self.highlight_column(i, sum_val)
        
        elif title == "Diagonal Products":
            results_list.addItem(f"Main Diagonal Product: {results[0]}")
            results_list.addItem(f"Anti-Diagonal Product: {results[1]}")
            self.highlight_diagonals(results[0], results[1])
        
        layout.addWidget(results_list)
        results_dialog.setLayout(layout)
        results_dialog.exec_()

    def highlight_row(self, row, value):
        """Highlight row with color intensity based on value"""
        color = self.get_highlight_color(value)
        for col in range(self.grid_panel.cols):
            item = self.grid_panel.grid_table.item(row, col)
            if item:
                item.setBackground(QBrush(color))

    def highlight_column(self, col, value):
        """Highlight column with color intensity based on value"""
        color = self.get_highlight_color(value)
        for row in range(self.grid_panel.rows):
            item = self.grid_panel.grid_table.item(row, col)
            if item:
                item.setBackground(QBrush(color))

    def highlight_diagonals(self, main_prod, anti_prod):
        """Highlight diagonals with different colors based on products"""
        main_color = self.get_highlight_color(main_prod)
        anti_color = self.get_highlight_color(anti_prod)
        
        # Highlight main diagonal
        for i in range(min(self.grid_panel.rows, self.grid_panel.cols)):
            item = self.grid_panel.grid_table.item(i, i)
            if item:
                item.setBackground(QBrush(main_color))
        
        # Highlight anti-diagonal
        for i in range(min(self.grid_panel.rows, self.grid_panel.cols)):
            item = self.grid_panel.grid_table.item(i, self.grid_panel.cols-i-1)
            if item:
                item.setBackground(QBrush(anti_color))

    def get_highlight_color(self, value):
        """Generate color based on value magnitude"""
        # Convert numpy.float64 to integer for HSV color
        hue = int(max(0, min(120 - (float(value) % 120), 120)))
        return QColor.fromHsv(hue, 200, 250)


    def display_region_results(self, title, results):
        """Display region analysis results"""
        results_dialog = QDialog(self)
        results_dialog.setWindowTitle(title)
        layout = QVBoxLayout()
        
        results_list = QListWidget()
        for row, col, avg in results:
            results_list.addItem(f"Region at ({row+1},{col+1}): {avg:.2f}")
            self.highlight_region(row, col, self.region_size.value(), avg)
        
        layout.addWidget(results_list)
        results_dialog.setLayout(layout)
        results_dialog.exec_()

    def highlight_region(self, start_row, start_col, size, value):
        """Highlight a region with color based on its average value"""
        color = self.get_highlight_color(value)
        for i in range(start_row, start_row + size):
            for j in range(start_col, start_col + size):
                item = self.grid_panel.grid_table.item(i, j)
                if item:
                    item.setBackground(QBrush(color))

    def display_statistics(self, stats):
        """Display statistical analysis results"""
        stats_dialog = QDialog(self)
        stats_dialog.setWindowTitle("Statistical Analysis")
        layout = QVBoxLayout()
        
        results_list = QListWidget()
        for stat, value in stats.items():
            results_list.addItem(f"{stat}: {value:.2f}")
        
        layout.addWidget(results_list)
        stats_dialog.setLayout(layout)
        stats_dialog.exec_()

    def show_plot(self, canvas):
        """Display matplotlib plot in a dialog"""
        plot_dialog = QDialog(self)
        plot_dialog.setWindowTitle("Analysis Plot")
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        plot_dialog.setLayout(layout)
        plot_dialog.exec_()

