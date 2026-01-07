"""Trigram Visualizer Tool."""
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QFrame, QPushButton, QWidget,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QColor, QMouseEvent

from shared.ui.theme import COLORS, get_card_style
from shared.ui.catalyst_styles import get_navigator_style
from ..services.ternary_service import TernaryService
from .trigram_glyph import TrigramGlyph


class TrigramVisualizerWindow(QMainWindow):
    """Window for visualizing Trigrams as geometric glyphs."""
    
    def __init__(self, parent=None):
        """Initialize the visualizer window."""
        super().__init__(parent)
        self.ternary_service = TernaryService()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = QPoint()
        self._setup_ui()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for dragging."""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        
    def _setup_ui(self):
        """Set up the user interface according to Visual Liturgy."""
        self.setWindowTitle("Trigram Visualizer")
        self.setMinimumSize(700, 520)
        
        # Level 0: The Substrate
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        bg_path = os.path.join(base_path, "assets", "textures", "substrate_v2.png")
        # Harmonia Tuning 1: Ghost Layer (15% opacity texture handled via stylesheet blending if possible, 
        # but here we use the established pattern with a dark background color)
        bg_style = f"background-image: url({bg_path}); background-repeat: repeat; background-position: center;"
        
        central = QWidget()
        central.setObjectName("Substrate")
        central.setStyleSheet(f"""
            QWidget#Substrate {{
                background-color: {COLORS.get('void', '#0e1116')};
                {bg_style}
                border: 1px solid {COLORS.get('gold', '#ffd700')};
                border-radius: 4px;
            }}
        """)
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(2, 2, 2, 2)

        # Harmonia Tuning: The Header (Custom Title Bar)
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(16, 0, 8, 0)
        
        title_label = QLabel("TRIGRAM VISUALIZER") # Uppercase
        title_label.setStyleSheet(f"""
            color: {COLORS.get('gold', '#ffd700')};
            font-family: 'Cinzel', 'Trajan Pro', serif;
            font-size: 12pt;
            font-weight: 700;
            letter-spacing: 2px;
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS.get('text_secondary', '#94a3b8')};
                font-size: 20pt;
                border: none;
                font-weight: 300;
            }}
            QPushButton:hover {{
                color: {COLORS.get('error', '#ef4444')};
            }}
        """)
        title_layout.addWidget(close_btn)
        
        main_layout.addWidget(title_bar)

        # Content Area
        content_area = QWidget()
        layout = QVBoxLayout(content_area)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 20, 40, 40)
        
        # Level 1: The Tablet
        content_card = QFrame()
        content_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS.get('surface', '#1e293b')};
                border-radius: 12px;
                border: 1px solid {COLORS.get('ash', '#334155')};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 80)) # Slightly darker for depth
        content_card.setGraphicsEffect(shadow)
        
        # Split Layout
        card_main_layout = QHBoxLayout(content_card)
        card_main_layout.setSpacing(30)
        card_main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Left Side: Controls
        control_container = QWidget()
        control_container.setStyleSheet("background: transparent; border: none;") # Reset for inner widget
        control_layout = QVBoxLayout(control_container)
        control_layout.setSpacing(20)
        
        # Decimal Input
        dec_label = QLabel("DECIMAL VALUE")
        dec_label.setStyleSheet(f"color: {COLORS.get('text_secondary', '#94a3b8')}; font-size: 9pt; font-weight: 700; letter-spacing: 1px;")
        control_layout.addWidget(dec_label)
        
        self.decimal_input = QLineEdit()
        self.decimal_input.setPlaceholderText("0 - 26")
        self.decimal_input.setStyleSheet(self._get_input_style())
        self.decimal_input.textChanged.connect(self._on_decimal_changed)
        control_layout.addWidget(self.decimal_input)
        
        # Ternary Input
        ter_label = QLabel("TERNARY KEY")
        ter_label.setStyleSheet(f"color: {COLORS.get('text_secondary', '#94a3b8')}; font-size: 9pt; font-weight: 700; letter-spacing: 1px;")
        control_layout.addWidget(ter_label)
        
        self.ternary_input = QLineEdit()
        self.ternary_input.setPlaceholderText("e.g. 120")
        self.ternary_input.setStyleSheet(self._get_input_style())
        self.ternary_input.textChanged.connect(self._on_ternary_changed)
        control_layout.addWidget(self.ternary_input)
        
        # Status Label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {COLORS.get('error', '#ef4444')}; font-family: 'Roboto Mono'; font-size: 9pt;")
        self.status_label.setWordWrap(True)
        control_layout.addWidget(self.status_label)
        
        control_layout.addStretch()
        
        # Clear Button (Destroyer Archetype)
        clear_btn = QPushButton("PURIFY") # Voice: Clear -> Purify
        clear_btn.clicked.connect(self._clear_all)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS.get('text_secondary', '#94a3b8')};
                border: 1px solid {COLORS.get('ash', '#334155')};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                border-color: {COLORS.get('error', '#ef4444')};
                color: {COLORS.get('error', '#ef4444')};
                background-color: rgba(239, 68, 68, 0.1);
            }}
        """)
        control_layout.addWidget(clear_btn)
        
        card_main_layout.addWidget(control_container, stretch=1)
        
        # Right Side: Glyph
        glyph_container = QWidget()
        glyph_container.setStyleSheet("background: transparent; border: none;")
        glyph_layout = QVBoxLayout(glyph_container)
        
        self.trigram_glyph = TrigramGlyph()
        glyph_layout.addWidget(self.trigram_glyph)
        
        card_main_layout.addWidget(glyph_container, stretch=2)
        
        layout.addWidget(content_card)
        layout.addStretch()
        main_layout.addWidget(content_area)

    def _get_input_style(self):
        return f"""
            QLineEdit {{
                font-family: 'Roboto Mono', monospace;
                font-size: 14pt; 
                padding: 12px;
                background-color: rgba(0, 0, 0, 0.3);
                color: {COLORS.get('gold', '#ffd700')};
                border: 1px solid {COLORS.get('ash', '#334155')};
                border-radius: 8px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS.get('cyan', '#38bdf8')};
                background-color: rgba(0, 0, 0, 0.5);
            }}
            QLineEdit::placeholder {{
                color: rgba(148, 163, 184, 0.3);
            }}
        """

    def _on_decimal_changed(self, text: str):
        self.status_label.clear()
        if not text:
            self.ternary_input.blockSignals(True)
            self.ternary_input.clear()
            self.ternary_input.blockSignals(False)
            return
        try:
            val = int(text)
            if val < 0 or val > 26:
                self.status_label.setText("The vessel holds only 0 to 26.")
                return

            self.trigram_glyph.set_value(val)
            
            ter = self.ternary_service.decimal_to_ternary(val)
            self.ternary_input.blockSignals(True)
            self.ternary_input.setText(ter)
            self.ternary_input.blockSignals(False)
        except ValueError:
            self.status_label.setText("The cipher is flawed (Integers only).")

    def _on_ternary_changed(self, text: str):
        self.status_label.clear()
        if not text:
            self.decimal_input.blockSignals(True)
            self.decimal_input.clear()
            self.decimal_input.blockSignals(False)
            return
        try:
            val = self.ternary_service.ternary_to_decimal(text)
            if val < 0 or val > 26:
                self.status_label.setText("This Pattern is beyond the Grid (0-26 only).")
                return

            self.trigram_glyph.set_value(val)
            
            self.decimal_input.blockSignals(True)
            self.decimal_input.setText(str(val))
            self.decimal_input.blockSignals(False)
        except ValueError:
            self.status_label.setText("The cipher is flawed (Ternary only).")

    def _clear_all(self):
        self.decimal_input.clear()
        self.ternary_input.clear()
        self.status_label.clear()
