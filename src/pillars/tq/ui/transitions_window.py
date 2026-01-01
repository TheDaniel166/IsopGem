"""Transitions tool window - aligned with Visual Liturgy."""
import os
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMenu,
    QGridLayout, QWidget, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QAction, QPixmap, QPainter

from ..services.ternary_service import TernaryService
from ..services.ternary_transition_service import TernaryTransitionService
from ..services.ternary_transition_service import TernaryTransitionService
from .quadset_analysis_window import QuadsetAnalysisWindow, SubstrateWidget
from shared.ui.theme import COLORS, get_card_style
from shared.signals.navigation_bus import navigation_bus


class TransitionsWindow(QMainWindow):
    """Window for Ternary Transition System analysis."""
    
    def __init__(self, window_manager=None, parent=None):
        """Initialize the window."""
        super().__init__(parent)
        self.window_manager = window_manager
        self.ternary_service = TernaryService()
        self.transition_service = TernaryTransitionService()
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface with Visual Liturgy styling."""
        self.setWindowTitle("Ternary Transitions")
        self.setMinimumSize(900, 700)
        
        # Level 0: The Substrate (Thematic background)
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        bg_path = os.path.join(base_path, "assets", "textures", "transitions_substrate.png")
        
        # Fallback to quadset substrate if transitions-specific doesn't exist
        if not os.path.exists(bg_path):
            bg_path = os.path.join(base_path, "assets", "textures", "quadset_substrate.png")
        
        central = SubstrateWidget(bg_path)
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title_label = QLabel("Ternary Transition System")
        title_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 28pt;
            font-weight: 700;
            letter-spacing: -1px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc = QLabel("Taoist transformation framework for ternary numbers.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12pt;")
        layout.addWidget(desc)
        
        # Inputs Card
        inputs_card = self._create_card()
        inputs_layout = QGridLayout(inputs_card)
        inputs_layout.setSpacing(16)
        inputs_layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        inputs_header = QLabel("INPUTS")
        inputs_header.setStyleSheet(f"""
            font-weight: 800; 
            font-size: 11pt; 
            color: {COLORS['text_secondary']}; 
            letter-spacing: 2px;
        """)
        inputs_layout.addWidget(inputs_header, 0, 0, 1, 4)
        
        # Input A
        lbl_a_dec = QLabel("Input A (Decimal):")
        lbl_a_dec.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11pt;")
        inputs_layout.addWidget(lbl_a_dec, 1, 0)
        
        self.input_a_dec = QLineEdit()
        self.input_a_dec.setPlaceholderText("Decimal...")
        self.input_a_dec.textChanged.connect(lambda t: self._on_decimal_changed(t, self.input_a_tern))
        inputs_layout.addWidget(self.input_a_dec, 1, 1)
        
        lbl_a_tern = QLabel("Ternary:")
        lbl_a_tern.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11pt;")
        inputs_layout.addWidget(lbl_a_tern, 1, 2)
        
        self.input_a_tern = QLineEdit()
        self.input_a_tern.setPlaceholderText("Ternary...")
        self.input_a_tern.textChanged.connect(lambda t: self._on_ternary_changed(t, self.input_a_dec))
        inputs_layout.addWidget(self.input_a_tern, 1, 3)
        
        # Input B (Modifier)
        lbl_b_dec = QLabel("Input B (Decimal):")
        lbl_b_dec.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11pt;")
        inputs_layout.addWidget(lbl_b_dec, 2, 0)
        
        self.input_b_dec = QLineEdit()
        self.input_b_dec.setPlaceholderText("Decimal...")
        self.input_b_dec.textChanged.connect(lambda t: self._on_decimal_changed(t, self.input_b_tern))
        inputs_layout.addWidget(self.input_b_dec, 2, 1)
        
        lbl_b_tern = QLabel("Ternary:")
        lbl_b_tern.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11pt;")
        inputs_layout.addWidget(lbl_b_tern, 2, 2)
        
        self.input_b_tern = QLineEdit()
        self.input_b_tern.setPlaceholderText("Ternary...")
        self.input_b_tern.textChanged.connect(lambda t: self._on_ternary_changed(t, self.input_b_dec))
        inputs_layout.addWidget(self.input_b_tern, 2, 3)
        
        layout.addWidget(inputs_card)
        
        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(16)
        
        self.calc_btn = QPushButton("Calculate Single Transition")
        self.calc_btn.clicked.connect(self._calculate_single)
        self.calc_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['magus']};
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['magus_hover']};
            }}
        """)
        controls_layout.addWidget(self.calc_btn)
        

        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Results Table Card
        table_card = self._create_card()
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(24, 24, 24, 24)
        
        table_header = QLabel("RESULTS")
        table_header.setStyleSheet(f"""
            font-weight: 800; 
            font-size: 11pt; 
            color: {COLORS['text_secondary']}; 
            letter-spacing: 2px;
            margin-bottom: 12px;
        """)
        table_layout.addWidget(table_header)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Step", "Current (A)", "Modifier (B)", "Result (Ternary)", "Result (Decimal)"])
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                gridline-color: {COLORS['border']};
                selection-background-color: {COLORS['primary_light']};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QTableWidget::item:alternate {{
                background-color: {COLORS['background_alt']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['background_alt']};
                padding: 10px 8px;
                border: none;
                border-bottom: 2px solid {COLORS['border']};
                font-weight: 600;
                color: {COLORS['text_primary']};
            }}
        """)
        
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Enable context menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_card)
        

        
    def _create_card(self) -> QFrame:
        """Create a styled card container with drop shadow."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 40))
        card.setGraphicsEffect(shadow)
        
        return card
        
    def _show_context_menu(self, position):
        """Show context menu for table items."""
        item = self.table.itemAt(position)
        if not item:
            return
            
        # Check if it's the Decimal Result column (index 4)
        if item.column() == 4:
            viewport = self.table.viewport()
            if not viewport:
                return
            menu = QMenu()
            send_action = QAction("Send to Quadset Analysis", self)
            send_action.triggered.connect(lambda: self._send_to_quadset(item.text()))
            menu.addAction(send_action)
            
            menu.addSeparator()
            
            emerald_action = QAction("Send Sequence to Emerald Tablet", self)
            emerald_action.triggered.connect(self._send_to_emerald)
            menu.addAction(emerald_action)
            
            menu.exec(viewport.mapToGlobal(position))
            
    def _send_to_emerald(self):
        """Package current sequence and send to Emerald Hub."""
        if not self.window_manager: return
        
        # 1. Harvest Data
        rows = []
        for r in range(self.table.rowCount()):
            row_vals = []
            for c in range(self.table.columnCount()):
                it = self.table.item(r, c)
                row_vals.append(it.text() if it else "")
            rows.append(row_vals)
        
        if not rows: return
        
        data = {
            "columns": ["Step", "Current (A)", "Modifier (B)", "Result (Ternary)", "Result (Decimal)"],
            "data": rows,
            "styles": {}
        }
        
        # 2. Request Window via Signal Bus to avoid direct import
        # We pass minimal params to open it
        navigation_bus.request_window.emit(
            "emerald_tablet", 
            {"allow_multiple": False, "window_manager": self.window_manager}
        )
        
        # 3. Retrieve instance and send data (Logic coupled to instance existence for now)
        # Since request_window is synchronous in our architecture, we can try to retrieve it immediately
        hub = self.window_manager.get_active_windows().get("emerald_tablet")
        
        if hub and hasattr(hub, "receive_import"):
            name = f"Transformation_{self.input_a_tern.text()}_by_{self.input_b_tern.text()}"
            hub.receive_import(name, data)
            
    def _send_to_quadset(self, decimal_value: str):
        """Send decimal value to Quadset Analysis window."""
        if not self.window_manager:
            return
            
        # Requests window via bus
        navigation_bus.request_window.emit(
            "quadset_analysis",
            {"window_manager": self.window_manager}
        )
        
        # We can't easily get the specific instance if multiple are allowed, 
        # but QuadsetAnalysis is usually unique or we rely on the bus passing initial_value if it was new.
        # But here we want to update an *existing* or *just opened* window.
        # For now, let's look for the most recent one or pass initial_value in params if we wanted a new one.
        # The original code opened a generic one. 
        # If we want to set field on the active one:
        
        # Better approach: Pass initial_value in params if possible
        # usage: request_window("quadset_analysis", {"initial_value": decimal_value})
        
        navigation_bus.request_window.emit(
            "quadset_analysis",
            {
                "window_manager": self.window_manager,
                "initial_value": decimal_value
            }
        )
        
        # The params above handle setting the value for new windows.
        # If we wanted to update an existing one without reopening/reinit, we'd need a different mechanism,
        # but the standard pattern is passing init params.
        pass

        
    def _on_decimal_changed(self, text: str, target_field: QLineEdit):
        """Handle decimal input change."""
        if not text:
            target_field.blockSignals(True)
            target_field.clear()
            target_field.blockSignals(False)
            return
            
        try:
            val = int(text)
            tern = self.ternary_service.decimal_to_ternary(val)
            target_field.blockSignals(True)
            target_field.setText(tern)
            target_field.blockSignals(False)
        except ValueError:
            pass

    def _on_ternary_changed(self, text: str, target_field: QLineEdit):
        """Handle ternary input change."""
        if not text:
            target_field.blockSignals(True)
            target_field.clear()
            target_field.blockSignals(False)
            return
            
        try:
            val = self.ternary_service.ternary_to_decimal(text)
            target_field.blockSignals(True)
            target_field.setText(str(val))
            target_field.blockSignals(False)
        except ValueError:
            pass

    def _calculate_single(self):
        """Calculate one transition."""
        t1 = self.input_a_tern.text()
        t2 = self.input_b_tern.text()
        
        if not t1 or not t2:
            return
            
        result = self.transition_service.transition(t1, t2)
        try:
            dec_res = self.ternary_service.ternary_to_decimal(result)
        except ValueError:
            dec_res = 0
            
        self.table.setRowCount(1)
        self._set_row(0, 1, t1, t2, result, dec_res)



    def _set_row(self, row, step, t1, t2, res, dec_res):
        """Helper to set table row data."""
        self.table.setItem(row, 0, QTableWidgetItem(str(step)))
        self.table.setItem(row, 1, QTableWidgetItem(t1))
        self.table.setItem(row, 2, QTableWidgetItem(t2))
        
        # Color code result digits
        res_item = QTableWidgetItem(res)
        res_item.setFont(QFont("Monospace"))
        self.table.setItem(row, 3, res_item)
        
        self.table.setItem(row, 4, QTableWidgetItem(str(dec_res)))


