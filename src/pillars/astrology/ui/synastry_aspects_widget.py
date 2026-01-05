"""
Synastry Aspects Widget — Cross-chart aspect analysis.
Displays aspects between two charts in list or grid format.
"""
from typing import List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from ..models.chart_models import PlanetPosition


class SynastryAspectsWidget(QWidget):
    """Widget displaying cross-chart aspects between two sets of planets."""
    
    # Aspect definitions: (name, angle, orb, glyph, color)
    ASPECTS = [
        ("Conjunction", 0, 8, "☌", "#ffee00"),
        ("Opposition", 180, 8, "☍", "#ff2a6d"),
        ("Trine", 120, 8, "△", "#4deeea"),
        ("Square", 90, 8, "□", "#f000ff"),
        ("Sextile", 60, 6, "⚹", "#74ee15"),
        ("Quincunx", 150, 3, "⚻", "#cccc88"),
        ("Semi-sextile", 30, 2, "⚺", "#88aa88"),
        ("Semi-square", 45, 2, "∠", "#cc88cc"),
        ("Sesquiquadrate", 135, 2, "⚼", "#cc8888"),
    ]
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._planets_a: List[PlanetPosition] = []
        self._planets_b: List[PlanetPosition] = []
        self._aspects_data: List[tuple] = []
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # View toggle
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("View:"))
        self.view_combo = QComboBox()
        self.view_combo.addItems(["List View", "Grid View"])
        self.view_combo.currentIndexChanged.connect(self._refresh_view)
        toolbar.addWidget(self.view_combo)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Table (used for both views, reconfigured dynamically)
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
    
    def set_data(self, planets_a: List[PlanetPosition], planets_b: List[PlanetPosition]):
        """Set the two planet lists and calculate aspects."""
        self._planets_a = planets_a or []
        self._planets_b = planets_b or []
        self._calculate_aspects()
        self._refresh_view()
    
    def _calculate_aspects(self):
        """Calculate all cross-chart aspects."""
        self._aspects_data = []
        
        for pa in self._planets_a:
            for pb in self._planets_b:
                diff = abs(pa.degree - pb.degree)
                if diff > 180:
                    diff = 360 - diff
                
                for name, angle, orb, glyph, color in self.ASPECTS:
                    if abs(diff - angle) <= orb:
                        actual_orb = abs(diff - angle)
                        self._aspects_data.append((
                            pa.name, pb.name, name, glyph, actual_orb, color
                        ))
                        break  # Only closest aspect per pair
    
    def _refresh_view(self):
        """Refresh the table based on current view mode."""
        if self.view_combo.currentIndex() == 0:
            self._show_list_view()
        else:
            self._show_grid_view()
    
    def _show_list_view(self):
        """Display aspects as a list."""
        self.table.clear()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Person A", "Aspect", "Person B", "Orb", ""])
        self.table.setRowCount(len(self._aspects_data))
        
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
            header.resizeSection(4, 30)
        
        for row, (pa, pb, name, glyph, orb, color) in enumerate(self._aspects_data):  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
            self.table.setItem(row, 0, QTableWidgetItem(pa))
            
            aspect_item = QTableWidgetItem(f"{glyph} {name}")
            aspect_item.setForeground(QColor(color))
            self.table.setItem(row, 1, aspect_item)
            
            self.table.setItem(row, 2, QTableWidgetItem(pb))
            self.table.setItem(row, 3, QTableWidgetItem(f"{orb:.1f}°"))
            
            # Color indicator
            color_item = QTableWidgetItem("●")
            color_item.setForeground(QColor(color))
            color_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, color_item)
    
    def _show_grid_view(self):
        """Display aspects as a grid/matrix."""
        self.table.clear()
        
        # Columns = Person B planets, Rows = Person A planets
        col_names = [p.name for p in self._planets_b]
        row_names = [p.name for p in self._planets_a]
        
        self.table.setColumnCount(len(col_names))
        self.table.setRowCount(len(row_names))
        self.table.setHorizontalHeaderLabels(col_names)
        self.table.setVerticalHeaderLabels(row_names)
        
        # Build lookup
        aspect_lookup = {}
        for pa, pb, _name, glyph, _orb, color in self._aspects_data:  # type: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnusedVariable]
            aspect_lookup[(pa, pb)] = (glyph, color)  # type: ignore[reportPossiblyUnboundVariable, reportUnboundVariable, unknown]
        
        for r, pa in enumerate(self._planets_a):
            for c, pb in enumerate(self._planets_b):
                key = (pa.name, pb.name)
                if key in aspect_lookup:
                    glyph, color = aspect_lookup[key]
                    item = QTableWidgetItem(glyph)
                    item.setForeground(QColor(color))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(r, c, item)
                else:
                    self.table.setItem(r, c, QTableWidgetItem(""))
        
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
