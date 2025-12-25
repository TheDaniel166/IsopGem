"""Special characters dialog for Rich Text Editor."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QPushButton,
    QLabel, QTabWidget, QScrollArea, QWidget
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal


class SpecialCharactersDialog(QDialog):
    """Dialog for inserting special characters and symbols."""
    
    CATEGORIES = {
        "Common": "© ® ™ § ¶ † ‡ • ° ± × ÷ ≠ ≤ ≥ ≈ ∞ √ ← → ↑ ↓ ↔",
        "Currency": "$ € £ ¥ ¢ ₹ ₽ ₿ ₩ ₪ ฿",
        "Greek": "Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω",
        "Math": "+ − × ÷ = ≠ < > ≤ ≥ ± ∞ √ ∑ ∏ ∫ ∂ ∇ ∈ ∉ ⊂ ⊃ ∪ ∩ ∧ ∨ ¬",
        "Fractions": "½ ⅓ ⅔ ¼ ¾ ⅕ ⅖ ⅗ ⅘ ⅙ ⅚ ⅛ ⅜ ⅝ ⅞",
        "Super/Sub": "⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹ ⁺ ⁻ ⁿ ₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉",
        "Arrows": "← → ↑ ↓ ↔ ↕ ⇐ ⇒ ⇑ ⇓ ⇔ ➔ ➜ ➡ ➢",
        "Shapes": "■ □ ▢ ▲ △ ▼ ▽ ◆ ◇ ○ ● ◐ ◑ ★ ☆",
        "Zodiac": "♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓",
        "Planets": "☉ ☽ ☿ ♀ ♁ ♂ ♃ ♄ ♅ ♆",
        "Music": "♩ ♪ ♫ ♬ ♭ ♮ ♯",
        "Cards": "♠ ♡ ♢ ♣ ♤ ♥ ♦ ♧",
        "Misc": "☀ ☁ ☂ ☃ ☄ ★ ☆ ☎ ☐ ☑ ☒ ☮ ☯ ☸ ☹ ☺ ☻ ☼ ☽ ☾ ♀ ♂",
    }
    
    char_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Special Characters")
        self.setMinimumSize(450, 350)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        for category, chars in self.CATEGORIES.items():
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            
            container = QWidget()
            grid = QGridLayout(container)
            grid.setSpacing(2)
            
            char_list = chars.split()
            cols = 10
            for i, char in enumerate(char_list):
                btn = QPushButton(char)
                btn.setFixedSize(32, 32)
                btn.setFont(QFont("Segoe UI Symbol", 12))
                btn.clicked.connect(lambda checked, c=char: self._on_char_clicked(c))
                grid.addWidget(btn, i // cols, i % cols)
            
            scroll.setWidget(container)
            self.tabs.addTab(scroll, category)
        
        layout.addWidget(self.tabs)
        
        self.selected_label = QLabel("Click a character to insert")
        layout.addWidget(self.selected_label)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def _on_char_clicked(self, char: str):
        self.selected_label.setText(f"Inserted: {char}")
        self.char_selected.emit(char)
