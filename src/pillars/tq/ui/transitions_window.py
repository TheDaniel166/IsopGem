"""Transitions tool window."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QGroupBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QSpinBox, QMenu,
    QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QAction

from ..services.ternary_service import TernaryService
from ..services.ternary_transition_service import TernaryTransitionService
from .quadset_analysis_window import QuadsetAnalysisWindow


class TransitionsWindow(QDialog):
    """Window for Ternary Transition System analysis."""
    
    def __init__(self, window_manager=None, parent=None):
        """Initialize the window."""
        super().__init__(parent)
        self.window_manager = window_manager
        self.ternary_service = TernaryService()
        self.transition_service = TernaryTransitionService()
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Ternary Transitions")
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Ternary Transition System")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc = QLabel("Taoist transformation framework for ternary numbers.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #666; font-size: 12pt;")
        layout.addWidget(desc)
        
        # Inputs Section
        inputs_group = QGroupBox("Inputs")
        inputs_layout = QGridLayout()
        inputs_layout.setSpacing(15)
        
        # Input A
        inputs_layout.addWidget(QLabel("Input A (Decimal):"), 0, 0)
        self.input_a_dec = QLineEdit()
        self.input_a_dec.setPlaceholderText("Decimal...")
        self.input_a_dec.textChanged.connect(lambda t: self._on_decimal_changed(t, self.input_a_tern))
        inputs_layout.addWidget(self.input_a_dec, 0, 1)
        
        inputs_layout.addWidget(QLabel("Ternary:"), 0, 2)
        self.input_a_tern = QLineEdit()
        self.input_a_tern.setPlaceholderText("Ternary...")
        self.input_a_tern.textChanged.connect(lambda t: self._on_ternary_changed(t, self.input_a_dec))
        inputs_layout.addWidget(self.input_a_tern, 0, 3)
        
        # Input B (Modifier)
        inputs_layout.addWidget(QLabel("Input B (Decimal):"), 1, 0)
        self.input_b_dec = QLineEdit()
        self.input_b_dec.setPlaceholderText("Decimal...")
        self.input_b_dec.textChanged.connect(lambda t: self._on_decimal_changed(t, self.input_b_tern))
        inputs_layout.addWidget(self.input_b_dec, 1, 1)
        
        inputs_layout.addWidget(QLabel("Ternary:"), 1, 2)
        self.input_b_tern = QLineEdit()
        self.input_b_tern.setPlaceholderText("Ternary...")
        self.input_b_tern.textChanged.connect(lambda t: self._on_ternary_changed(t, self.input_b_dec))
        inputs_layout.addWidget(self.input_b_tern, 1, 3)
        
        inputs_group.setLayout(inputs_layout)
        layout.addWidget(inputs_group)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.calc_btn = QPushButton("Calculate Single Transition")
        self.calc_btn.clicked.connect(self._calculate_single)
        self.calc_btn.setStyleSheet("background-color: #2563eb; color: white; padding: 8px;")
        controls_layout.addWidget(self.calc_btn)
        
        controls_layout.addSpacing(20)
        
        controls_layout.addWidget(QLabel("Iterations:"))
        self.iter_spin = QSpinBox()
        self.iter_spin.setRange(1, 100)
        self.iter_spin.setValue(10)
        controls_layout.addWidget(self.iter_spin)
        
        self.seq_btn = QPushButton("Generate Sequence")
        self.seq_btn.clicked.connect(self._generate_sequence)
        self.seq_btn.setStyleSheet("background-color: #7c3aed; color: white; padding: 8px;")
        controls_layout.addWidget(self.seq_btn)
        
        layout.addLayout(controls_layout)
        
        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Step", "Current (A)", "Modifier (B)", "Result (Ternary)", "Result (Decimal)"])
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Enable context menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        
        layout.addWidget(self.table)
        
        # Legend/Info
        info_group = QGroupBox("Philosophical Key")
        info_layout = QHBoxLayout()
        
        for digit, info in self.transition_service.PHILOSOPHY.items():
            lbl = QLabel(f"<b>{digit}</b>: {info['meaning']} - {info['force']}")
            lbl.setStyleSheet("background-color: #f3f4f6; padding: 5px; border-radius: 4px;")
            info_layout.addWidget(lbl)
            
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
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
            menu.exec(viewport.mapToGlobal(position))
            
    def _send_to_quadset(self, decimal_value: str):
        """Send decimal value to Quadset Analysis window."""
        if not self.window_manager:
            return
            
        # Open the window
        window = self.window_manager.open_window(
            "quadset_analysis",
            QuadsetAnalysisWindow
        )
        
        # Set the value
        if window and hasattr(window, 'input_field'):
            window.input_field.setText(decimal_value)
            window.raise_()
            window.activateWindow()

        
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

    def _generate_sequence(self):
        """Generate transition sequence."""
        t1 = self.input_a_tern.text()
        t2 = self.input_b_tern.text()
        iterations = self.iter_spin.value()
        
        if not t1 or not t2:
            return
            
        sequence = self.transition_service.generate_sequence(t1, t2, iterations)
        
        self.table.setRowCount(len(sequence))
        for i, (curr, mod, res) in enumerate(sequence):
            try:
                dec_res = self.ternary_service.ternary_to_decimal(res)
            except ValueError:
                dec_res = 0
            self._set_row(i, i+1, curr, mod, res, dec_res)

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

from PyQt6.QtWidgets import QGridLayout
