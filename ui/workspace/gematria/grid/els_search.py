from typing import List, Tuple, Dict
from enum import Enum
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSpinBox, QComboBox, QCheckBox, QSlider,
                            QListWidget, QTableWidget, QGroupBox, QProgressBar, QTableWidgetItem, QLineEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen
import numpy as np
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class SearchDirection(Enum):
    FORWARD = "forward"
    BACKWARD = "backward"
    BIDIRECTIONAL = "bidirectional"

class ELSSearch(QWidget):
    searchComplete = pyqtSignal(list)
    sequenceFound = pyqtSignal(list)
    
    def __init__(self, grid_panel):
        super().__init__()
        self.grid_panel = grid_panel
        self.text = self._get_grid_text()
        self.sequences = []
        self.animation_timer = QTimer()
        self.current_animation_step = 0
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Search Controls
        search_group = QGroupBox("Search Parameters")
        search_layout = QVBoxLayout()
        
        # Basic controls
        basic_layout = QHBoxLayout()
        self.term_input = QLineEdit()
        self.term_input.setPlaceholderText("Enter search term...")
        self.step_size = QSpinBox()
        self.step_size.setRange(1, 1000)
        self.direction = QComboBox()
        self.direction.addItems(["Forward", "Backward", "Bidirectional"])
        
        basic_layout.addWidget(QLabel("Term:"))
        basic_layout.addWidget(self.term_input)
        basic_layout.addWidget(QLabel("Step:"))
        basic_layout.addWidget(self.step_size)
        basic_layout.addWidget(QLabel("Direction:"))
        basic_layout.addWidget(self.direction)
        
        # Advanced controls
        advanced_layout = QHBoxLayout()
        self.min_step = QSpinBox()
        self.max_step = QSpinBox()
        self.min_step.setRange(1, 500)
        self.max_step.setRange(1, 1000)
        self.max_step.setValue(50)
        
        self.auto_step = QCheckBox("Auto Step Range")
        self.find_intersections = QCheckBox("Find Intersections")
        self.reverse_match = QCheckBox("Include Reverse")
        
        advanced_layout.addWidget(QLabel("Min Step:"))
        advanced_layout.addWidget(self.min_step)
        advanced_layout.addWidget(QLabel("Max Step:"))
        advanced_layout.addWidget(self.max_step)
        advanced_layout.addWidget(self.auto_step)
        advanced_layout.addWidget(self.find_intersections)
        advanced_layout.addWidget(self.reverse_match)
        
        # Visualization Controls
        visual_group = QGroupBox("Visualization")
        visual_layout = QHBoxLayout()
        
        self.animation_speed = QSlider(Qt.Horizontal)
        self.animation_speed.setRange(100, 2000)
        self.animation_speed.setValue(500)
        
        self.play_btn = QPushButton("Play")
        self.pause_btn = QPushButton("Pause")
        self.reset_btn = QPushButton("Reset")
        
        self.show_paths = QCheckBox("Show Paths")
        self.highlight_clusters = QCheckBox("Highlight Clusters")
        
        visual_layout.addWidget(QLabel("Speed:"))
        visual_layout.addWidget(self.animation_speed)
        visual_layout.addWidget(self.play_btn)
        visual_layout.addWidget(self.pause_btn)
        visual_layout.addWidget(self.reset_btn)
        visual_layout.addWidget(self.show_paths)
        visual_layout.addWidget(self.highlight_clusters)
        
        visual_group.setLayout(visual_layout)
        
        # Statistics Display
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels([
            "Pattern", "Frequency", "Probability", "Significance"
        ])
        
        stats_layout.addWidget(self.stats_table)
        stats_group.setLayout(stats_layout)
        
        # Results Display
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout()
        
        self.results_list = QListWidget()
        self.progress_bar = QProgressBar()
        self.export_btn = QPushButton("Export Results")
        
        results_layout.addWidget(self.results_list)
        results_layout.addWidget(self.progress_bar)
        results_layout.addWidget(self.export_btn)
        
        results_group.setLayout(results_layout)
        
        # Add all components to main layout
        layout.addWidget(search_group)
        layout.addWidget(visual_group)
        layout.addWidget(stats_group)
        layout.addWidget(results_group)
        
        self.setLayout(layout)
        self.connect_signals()
        
    def connect_signals(self):
        self.play_btn.clicked.connect(self.start_animation)
        self.pause_btn.clicked.connect(self.pause_animation)
        self.reset_btn.clicked.connect(self.reset_animation)
        self.export_btn.clicked.connect(self.export_results)
        self.animation_timer.timeout.connect(self.animate_step)
        self.auto_step.toggled.connect(self.toggle_auto_step)
        
    def search_els(self, term: str, step_size: int, direction: SearchDirection) -> List[Tuple[int, List[int]]]:
        results = []
        self.progress_bar.setMaximum(len(self.text))
        
        if direction in [SearchDirection.FORWARD, SearchDirection.BIDIRECTIONAL]:
            results.extend(self._search_direction(term, step_size, True))
            
        if direction in [SearchDirection.BACKWARD, SearchDirection.BIDIRECTIONAL]:
            results.extend(self._search_direction(term, step_size, False))
            
        self.analyze_results(results)
        return results
    
    def _get_grid_text(self) -> str:
        """Extract text from grid into single string"""
        text = ""
        for row in range(self.grid_panel.rows):
            for col in range(self.grid_panel.cols):
                item = self.grid_panel.grid_table.item(row, col)
                if item:
                    text += item.text()
        return text

    def _search_direction(self, term: str, step: int, forward: bool) -> List[Tuple[int, List[int]]]:
        """Search in specified direction with given step size"""
        results = []  # Will store tuples of (step_size, positions)
        text = self.text if forward else self.text[::-1]
        
        for start in range(len(text)):
            sequence = ""
            curr_positions = []
            
            pos = start
            while pos < len(text) and len(sequence) < len(term):
                sequence += text[pos]
                curr_positions.append(pos)
                pos += step
                
            if sequence == term:
                if not forward:
                    curr_positions = [len(text) - 1 - p for p in curr_positions]
                results.append((step, curr_positions))  # Return tuple of step and positions
                    
        return results

        
    def analyze_results(self, results: List[Tuple[int, List[int]]]):
        """Perform statistical analysis on results"""
        if not results:
            return
            
        # Calculate basic statistics
        total_sequences = len(results)
        avg_step_size = np.mean([step for step, _ in results])
        
        # Calculate probability
        text_length = len(self.text)
        probability = total_sequences / (text_length * len(results[0][1]))
        
        # Update statistics display
        self.stats_table.setRowCount(1)
        self.stats_table.setItem(0, 0, QTableWidgetItem(str(total_sequences)))
        self.stats_table.setItem(0, 1, QTableWidgetItem(f"{avg_step_size:.2f}"))
        self.stats_table.setItem(0, 2, QTableWidgetItem(f"{probability:.4f}"))
        
    def start_animation(self):
        """Start sequence animation"""
        if self.sequences:
            self.animation_timer.start(self.animation_speed.value())
            
    def pause_animation(self):
        """Pause sequence animation"""
        self.animation_timer.stop()
        
    def reset_animation(self):
        """Reset animation to beginning"""
        self.current_animation_step = 0
        self.clear_highlights()
        
    def animate_step(self):
        """Animate one step of sequence visualization"""
        if self.current_animation_step >= len(self.sequences):
            self.animation_timer.stop()
            return
            
        sequence = self.sequences[self.current_animation_step]
        self.highlight_sequence(sequence)
        self.current_animation_step += 1
        
    def highlight_sequence(self, positions: List[int]):
        """Highlight a sequence in the grid"""
        self.clear_highlights()
        
        for pos in positions:
            row = pos // self.grid_panel.cols
            col = pos % self.grid_panel.cols
            item = self.grid_panel.grid_table.item(row, col)
            if item:
                item.setBackground(QColor(255, 255, 0, 100))
                
        if self.show_paths.isChecked():
            self.draw_path(positions)
            
    def draw_path(self, positions: List[int]):
        """Draw connecting lines between sequence positions"""
        painter = QPainter(self.grid_panel)
        pen = QPen(QColor(0, 0, 255, 100))
        pen.setWidth(2)
        painter.setPen(pen)
        
        for i in range(len(positions) - 1):
            start_row = positions[i] // self.grid_panel.cols
            start_col = positions[i] % self.grid_panel.cols
            end_row = positions[i + 1] // self.grid_panel.cols
            end_col = positions[i + 1] % self.grid_panel.cols
            
            painter.drawLine(start_col * 40 + 20, start_row * 40 + 20,
                           end_col * 40 + 20, end_row * 40 + 20)
            
    def export_results(self):
        """Export search results to JSON"""
        data = {
            'parameters': {
                'term': self.term_input.text(),
                'step_size': self.step_size.value(),
                'direction': self.direction.currentText()
            },
            'sequences': [
                {
                    'step': step,
                    'positions': [
                        {'row': pos // self.grid_panel.cols + 1,
                         'col': pos % self.grid_panel.cols + 1}
                        for pos in positions
                    ]
                }
                for step, positions in self.sequences
            ],
            'statistics': {
                'total_sequences': len(self.sequences),
                'avg_step_size': np.mean([step for step, _ in self.sequences])
            }
        }
        
        with open('els_results.json', 'w') as f:
            json.dump(data, f, indent=2)
            
    def toggle_auto_step(self, checked: bool):
        """Toggle automatic step range calculation"""
        self.min_step.setEnabled(not checked)
        self.max_step.setEnabled(not checked)
        if checked:
            text_length = len(self.text)
            self.min_step.setValue(max(1, text_length // 100))
            self.max_step.setValue(min(1000, text_length // 10))
