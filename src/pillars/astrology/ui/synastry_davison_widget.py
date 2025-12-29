"""
Synastry Davison Widget — Davison Relationship Chart information.
Displays the time/space midpoint used for Davison chart calculation.
"""
from typing import Dict, Optional, Any
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt


class SynastryDavisonWidget(QWidget):
    """Widget displaying Davison time/space midpoint information."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Explanation
        intro = QLabel(
            "<b>Davison Relationship Chart</b><br><br>"
            "The Davison chart is cast for the exact midpoint in time and space between two people. "
            "Unlike the Composite chart (which uses midpoints of planetary positions), the Davison "
            "chart represents a real moment in time and a real location, making it interpretable "
            "as a standalone natal chart for the relationship itself."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #94a3b8; font-size: 10pt;")
        layout.addWidget(intro)
        
        layout.addSpacing(16)
        
        # Midpoint Information Group
        group = QGroupBox("Calculated Midpoint")
        form = QFormLayout(group)
        
        self.time_label = QLabel("—")
        self.lat_label = QLabel("—")
        self.lon_label = QLabel("—")
        
        form.addRow("Midpoint Date/Time:", self.time_label)
        form.addRow("Midpoint Latitude:", self.lat_label)
        form.addRow("Midpoint Longitude:", self.lon_label)
        
        layout.addWidget(group)
        layout.addStretch()
    
    def set_data(self, davison_info: Optional[Dict[str, Any]]):
        """Update the displayed Davison midpoint information."""
        if not davison_info:
            self.time_label.setText("—")
            self.lat_label.setText("—")
            self.lon_label.setText("—")
            return
        
        mid_time = davison_info.get("midpoint_time")
        if isinstance(mid_time, datetime):
            self.time_label.setText(mid_time.strftime("%Y-%m-%d %H:%M:%S UTC"))
        else:
            self.time_label.setText(str(mid_time) if mid_time else "—")
        
        mid_lat = davison_info.get("midpoint_lat")
        mid_lon = davison_info.get("midpoint_lon")
        
        self.lat_label.setText(f"{mid_lat:.4f}°" if mid_lat is not None else "—")
        self.lon_label.setText(f"{mid_lon:.4f}°" if mid_lon is not None else "—")
