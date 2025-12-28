"""
Nuclear Mutation Panel - The Reactor Sidebar.
Displays the Soul Analysis of a Kamea cell, visualizing the Skin → Body → Core mutation path.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from ..models.kamea_cell import KameaCell
from ..services.ditrunal_service import DitrunalService
from ..repositories.cipher_repository import CipherRepository

class NuclearMutationPanel(QWidget):
    """
    Side Panel ("The Reactor") for analyzing the Soul of a Kamea Cell.
    Visualizes the Nuclear Mutation breakdown: Skin -> Body -> Core.
    """
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setFixedWidth(300)
        self.setStyleSheet("background-color: #0a0a1a; border-left: 1px solid #333;")
        self.cipher_repo = CipherRepository()
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("NUCLEAR REACTOR")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #FFD700; font-size: 16pt; font-weight: bold; margin-top: 10px;")
        layout.addWidget(header)
        
        # Entanglement/Vector Info
        entanglement_frame = QFrame()
        entanglement_frame.setStyleSheet("border: 1px solid #333; border-radius: 5px; padding: 5px;")
        v_entangle = QVBoxLayout(entanglement_frame)
        self.lbl_class = QLabel("Awaiting Classification...")
        self.lbl_class.setFont(QFont("Monospace", 10))
        self.lbl_class.setStyleSheet("color: #00eeff;")
        self.lbl_class.setWordWrap(True)
        v_entangle.addWidget(self.lbl_class)
        self.lbl_entangle = QLabel("Awaiting Entanglement...")
        self.lbl_entangle.setFont(QFont("Monospace", 10))
        self.lbl_entangle.setStyleSheet("color: #00eeff;")
        self.lbl_entangle.setWordWrap(True)
        v_entangle.addWidget(self.lbl_entangle)
        
        self.lbl_vector = QLabel("")
        self.lbl_vector.setFont(QFont("Monospace", 9))
        self.lbl_vector.setStyleSheet("color: #ff9900; font-style: italic;")
        v_entangle.addWidget(self.lbl_vector)
        layout.addWidget(entanglement_frame)

        # Current Cell Info
        self.info_label = QLabel("Select a Cell to Analyze")
        self.info_label.setStyleSheet("color: #a0a0ff; font-size: 10pt;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Mutation Visualization Area
        self.mutation_area = QScrollArea()
        self.mutation_area.setWidgetResizable(True)
        self.mutation_area.setStyleSheet("background: transparent; border: none;")
        self.mutation_content = QWidget()
        self.mutation_content.setStyleSheet("background-color: #0a0a1a;") # Enforce Dark Background
        self.mutation_layout = QVBoxLayout(self.mutation_content)
        self.mutation_area.setWidget(self.mutation_content)
        layout.addWidget(self.mutation_area)
        
        layout.addStretch()
        
    def analyze_cell(self, cell: KameaCell):
        """Performs Soul Analysis on the cell."""
        # Update Info
        conrune_val = DitrunalService.get_conrune_value(cell.ternary_value)
        self.lbl_entangle.setText(
            f"Conrune Pair: {conrune_val}\n"
            f"Coordinate: ({-cell.x}, {-cell.y})"
        )
        # Star Classification
        star_cat = DitrunalService.get_star_category(cell.ternary_value)
        
        # Cipher Bond
        t_left = cell.ternary_value[0:3]
        t_right = cell.ternary_value[3:6]
        val_left = int(t_left, 3)
        val_right = int(t_right, 3)
        
        token_left = self.cipher_repo.get_by_decimal(val_left)
        token_right = self.cipher_repo.get_by_decimal(val_right)
        
        lbl_left = token_left.label if token_left else "?"
        lbl_right = token_right.label if token_right else "?"
        
        self.lbl_class.setText(f"Star Category: {star_cat}\nBond: {lbl_left} / {lbl_right}")
        
        vector = cell.conrune_vector
        self.lbl_vector.setText(f"Vector Magnitude: {vector}")

        self.info_label.setText(
            f"Subject: ({cell.x}, {cell.y})\n"
            f"Locator: {cell.kamea_locator}\n"
            f"Value: {cell.decimal_value} | {cell.ternary_value}"
        )
        
        # Clear previous analysis
        self._clear_layout(self.mutation_layout)
        
        # Get Path
        path = DitrunalService.analyze_mutation_path(cell.ternary_value)
        family_id = DitrunalService.get_family_id(cell.ternary_value)
        family_color = self._get_family_color_hex(family_id)
        
        # Determine Target Core from the Prime (last in path)
        prime_val = path[-1]
        target_core = prime_val[2:4]

        # Visualize Path
        for i, val in enumerate(path):
            is_prime = (i == len(path) - 1)
            is_acolyte = False
            
            if not is_prime:
                # Check for Acolyte State (Body == Prime's Core)
                # This covers both Cycle Primes (Fam 5/7) and Standard Primes.
                body = val[1] + val[4]
                if body == target_core:
                    is_acolyte = True
            
            # Calculate Decimal
            decimal_val = int(val, 3)
            
            # Label
            if is_prime:
                label_text = f"CORE (Prime)\n{decimal_val} | {val}\nFamily {family_id}"
            elif is_acolyte:
                label_text = f"ACOLYTE\n{decimal_val} | {val}\nAwaiting Priming"
            else:
                # If not Prime and not Acolyte (Core != Body), it is a Temple.
                label_text = f"TEMPLE\n{decimal_val} | {val}\nMutating..."
                
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Style
            if is_prime:
                # High contrast for Prime: Black text on Family Color
                style = f"""
                    background-color: {family_color};
                    color: black;
                    border: 2px solid white;
                    border-radius: 8px;
                    padding: 10px;
                    font-weight: bold;
                    font-size: 12pt;
                """
            elif is_acolyte:
                # Lighter text for visibility, Dashed Border
                style = f"""
                    border: 1px dashed {family_color};
                    color: #ffffff;
                    border-radius: 6px;
                    padding: 8px;
                    font-weight: bold;
                    font-size: 11pt;
                """
            else: # Temple
                # White text, Dotted Border
                style = f"""
                    border: 1px dotted rgba(255, 255, 255, 50);
                    color: #e0e0e0;
                    font-size: 10pt;
                    padding: 5px;
                """
                
            label.setStyleSheet(style)
            self.mutation_layout.addWidget(label)
            
            # Connector arrow (if not last)
            if not is_prime:
                arrow = QLabel("↓")
                arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
                arrow.setStyleSheet("color: #555; font-weight: bold;")
                self.mutation_layout.addWidget(arrow)

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _get_family_color_hex(self, family_id: int) -> str:
        # Reusing the cosmic palette
        colors = {
            0: "#2d2d2d", # Void
            1: "#ff4d4d", # Pulse
            2: "#4d4dff", # Recoil
            3: "#4dff4d", # Projector
            4: "#ffffff", # Monolith
            5: "#9933ff", # Weaver
            6: "#33ffff", # Receiver
            7: "#ff9933", # Splicer
            8: "#1a1a52"  # Abyss
        }
        return colors.get(family_id, "#555555")