"""
Fractal Network Dialog - The Dimensional Descent Viewer.
A popup that visualizes the hierarchical path from Singularity (6D) to Leaf (0D) for any Ditrune.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class FractalNetworkDialog(QDialog):
    """
    Non-modal popup detailing the hierarchical network of a Ditrune.
    Shows the path: Singularity -> Region -> Area -> Leaf.
    """
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Fractal Network Analysis")
        self.setWindowFlags(Qt.WindowType.Window) # Standard window to ensure visibility
        self.setModal(False)
        self.resize(300, 400)
        self.setStyleSheet("background-color: #050510; color: #ddd;")
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        
        self.title = QLabel("Network Path")
        self.title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.title.setStyleSheet("color: #fff; border-bottom: 1px solid #444; padding-bottom: 5px;")
        self.layout.addWidget(self.title)
        
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(5)
        self.layout.addWidget(self.content_area)
        
        self.layout.addStretch()
        
    def update_network(self, ternary: str):
        """Updates the view with the path for the given Ditrune."""
        # Clear previous
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if not ternary:
            self.content_layout.addWidget(QLabel("No Focus Selected"))
            return

        # Calculate IDs (Base 9 from Bigrams - kept for reference, or remove?)
        # User wants simple single-digit progression now.
        
        dims = [
            ("SINGULARITY (6D)", "The Source", "#ff3333"),
            ("AXIS (5D)", "Primary Axis", "#ff9933"),
            ("FACE (4D)", "Region Face", "#ffff00"),
            ("CELL (3D)", "Volume Center", "#99ff33"),
            ("PLANE (2D)", "Area Plane", "#00ffff"),
            ("LINE (1D)", "Linear Path", "#3399ff"),
            ("LEAF (0D)", "Ditrune Point", "#9600ff")
        ]
        
        # 6D: 000000 (0 digits)
        # 5D: X00000 (1 digit)
        # 4D: XX0000 (2 digits)
        # 3D: XXX000 (3 digits)
        # 2D: XXXX00 (4 digits)
        # 1D: XXXXX0 (5 digits)
        # 0D: XXXXXX (6 digits)
        
        for i in range(7):
            # Masking: Take first i digits, pad rest with 0
            # i=0 -> "" -> 000000
            # i=6 -> full -> no pad
            prefix = ternary[:i]
            pad = "0" * (6-i)
            val = prefix + pad
            
            # Current digit value (for ID)
            # 6D has no "ID"
            if i == 0:
                step_id = "ROOT"
            else:
                # The ID is usually the value of the last exposed digit?
                # Or just use the masked value itself.
                # Let's show the value added.
                new_digit = ternary[i-1] if i > 0 else "-"
                step_id = f"Step {i} (+{new_digit})"

            label, desc_base, color = dims[i]
            
            # Add Arrows between steps
            if i > 0:
                self._add_arrow()
                
            self._add_step(label, val, desc_base, color)
        
    def _add_step(self, label, value, desc, color):
        container = QFrame()
        container.setStyleSheet(f"border: 1px solid {color}; border-radius: 5px; background-color: rgba(255,255,255,0.05);")
        l = QVBoxLayout(container)
        l.setContentsMargins(5, 5, 5, 5)
        l.setSpacing(2)
        
        lbl_title = QLabel(label)
        lbl_title.setStyleSheet(f"color: {color}; font-weight: bold;")
        l.addWidget(lbl_title)
        
        lbl_val = QLabel(f"Value: {value}")
        lbl_val.setFont(QFont("Monospace", 10))
        l.addWidget(lbl_val)
        
        lbl_desc = QLabel(desc)
        lbl_desc.setStyleSheet("color: #aaa; font-style: italic;")
        l.addWidget(lbl_desc)
        
        self.content_layout.addWidget(container)

    def _add_arrow(self):
        lbl = QLabel("  ↓")
        lbl.setStyleSheet("color: #555; font-size: 14px; font-weight: bold;")
        self.content_layout.addWidget(lbl)