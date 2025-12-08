"""Virtual keyboard widget for Hebrew and Greek text input."""
from PyQt6 import sip
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QButtonGroup, QGridLayout, QLabel, QLineEdit, QTextEdit, QLayoutItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, Sequence


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
        self.target_editor: Optional[QTextEdit] = None
        self.shift_active: bool = False
        self.shift_locked: bool = False
        
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
        self.setObjectName("keyboardRoot")
        self.setStyleSheet(
            """
            #keyboardRoot {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #111827, stop:1 #0b1222);
                border: 1px solid #1f2937;
                border-radius: 12px;
            }
            QLabel#titleLabel {
                color: #e5e7eb;
                font-size: 15pt;
                font-weight: 700;
            }
            QLabel#subtitleLabel {
                color: #9ca3af;
                font-size: 9.5pt;
            }
            QPushButton.layoutToggle {
                background-color: #0ea5e9;
                color: #f8fafc;
                border: none;
                border-radius: 8px;
                padding: 10px 14px;
                font-weight: 600;
            }
            QPushButton.layoutToggle:checked {
                background-color: #38bdf8;
            }
            QPushButton.layoutToggle:hover {
                background-color: #28b0f5;
            }
            QPushButton.layoutToggle:pressed {
                background-color: #0ea5e9;
            }
            QPushButton.keyButton {
                background-color: #1f2937;
                color: #e5e7eb;
                border: 1px solid #273449;
                border-radius: 10px;
                padding: 8px;
                font-weight: 600;
                min-width: 46px;
                min-height: 46px;
            }
            QPushButton.keyButton:hover {
                background-color: #243049;
                border-color: #2f3f5c;
            }
            QPushButton.keyButton:pressed {
                background-color: #111827;
                border-color: #1f2937;
            }
            QPushButton.backspaceButton {
                background-color: #111827;
                color: #f8fafc;
                border: 1px solid #273449;
                border-radius: 10px;
                padding: 10px 12px;
                font-weight: 600;
                min-height: 46px;
            }
            QPushButton.backspaceButton:hover {
                background-color: #1f2937;
                border-color: #374151;
            }
            QPushButton.backspaceButton:pressed {
                background-color: #0f172a;
                border-color: #1f2937;
            }
            QPushButton.metaButton {
                background-color: #1f2937;
                color: #e5e7eb;
                border: 1px solid #273449;
                border-radius: 10px;
                padding: 10px 12px;
                font-weight: 600;
                min-height: 46px;
            }
            QPushButton.metaButton:hover {
                background-color: #243049;
                border-color: #2f3f5c;
            }
            QPushButton.metaButton:pressed {
                background-color: #111827;
                border-color: #1f2937;
            }
            """
        )

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(16, 14, 16, 16)

        # Title
        title_row = QVBoxLayout()
        title = QLabel("Virtual Keyboard")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Hebrew • Greek (lower/upper)")
        subtitle.setObjectName("subtitleLabel")
        title_row.addWidget(title)
        title_row.addWidget(subtitle)
        main_layout.addLayout(title_row)

        # Layout selector
        header_layout = QHBoxLayout()
        self.hebrew_btn = QPushButton("Hebrew")
        self.hebrew_btn.setCheckable(True)
        self.hebrew_btn.setChecked(True)
        self.hebrew_btn.setProperty("class", "layoutToggle")
        self.hebrew_btn.clicked.connect(lambda: self._switch_layout("hebrew"))
        header_layout.addWidget(self.hebrew_btn)

        self.greek_btn = QPushButton("Greek")
        self.greek_btn.setCheckable(True)
        self.greek_btn.setProperty("class", "layoutToggle")
        self.greek_btn.clicked.connect(lambda: self._switch_layout("greek"))
        header_layout.addWidget(self.greek_btn)

        self.special_btn = QPushButton("Special")
        self.special_btn.setCheckable(True)
        self.special_btn.setProperty("class", "layoutToggle")
        self.special_btn.clicked.connect(lambda: self._switch_layout("special"))
        header_layout.addWidget(self.special_btn)

        self.esoteric_btn = QPushButton("Esoteric")
        self.esoteric_btn.setCheckable(True)
        self.esoteric_btn.setProperty("class", "layoutToggle")
        self.esoteric_btn.clicked.connect(lambda: self._switch_layout("esoteric"))
        header_layout.addWidget(self.esoteric_btn)

        header_layout.addStretch()

        # Button group for exclusive selection
        self.layout_group = QButtonGroup(self)
        self.layout_group.addButton(self.hebrew_btn)
        self.layout_group.addButton(self.greek_btn)
        self.layout_group.addButton(self.special_btn)
        self.layout_group.addButton(self.esoteric_btn)

        main_layout.addLayout(header_layout)

        # Keyboard grid container
        self.keyboard_container = QWidget()
        self.keyboard_layout = QGridLayout(self.keyboard_container)
        self.keyboard_layout.setSpacing(6)
        main_layout.addWidget(self.keyboard_container)

        # Initially show Hebrew keyboard
        self._show_hebrew_keyboard()

        # Set compact size
        self.setFixedSize(720, 340)
    
    def set_target_input(self, input_field: QLineEdit):
        """
        Set the target input field for this keyboard.
        
        Args:
            input_field: The QLineEdit to send characters to
        """
        self.target_input = input_field
        self.target_editor = None

    def set_target_editor(self, editor: QTextEdit):
        """
        Set the target QTextEdit for this keyboard.

        Args:
            editor: The QTextEdit to send characters to
        """
        self.target_editor = editor
        self.target_input = None
    
    def set_layout(self, layout: str):
        """
        Public method to switch keyboard layout.
        
        Args:
            layout: Layout name ('hebrew', 'greek_lower', 'greek_upper')
        """
        normalized = layout
        # Backward compatibility for old callers
        if layout in ("greek_lower", "greek_upper"):
            normalized = "greek"
            self.shift_locked = layout == "greek_upper"
            self.shift_active = False
        self._switch_layout(normalized)
    
    def _switch_layout(self, layout: str):
        """Switch keyboard layout."""
        self.current_layout = layout
        # Reflect toggle state in header buttons
        if hasattr(self, "hebrew_btn") and hasattr(self, "greek_btn"):
            if layout == "hebrew":
                self.hebrew_btn.setChecked(True)
                self.greek_btn.setChecked(False)
                if hasattr(self, "special_btn"):
                    self.special_btn.setChecked(False)
            elif layout == "greek":
                self.hebrew_btn.setChecked(False)
                self.greek_btn.setChecked(True)
                if hasattr(self, "special_btn"):
                    self.special_btn.setChecked(False)
            elif layout == "special":
                self.hebrew_btn.setChecked(False)
                self.greek_btn.setChecked(False)
                if hasattr(self, "special_btn"):
                    self.special_btn.setChecked(True)
                if hasattr(self, "esoteric_btn"):
                    self.esoteric_btn.setChecked(False)
            elif layout == "esoteric":
                self.hebrew_btn.setChecked(False)
                self.greek_btn.setChecked(False)
                if hasattr(self, "special_btn"):
                    self.special_btn.setChecked(False)
                if hasattr(self, "esoteric_btn"):
                    self.esoteric_btn.setChecked(True)
        if layout != "greek":
            self.shift_active = False
            self.shift_locked = False
        
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
        elif layout == "greek":
            self._show_greek_keyboard()
        elif layout == "special":
            self._show_special_keyboard()
        elif layout == "esoteric":
            self._show_esoteric_keyboard()

    def _display_char(self, char: str) -> str:
        """Return the character as displayed based on current shift state."""
        if self.current_layout == "greek" and (self.shift_active or self.shift_locked):
            return char.upper()
        return char

    def _activate_shift(self):
        """Momentarily enable shift for the next Greek character."""
        if self.current_layout != "greek":
            return
        self.shift_active = True
        self._switch_layout("greek")

    def _toggle_shift_lock(self):
        """Toggle persistent shift for Greek layout."""
        if self.current_layout != "greek":
            return
        self.shift_locked = not self.shift_locked
        # Turning on lock clears momentary shift; turning off clears both
        self.shift_active = False
        sender = self.sender()
        if sender is not None and isinstance(sender, QPushButton):
            try:
                sender.setChecked(self.shift_locked)
            except Exception:
                pass
        self._switch_layout("greek")
    
    def _show_hebrew_keyboard(self):
        """Display Hebrew keyboard in physical layout order."""
        rows = [
            ['ק', 'ר', 'א', 'ט', 'ו', 'ן', 'ם', 'פ'],
            ['ש', 'ד', 'ג', 'כ', 'ע', 'י', 'ח', 'ל', 'ך', 'ף'],
            ['ז', 'ס', 'ב', 'ה', 'נ', 'מ', 'צ', 'ת', 'ץ'],
        ]
        self._render_keyboard(rows, include_shift=False)
    
    def _show_greek_keyboard(self):
        """Display Greek keyboard with shift/lock support for uppercase."""
        rows = [
            ['ς', 'ε', 'ρ', 'τ', 'υ', 'θ', 'ι', 'ο', 'π'],
            ['α', 'σ', 'δ', 'φ', 'γ', 'η', 'ξ', 'κ', 'λ'],
            ['ζ', 'χ', 'ψ', 'ω', 'β', 'ν', 'μ'],
        ]
        self._render_keyboard(rows, include_shift=True)

    def _show_special_keyboard(self):
        """Display special-character keys."""
        rows = [
            ['Å', '<', '>', '→', '↓', '↑'],
            ['×', '°', '∞', '≈', '±', '•']
        ]
        self._render_keyboard(rows, include_shift=False)

    def _show_esoteric_keyboard(self):
        """Display Esoteric symbols (Zodiac, Planets, Elements)."""
        rows = [
            # Zodiac
            ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'],
            # Planets (+ Chiron)
            ['☉', '☾', '☿', '♀', '♂', '♃', '♄', '♅', '♆', '♇', '⚷'],
            # Elements / Alchemy / Misc
            ['🜂', '🜄', '🜁', '🜃', '∞', '∆', '∇', '★', '☆']
        ]
        self._render_keyboard(rows, include_shift=False)
    
    def _render_keyboard(self, rows: Sequence[Sequence[str]], include_shift: bool):
        """Render a keyboard grid with optional shift controls."""
        max_cols = max(len(r) for r in rows) if rows else 0

        for row_idx, row in enumerate(rows):
            for col_idx, char in enumerate(row):
                display = self._display_char(char)
                btn = self._create_char_button(display, display)
                self.keyboard_layout.addWidget(btn, row_idx, col_idx)

        meta_row = len(rows)
        if include_shift:
            shift_btn = QPushButton("Shift")
            shift_btn.setProperty("class", "metaButton")
            shift_btn.clicked.connect(self._activate_shift)
            self.keyboard_layout.addWidget(shift_btn, meta_row, 0)

            lock_btn = QPushButton("Shift Lock")
            lock_btn.setCheckable(True)
            lock_btn.setChecked(self.shift_locked)
            lock_btn.setProperty("class", "metaButton")
            lock_btn.clicked.connect(self._toggle_shift_lock)
            self.keyboard_layout.addWidget(lock_btn, meta_row, 1)

            backspace_btn = QPushButton("⌫")
            backspace_btn.clicked.connect(self._on_backspace)
            backspace_btn.setProperty("class", "backspaceButton")
            cols = max_cols if max_cols > 2 else 3
            self.keyboard_layout.addWidget(backspace_btn, meta_row, cols - 2, 1, 2)
        else:
            backspace_btn = QPushButton("⌫")
            backspace_btn.clicked.connect(self._on_backspace)
            backspace_btn.setProperty("class", "backspaceButton")
            cols = max_cols if max_cols > 2 else 3
            self.keyboard_layout.addWidget(backspace_btn, meta_row, cols - 2, 1, 2)
    
    def _create_char_button(self, label: str, emit_char: str) -> QPushButton:
        """Create a character button."""
        btn = QPushButton(label)
        btn.setMinimumSize(48, 48)
        btn.setMaximumSize(68, 52)
        
        # Set font size for better visibility
        font = QFont()
        font.setPointSize(16)
        btn.setFont(font)
        
        # Connect click to insert character
        btn.clicked.connect(lambda checked, c=emit_char: self._on_char_clicked(c))
        
        # Style
        btn.setProperty("class", "keyButton")
        
        return btn
    
    def _on_char_clicked(self, char: str):
        """Handle character button click."""
        # Emit signal
        self.character_typed.emit(char)
        
        # If target input is set, insert directly
        if self.target_editor:
            cursor = self.target_editor.textCursor()
            cursor.insertText(char)
            self.target_editor.setTextCursor(cursor)
            self.target_editor.setFocus()
        elif self.target_input:
            cursor_pos = self.target_input.cursorPosition()
            current_text = self.target_input.text()
            new_text = current_text[:cursor_pos] + char + current_text[cursor_pos:]
            self.target_input.setText(new_text)
            self.target_input.setCursorPosition(cursor_pos + 1)
            self.target_input.setFocus()

        # If shift was momentary, reset after a single key
        if self.shift_active and not self.shift_locked:
            self.shift_active = False
            if self.current_layout == "greek":
                self._switch_layout("greek")
    
    def _on_backspace(self):
        """Handle backspace button click."""
        # Emit signal
        self.backspace_pressed.emit()
        
        # If target input is set, delete character
        if self.target_editor:
            cursor = self.target_editor.textCursor()
            cursor.deletePreviousChar()
            self.target_editor.setTextCursor(cursor)
            self.target_editor.setFocus()
        elif self.target_input:
            cursor_pos = self.target_input.cursorPosition()
            if cursor_pos > 0:
                current_text = self.target_input.text()
                new_text = current_text[:cursor_pos-1] + current_text[cursor_pos:]
                self.target_input.setText(new_text)
                self.target_input.setCursorPosition(cursor_pos - 1)
                self.target_input.setFocus()


_shared_virtual_keyboard: Optional[VirtualKeyboard] = None


def get_shared_virtual_keyboard(parent: Optional[QWidget] = None) -> VirtualKeyboard:
    """Return a singleton virtual keyboard instance, reparenting it if needed."""
    global _shared_virtual_keyboard
    needs_new = (
        _shared_virtual_keyboard is None or sip.isdeleted(_shared_virtual_keyboard)
    )
    if needs_new:
        _shared_virtual_keyboard = VirtualKeyboard(parent)
    elif parent is not None and _shared_virtual_keyboard.parent() is not parent:
        _shared_virtual_keyboard.setParent(parent)
    return _shared_virtual_keyboard
