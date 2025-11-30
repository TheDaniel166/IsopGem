"""Virtual keyboard widget for Hebrew and Greek text input."""
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QButtonGroup, QGridLayout, QLabel, QLineEdit, QLayoutItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional


class VirtualKeyboard(QDialog):
    """Virtual keyboard window for Hebrew and Greek character input."""
    
    # Signal emitted when a character is typed
    character_typed = pyqtSignal(str)
    
    # Signal emitted when backspace is pressed
    backspace_pressed = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the virtual keyboard."""
        super().__init__(parent)
        self.current_layout = "hebrew"  # hebrew, greek_lower, greek_upper
        self.target_input: Optional[QLineEdit] = None
        
        # Dialog settings
        self.setWindowTitle("Virtual Keyboard")
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.setModal(False)
        self.setWindowFlags(
            Qt.WindowType.Tool | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the keyboard interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Layout selector
        header_layout = QHBoxLayout()
        
        # Layout selector buttons
        self.hebrew_btn = QPushButton("Hebrew")
        self.hebrew_btn.setCheckable(True)
        self.hebrew_btn.setChecked(True)
        self.hebrew_btn.clicked.connect(lambda: self._switch_layout("hebrew"))
        header_layout.addWidget(self.hebrew_btn)
        
        self.greek_lower_btn = QPushButton("Greek α")
        self.greek_lower_btn.setCheckable(True)
        self.greek_lower_btn.clicked.connect(lambda: self._switch_layout("greek_lower"))
        header_layout.addWidget(self.greek_lower_btn)
        
        self.greek_upper_btn = QPushButton("Greek Α")
        self.greek_upper_btn.setCheckable(True)
        self.greek_upper_btn.clicked.connect(lambda: self._switch_layout("greek_upper"))
        header_layout.addWidget(self.greek_upper_btn)
        
        # Button group for exclusive selection
        self.layout_group = QButtonGroup(self)
        self.layout_group.addButton(self.hebrew_btn)
        self.layout_group.addButton(self.greek_lower_btn)
        self.layout_group.addButton(self.greek_upper_btn)
        
        main_layout.addLayout(header_layout)
        
        # Keyboard grid container
        self.keyboard_container = QWidget()
        self.keyboard_layout = QGridLayout(self.keyboard_container)
        self.keyboard_layout.setSpacing(3)
        main_layout.addWidget(self.keyboard_container)
        
        # Initially show Hebrew keyboard
        self._show_hebrew_keyboard()
        
        # Set compact size
        self.setFixedSize(600, 250)
    
    def set_target_input(self, input_field: QLineEdit):
        """
        Set the target input field for this keyboard.
        
        Args:
            input_field: The QLineEdit to send characters to
        """
        self.target_input = input_field
    
    def set_layout(self, layout: str):
        """
        Public method to switch keyboard layout.
        
        Args:
            layout: Layout name ('hebrew', 'greek_lower', 'greek_upper')
        """
        self._switch_layout(layout)
    
    def _switch_layout(self, layout: str):
        """Switch keyboard layout."""
        self.current_layout = layout
        
        # Clear existing keyboard
        while self.keyboard_layout.count():
            item: QLayoutItem | None = self.keyboard_layout.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # Show appropriate keyboard
        if layout == "hebrew":
            self._show_hebrew_keyboard()
        elif layout == "greek_lower":
            self._show_greek_keyboard(lowercase=True)
        elif layout == "greek_upper":
            self._show_greek_keyboard(lowercase=False)
    
    def _show_hebrew_keyboard(self):
        """Display Hebrew keyboard layout."""
        # Hebrew letters in logical order
        hebrew_letters = [
            # Row 1: Regular letters
            ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט'],
            # Row 2: More letters
            ['י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ'],
            # Row 3: Final letters and last letters
            ['ק', 'ר', 'ש', 'ת', '|', 'ך', 'ם', 'ן', 'ף', 'ץ'],
        ]
        
        # Create buttons
        for row_idx, row in enumerate(hebrew_letters):
            for col_idx, char in enumerate(row):
                if char == '|':
                    # Separator/spacer
                    continue
                btn = self._create_char_button(char)
                self.keyboard_layout.addWidget(btn, row_idx, col_idx)
        
        # Add backspace button spanning last row
        backspace_btn = QPushButton("⌫ Backspace")
        backspace_btn.clicked.connect(self._on_backspace)
        backspace_btn.setMinimumHeight(35)
        self.keyboard_layout.addWidget(backspace_btn, 3, 0, 1, 10)
    
    def _show_greek_keyboard(self, lowercase: bool = True):
        """Display Greek keyboard layout."""
        if lowercase:
            # Greek lowercase letters
            greek_letters = [
                # Row 1
                ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ'],
                # Row 2
                ['ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π'],
                # Row 3
                ['ρ', 'σ', 'ς', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω'],
            ]
        else:
            # Greek uppercase letters
            greek_letters = [
                # Row 1
                ['Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ'],
                # Row 2
                ['Ι', 'Κ', 'Λ', 'Μ', 'Ν', 'Ξ', 'Ο', 'Π'],
                # Row 3
                ['Ρ', 'Σ', 'Τ', 'Υ', 'Φ', 'Χ', 'Ψ', 'Ω'],
            ]
        
        # Create buttons
        for row_idx, row in enumerate(greek_letters):
            for col_idx, char in enumerate(row):
                btn = self._create_char_button(char)
                self.keyboard_layout.addWidget(btn, row_idx, col_idx)
        
        # Add backspace button spanning last row
        backspace_btn = QPushButton("⌫ Backspace")
        backspace_btn.clicked.connect(self._on_backspace)
        backspace_btn.setMinimumHeight(35)
        self.keyboard_layout.addWidget(backspace_btn, 3, 0, 1, 9)
    
    def _create_char_button(self, char: str) -> QPushButton:
        """Create a character button."""
        btn = QPushButton(char)
        btn.setMinimumSize(40, 40)
        btn.setMaximumSize(60, 40)
        
        # Set font size for better visibility
        font = QFont()
        font.setPointSize(14)
        btn.setFont(font)
        
        # Connect click to insert character
        btn.clicked.connect(lambda checked, c=char: self._on_char_clicked(c))
        
        # Style
        btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                color: #000000;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
                color: #000000;
            }
        """)
        
        return btn
    
    def _on_char_clicked(self, char: str):
        """Handle character button click."""
        # Emit signal
        self.character_typed.emit(char)
        
        # If target input is set, insert directly
        if self.target_input:
            cursor_pos = self.target_input.cursorPosition()
            current_text = self.target_input.text()
            new_text = current_text[:cursor_pos] + char + current_text[cursor_pos:]
            self.target_input.setText(new_text)
            self.target_input.setCursorPosition(cursor_pos + 1)
            self.target_input.setFocus()
    
    def _on_backspace(self):
        """Handle backspace button click."""
        # Emit signal
        self.backspace_pressed.emit()
        
        # If target input is set, delete character
        if self.target_input:
            cursor_pos = self.target_input.cursorPosition()
            if cursor_pos > 0:
                current_text = self.target_input.text()
                new_text = current_text[:cursor_pos-1] + current_text[cursor_pos:]
                self.target_input.setText(new_text)
                self.target_input.setCursorPosition(cursor_pos - 1)
                self.target_input.setFocus()
