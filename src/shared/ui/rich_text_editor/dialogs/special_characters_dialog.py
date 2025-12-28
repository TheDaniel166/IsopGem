"""
Special Characters Dialog - The Symbol Palette.
Dialog for inserting Hebrew, Greek, alchemical, occult, and mathematical symbols.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QPushButton,
    QLabel, QScrollArea, QWidget, QHBoxLayout,
    QListWidget, QStackedWidget, QListWidgetItem
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal, Qt


class SpecialCharactersDialog(QDialog):
    """Dialog for inserting special characters and symbols."""
    
    CATEGORIES = {
        "Hebrew": "א ב ג ד ה ו ז ח ט י כ ך ל מ ם נ ן ס ע פ ף צ ץ ק ר ש ת",
        "Greek": "Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω Ϛ ϛ Ϝ ϝ Ϟ ϟ Ϡ ϡ",
        "Alchemy": "🜁 🜂 🜃 🜄 🜔 🜕 🜖 🜗 🜘 🜙 🜚 🜛 🜜 🜝 🜞 🜟 🜠 🜡 🜢 🜣 🜤 🜥 🝀 🝁 🝂 🝃 🝄 🝅 🝆 🝇 🝈 🝉 🝊 🝋 🝌 🝍 🝎 🝏 🝐 🝑",
        "Occult": "☥ ☧ ☨ ☩ ☪ ☫ ☬ ☭ ☮ ☯ ☸ ☹ ☺ ☻ ☼ ☽ ☾ ✆ ✝ ✞ ✟ ✠ ✡ ✦ ✧ ✩ ✪ ✫ ✬ ✭ ✮ ✯ ✰ ⁂ ⁎ ⁑",
        "Planets": "☉ ☽ ☿ ♀ ♁ ♂ ♃ ♄ ♅ ♆ ♇ ⚳ ⚴ ⚵ ⚶ ⚷ ⚸ ⚹ ⚺ ⚻ ⚼",
        "Zodiac": "♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓ ⛎",
        "Math (Logic)": "∀ ∃ ∄ ∅ ∆ ∇ ∈ ∉ ∋ ∌ ∏ ∐ ∑ − ∓ ∔ ∕ ∖ ∗ ∘ ∙ √ ∛ ∜ ∝ ∞ ∟ ∠ ∡ ∢ ∣ ∤ ∥ ∦ ∧ ∨ ∩ ∪ ∫ ∬ ∭ ∮ ∯ ∰ ∱ ∲ ∳",
        "Math (Relations)": "∴ ∵ ∶ ∷ ∸ ∹ ∺ ∻ ∼ ∽ ∾ ∿ ≀ ≁ ≂ ≃ ≄ ≅ ≆ ≇ ≈ ≉ ≊ ≋ ≌ ≍ ≎ ≏ ≐ ≑ ≒ ≓ ≔ ≕ ≖ ≗ ≘ ≙ ≚ ≛ ≜ ≝ ≞ ≟ ≠ ≡ ≢ ≣ ≤ ≥ ≦ ≧ ≨ ≩ ≪ ≫ ≬ ≭ ≮ ≯",
        "Common": "© ® ™ § ¶ † ‡ • ° ± × ÷ ≠ ≤ ≥ ≈ ∞ √ ← → ↑ ↓ ↔",
        "Currency": "$ € £ ¥ ¢ ₹ ₽ ₿ ₩ ₪ ฿ ₠ ₡ ₢ ₣ ₤ ₥ ₦ ₧ ₨ ₩ ₪ ₫ € ₭ ₮ ₯ ₰ ₱ ₲ ₳ ₴ ₵",
        "Arrows": "← → ↑ ↓ ↔ ↕ ⇐ ⇒ ⇑ ⇓ ⇔ ➔ ➜ ➡ ➢ ➣ ➤ ➥ ➦ ➧ ➨ ➩ ➪ ➫ ➬ ➭ ➮ ➯ ➱ ➲ ➳ ➴ ➵ ➶ ➷ ➸ ➹ ➺ ➻ ➼ ➽",
        "Shapes": "■ □ ▢ ▲ △ ▼ ▽ ◆ ◇ ○ ● ◐ ◑ ★ ☆ ♠ ♡ ♢ ♣ ♤ ♥ ♦ ♧ ♙ ♘ ♗ ♖ ♕ ♔ ♟ ♞ ♝ ♜ ♛ ♚",
        "Music": "♩ ♪ ♫ ♬ ♭ ♮ ♯",
    }
    
    char_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Insert Special Character")
        self.setMinimumSize(800, 550) # Increased width for sidebar
        self.setStyleSheet("""
            QDialog {
                background-color: #0f172a; /* Void Slate */
            }
            QListWidget {
                background-color: #1e293b; /* Stone */
                border-right: 1px solid #334155;
                outline: none;
                font-family: 'Inter';
                font-size: 11pt;
            }
            QListWidget::item {
                padding: 12px 16px;
                color: #94a3b8;
                border-bottom: 1px solid #334155;
            }
            QListWidget::item:selected {
                background-color: #3b82f6; /* Electric Blue */
                color: #f8fafc;
            }
            QListWidget::item:hover {
                background-color: #334155;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QWidget {
                background-color: #0f172a;
                color: #f8fafc;
            }
            QPushButton {
                background-color: #334155;
                color: #f8fafc;
                border: 1px solid #475569;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #475569;
                border: 1px solid #64748b;
            }
            QLabel {
                color: #94a3b8;
                font-size: 11pt;
            }
        """)
        self._setup_ui()
    
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Body (Sidebar + Content) ---
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setSpacing(0)
        body_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. Sidebar (Categories)
        self.category_list = QListWidget()
        self.category_list.setFixedWidth(180)
        self.category_list.currentRowChanged.connect(self._on_category_changed)
        
        # 2. Content Stack
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #0f172a;")
        
        # Populate Categories
        for category, chars in self.CATEGORIES.items():
            # Add to Sidebar
            item = QListWidgetItem(category)
            self.category_list.addItem(item)
            
            # Add to Stack
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(20, 20, 20, 20)
            
            # Title for context
            title = QLabel(category)
            title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #f8fafc; margin-bottom: 10px;")
            page_layout.addWidget(title)
            
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            
            container = QWidget()
            container.setStyleSheet("background: transparent;")
            
            grid = QGridLayout(container)
            grid.setSpacing(10)
            grid.setContentsMargins(0, 0, 0, 0)
            
            char_list = chars.split()
            cols = 8
            
            for i, char in enumerate(char_list):
                btn = QPushButton(char)
                btn.setFixedSize(52, 52) 
                btn.setFont(QFont("Segoe UI Symbol", 24))
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda checked, c=char: self._on_char_clicked(c))
                grid.addWidget(btn, i // cols, i % cols)
            
            # Push to top-left alignment
            grid.setRowStretch(grid.rowCount(), 1)
            grid.setColumnStretch(grid.columnCount(), 1)
            
            scroll.setWidget(container)
            page_layout.addWidget(scroll)
            
            self.stack.addWidget(page)
        
        body_layout.addWidget(self.category_list)
        body_layout.addWidget(self.stack)
        
        main_layout.addWidget(body_widget)
        
        # --- Footer ---
        footer_container = QWidget()
        footer_container.setStyleSheet("background-color: #1e293b; border-top: 1px solid #334155;")
        footer_layout = QHBoxLayout(footer_container)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        
        self.selected_label = QLabel("Click a symbol to insert...")
        self.selected_label.setStyleSheet("color: #3b82f6; font-weight: bold; font-size: 11pt;")
        footer_layout.addWidget(self.selected_label)
        
        footer_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(100, 36)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444; 
                color: white; 
                border: none;
                font-weight: 600;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #dc2626; }
        """)
        close_btn.clicked.connect(self.close)
        footer_layout.addWidget(close_btn)
        
        main_layout.addWidget(footer_container)
        
        # Select first category
        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)
    
    def _on_category_changed(self, row):
        self.stack.setCurrentIndex(row)
    
    def _on_char_clicked(self, char: str):
        self.selected_label.setText(f"Inserted: {char}")
        self.char_selected.emit(char)
        # Optional: Auto-close? For now keep open for multiple inserts.
