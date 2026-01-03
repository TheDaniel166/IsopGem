"""Synastry Midpoints Widget — Planet and House midpoint analysis.

Displays midpoints between corresponding bodies/houses in two charts.
"""

from __future__ import annotations

from typing import List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox
)

from ..models.chart_models import PlanetPosition, HousePosition


def calculate_midpoint(deg_a: float, deg_b: float) -> float:
    """Calculate the midpoint between two degrees on a circle."""
    # Normalize to 0-360
    a = deg_a % 360
    b = deg_b % 360
    
    # Calculate both possible midpoints
    mid1 = (a + b) / 2
    mid2 = mid1 + 180 if mid1 < 180 else mid1 - 180
    
    # Return the one that's between the two points (shorter arc)
    # Simple heuristic: use mid1 if the arc is < 180, else mid2
    diff = abs(a - b)
    if diff > 180:
        diff = 360 - diff
    
    # If input degrees are more than 180 apart, use the opposite midpoint
    if abs(a - b) > 180:
        return mid2 % 360
    return mid1 % 360


def degree_to_zodiac(deg: float) -> str:
    """Convert degree to zodiacal notation."""
    signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
    sign_idx = int(deg / 30) % 12
    sign_deg = int(deg % 30)
    minutes = int((deg % 1) * 60)
    return f"{sign_deg}° {signs[sign_idx]} {minutes}'"


class SynastryMidpointsWidget(QWidget):
    """Widget displaying midpoints between two charts."""
    
    PLANET_ORDER = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "North Node", "Chiron"]
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._planets_a: List[PlanetPosition] = []
        self._planets_b: List[PlanetPosition] = []
        self._houses_a: List[HousePosition] = []
        self._houses_b: List[HousePosition] = []
        self._midpoint_planets: List[PlanetPosition] = []
        self._midpoint_houses: List[HousePosition] = []
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Planet Midpoints Section
        planet_group = QGroupBox("Planet Midpoints")
        planet_layout = QVBoxLayout(planet_group)
        
        self.planet_table = QTableWidget()
        self.planet_table.setColumnCount(4)
        self.planet_table.setHorizontalHeaderLabels(["Body", "Person A", "Person B", "Midpoint"])
        self.planet_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = self.planet_table.horizontalHeader()
        if header:
            for i in range(4):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        planet_layout.addWidget(self.planet_table)
        layout.addWidget(planet_group)
        
        # House Midpoints Section
        house_group = QGroupBox("House Cusp Midpoints")
        house_layout = QVBoxLayout(house_group)
        
        self.house_table = QTableWidget()
        self.house_table.setColumnCount(4)
        self.house_table.setHorizontalHeaderLabels(["House", "Person A", "Person B", "Midpoint"])
        self.house_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header2 = self.house_table.horizontalHeader()
        if header2:
            for i in range(4):
                header2.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        house_layout.addWidget(self.house_table)
        layout.addWidget(house_group)
    
    def set_data(
        self,
        planets_a: List[PlanetPosition],
        planets_b: List[PlanetPosition],
        houses_a: List[HousePosition],
        houses_b: List[HousePosition],
    ) -> None:
        """Set the chart data and calculate midpoints."""
        self._planets_a = planets_a or []
        self._planets_b = planets_b or []
        self._houses_a = houses_a or []
        self._houses_b = houses_b or []
        self._calculate_midpoints()
        self._populate_tables()
    
    def _calculate_midpoints(self) -> None:
        """Calculate all midpoints and store for composite chart."""
        self._midpoint_planets = []
        self._midpoint_houses = []
        
        # Build lookup by name
        lookup_a = {p.name.lower(): p for p in self._planets_a}
        lookup_b = {p.name.lower(): p for p in self._planets_b}
        
        for name in self.PLANET_ORDER:
            key = name.lower()
            if key in lookup_a and key in lookup_b:
                mid_deg = calculate_midpoint(lookup_a[key].degree, lookup_b[key].degree)
                self._midpoint_planets.append(PlanetPosition(
                    name=name,
                    degree=mid_deg,
                    sign_index=int(mid_deg / 30) % 12
                ))
        
        # Houses
        house_lookup_a = {h.number: h for h in self._houses_a}
        house_lookup_b = {h.number: h for h in self._houses_b}
        
        for i in range(1, 13):
            if i in house_lookup_a and i in house_lookup_b:
                mid_deg = calculate_midpoint(house_lookup_a[i].degree, house_lookup_b[i].degree)
                self._midpoint_houses.append(HousePosition(number=i, degree=mid_deg))
    
    def _populate_tables(self) -> None:
        """Populate both tables with midpoint data."""
        # Planet table
        lookup_a = {p.name.lower(): p for p in self._planets_a}
        lookup_b = {p.name.lower(): p for p in self._planets_b}
        
        rows: list[tuple[str, float, float]] = []
        for name in self.PLANET_ORDER:
            key = name.lower()
            if key in lookup_a and key in lookup_b:
                rows.append((name, lookup_a[key].degree, lookup_b[key].degree))
        
        self.planet_table.setRowCount(len(rows))
        for r, (name, deg_a, deg_b) in enumerate(rows):
            mid = calculate_midpoint(deg_a, deg_b)
            self.planet_table.setItem(r, 0, QTableWidgetItem(name))
            self.planet_table.setItem(r, 1, QTableWidgetItem(degree_to_zodiac(deg_a)))
            self.planet_table.setItem(r, 2, QTableWidgetItem(degree_to_zodiac(deg_b)))
            self.planet_table.setItem(r, 3, QTableWidgetItem(degree_to_zodiac(mid)))
        
        # House table
        house_lookup_a = {h.number: h for h in self._houses_a}
        house_lookup_b = {h.number: h for h in self._houses_b}
        
        house_rows: list[tuple[int, float, float]] = []
        for i in range(1, 13):
            if i in house_lookup_a and i in house_lookup_b:
                house_rows.append((i, house_lookup_a[i].degree, house_lookup_b[i].degree))
        
        self.house_table.setRowCount(len(house_rows))
        for r, (num, deg_a, deg_b) in enumerate(house_rows):
            mid = calculate_midpoint(deg_a, deg_b)
            self.house_table.setItem(r, 0, QTableWidgetItem(f"House {num}"))
            self.house_table.setItem(r, 1, QTableWidgetItem(degree_to_zodiac(deg_a)))
            self.house_table.setItem(r, 2, QTableWidgetItem(degree_to_zodiac(deg_b)))
            self.house_table.setItem(r, 3, QTableWidgetItem(degree_to_zodiac(mid)))
    
    def get_midpoint_data(self) -> tuple[list[PlanetPosition], list[HousePosition]]:
        """Return calculated midpoint positions."""
        return self._midpoint_planets, self._midpoint_houses

