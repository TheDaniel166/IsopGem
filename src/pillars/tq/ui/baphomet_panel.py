"""
Baphomet Panel - The Converse Analysis Inspector.
Displays the Converse Pair relationship, differential, and sumlation for selected Kamea cells.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ..models.kamea_cell import KameaCell
from ..services.baphomet_color_service import BaphometColorService

class BaphometPanel(QWidget):
    """
    Side Panel for the Kamea of Baphomet.
    Focuses on the "Converse Pair" relationship (Swapping Top/Bottom Trigrams).
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.setStyleSheet("background-color: #0a0a0a; border-left: 1px solid #ff3333;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("BAPHOMET\nANALYSIS")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #ff3333; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # --- Selected Cell ---
        self.lbl_selected_title = QLabel("Selected Cell")
        self.lbl_selected_title.setStyleSheet("color: #888; font-weight: bold;")
        layout.addWidget(self.lbl_selected_title)
        
        self.lbl_selected_val = QLabel("000000")
        self.lbl_selected_val.setStyleSheet("color: #fff; font-size: 24px; font-family: monospace;")
        self.lbl_selected_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_selected_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_selected_val)

        # Color Swatch
        self.color_swatch = QFrame()
        self.color_swatch.setFixedSize(50, 50)
        self.color_swatch.setStyleSheet("background-color: #000; border: 1px solid #333; border-radius: 4px;")
        
        # Center the swatch
        h_layout = QVBoxLayout() 
        h_layout.addWidget(self.color_swatch) 
        h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(h_layout)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #333;")
        layout.addWidget(line)
        
        # --- Converse Pair ---
        self.lbl_converse_title = QLabel("Converse Pair (Mirror)")
        self.lbl_converse_title.setStyleSheet("color: #888; font-weight: bold;")
        layout.addWidget(self.lbl_converse_title)
        
        self.lbl_converse_val = QLabel("000000")
        self.lbl_converse_val.setStyleSheet("color: #ff3333; font-size: 24px; font-family: monospace;")
        self.lbl_converse_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_converse_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_converse_val)

        # Divider 2
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("color: #333;")
        layout.addWidget(line2)

        # --- Converse Differential ---
        self.lbl_diff_title = QLabel("Differential (Law of 26)")
        self.lbl_diff_title.setStyleSheet("color: #888; font-weight: bold;")
        layout.addWidget(self.lbl_diff_title)
        
        self.lbl_diff_val = QLabel("Diff: 0\nK: 0")
        self.lbl_diff_val.setStyleSheet("color: #4dff4d; font-size: 18px; font-family: monospace;")
        self.lbl_diff_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_diff_val)

        # Divider 3
        line3 = QFrame()
        line3.setFrameShape(QFrame.Shape.HLine)
        line3.setStyleSheet("color: #333;")
        layout.addWidget(line3)

        # --- Converse Sumlation ---
        self.lbl_sum_title = QLabel("Sumlation (Law of 28)")
        self.lbl_sum_title.setStyleSheet("color: #888; font-weight: bold;")
        layout.addWidget(self.lbl_sum_title)
        
        self.lbl_sum_val = QLabel("Sum: 0\nL: 0")
        self.lbl_sum_val.setStyleSheet("color: #4d4dff; font-size: 18px; font-family: monospace;")
        self.lbl_sum_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_sum_val)
        
        # Analysis Text
        self.lbl_analysis = QLabel("Analysis")
        self.lbl_analysis.setWordWrap(True)
        self.lbl_analysis.setStyleSheet("color: #aaa; margin-top: 10px;")
        layout.addWidget(self.lbl_analysis)

        layout.addStretch()

    def analyze_cell(self, cell: KameaCell):
        """Updates the panel with the selected cell's Converse data."""
        t_val = cell.ternary_value
        
        # Display Selected
        self.lbl_selected_val.setText(f"{t_val}\n({cell.decimal_value})")
        
        # Calculate Converse (Swap Trigrams)
        # Top: 0-3, Bottom: 3-6
        top = t_val[0:3]
        bot = t_val[3:6]
        converse_t = bot + top
        converse_d = int(converse_t, 3)
        
        self.lbl_converse_val.setText(f"{converse_t}\n({converse_d})")
        
        # Calculate Differential
        diff = abs(cell.decimal_value - converse_d)
        k_factor = diff // 26
        
        self.lbl_diff_val.setText(f"Diff: {diff}\nK-Axis: {k_factor}")

        # Calculate Sumlation
        total_sum = cell.decimal_value + converse_d
        l_factor = total_sum // 28
        
        self.lbl_sum_val.setText(f"Sum: {total_sum}\nL-Axis: {l_factor}")
        
        # Check Identity
        if top == bot:
            self.lbl_analysis.setText("IDENTITY STATE\n(Top == Bottom)\n\nThis cell lies on the Axis of Unity. The Mirror reflects the Self without distortion.")
            self.lbl_converse_val.setStyleSheet("color: #ffffff; font-size: 24px; font-family: monospace;")
        else:
            self.lbl_analysis.setText("DUAL STATE\n(Top != Bottom)\n\nThis cell has a Converse Twin on the opposite side of the Axis.")
            self.lbl_converse_val.setStyleSheet("color: #ff3333; font-size: 24px; font-family: monospace;")

        # Resolve Color
        color = BaphometColorService.resolve_color(t_val)
        self.color_swatch.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #555; border-radius: 4px;")

