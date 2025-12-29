"""
Composite Chart Window — Non-modal window displaying midpoint-based composite chart.
"""
from typing import List, Optional

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

from ..models.chart_models import PlanetPosition, HousePosition
from .chart_canvas import ChartCanvas


class CompositeChartWindow(QMainWindow):
    """Non-modal window for displaying a composite (midpoint) chart."""
    
    def __init__(self, planets: List[PlanetPosition], houses: List[HousePosition], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Composite Chart (Midpoints)")
        self.resize(700, 700)
        
        # Non-modal by default (no exec(), just show())
        self.setWindowModality(Qt.WindowModality.NonModal)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Chart canvas
        self.canvas = ChartCanvas()
        self.canvas.set_data(planets, houses)
        layout.addWidget(self.canvas)
