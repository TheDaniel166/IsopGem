"""Virtual keyboard widget for Hebrew and Greek text input."""
from PyQt6 import sip
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QButtonGroup, QGridLayout, QLabel, QLineEdit, QTextEdit, QLayoutItem,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPalette
from typing import Optional, List

from .keyboard_layouts import LAYOUTS, KeyboardLayout


class VirtualKeyboard(QDialog):
    """Virtual keyboard window for Hebrew and Greek character input."""
    
    character_typed = pyqtSignal(str)
    backspace_pressed = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the virtual keyboard."""
        super().__init__(parent)
        self.current_layout_name = "hebrew"
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
        
        # Modern Dark Theme (Slate/Zinc Palette)
        self.setStyleSheet(
            """
            #keyboardRoot {
                background-color: #0f172a; /* Slate 900 */
                border: 1px solid #334155; /* Slate 700 */
                border-radius: 16px;
            }
            QLabel#titleLabel {
                color: #f1f5f9; /* Slate 100 */
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 16pt;
                font-weight: 700;
            }
            QLabel#subtitleLabel {
                color: #94a3b8; /* Slate 400 */
                font-size: 10pt;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            
            /* Layout Toggle Group */
            QFrame#toggleContainer {
                background-color: #1e293b; /* Slate 800 */
                border-radius: 8px;
                padding: 4px;
            }
            QPushButton.layoutToggle {
                background-color: transparent;
                color: #94a3b8;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton.layoutToggle:checked {
                background-color: #38bdf8; /* Sky 400 */
                color: #0f172a;
            }
            QPushButton.layoutToggle:hover:!checked {
                background-color: #334155; /* Slate 700 */
                color: #e2e8f0;
            }
            
            /* Keys */
            QPushButton.keyButton {
                background-color: #1e293b; /* Slate 800 */
                color: #e2e8f0; /* Slate 200 */
                border: 1px solid #334155; /* Slate 700 */
                border-bottom: 3px solid #0f172a; /* Tactile depth */
                border-radius: 8px;
                font-weight: 500;
                font-family: 'Segoe UI', 'David', 'SBL Greek', sans-serif;
            }
            QPushButton.keyButton:hover {
                background-color: #334155; /* Slate 700 */
                border-color: #475569;
                margin-top: -1px; /* Lift effect */
                border-bottom-width: 4px;
            }
            QPushButton.keyButton:pressed {
                background-color: #0f172a;
                border: 1px solid #334155;
                margin-top: 2px;
                border-bottom-width: 1px;
            }
            
            /* Control Keys */
            QPushButton.controlButton {
                background-color: #334155; /* Slate 700 */
                color: #f8fafc;
                border: 1px solid #475569;
                border-bottom: 3px solid #1e293b;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton.controlButton:checked {
                background-color: #f59e0b; /* Amber 500 for Lock */
                color: #000;
                border-color: #d97706;
            }
            QPushButton.controlButton:pressed {
                margin-top: 2px;
                border-bottom-width: 1px;
            }
            QPushButton.backspaceButton {
                background-color: #ef4444; /* Red 500 */
                color: white;
                border: 1px solid #dc2626;
                border-bottom: 3px solid #991b1b;
                border-radius: 8px;
                font-weight: 900;
            }
            QPushButton.backspaceButton:pressed {
                margin-top: 2px;
                border-bottom-width: 1px;
            }
            """
        )

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header Section
        header = QHBoxLayout()
        titles = QVBoxLayout()
        title = QLabel("Virtual Keyboard")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Select a layout to begin")
        subtitle.setObjectName("subtitleLabel")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header.addLayout(titles)
        header.addStretch()
        main_layout.addLayout(header)

        # Layout Switcher (Segmented Control style)
        self.toggle_container = QFrame()
        self.toggle_container.setObjectName("toggleContainer")
        toggle_layout = QHBoxLayout(self.toggle_container)
        toggle_layout.setContentsMargins(4, 4, 4, 4)
        toggle_layout.setSpacing(4)
        
        self.layout_group = QButtonGroup(self)
        self.layout_buttons = {}
        
        # Create buttons dynamically from generic definitions + Esoteric
        # We manually order them for UX consistency: Hebrew, Greek, Special, Esoteric
        layout_order = ["hebrew", "greek", "special", "esoteric"]
        
        for layout_id in layout_order:
            if layout_id not in LAYOUTS: continue
            
            layout_def = LAYOUTS[layout_id]
            btn = QPushButton(layout_def.display_name)
            btn.setCheckable(True)
            btn.setProperty("class", "layoutToggle")
            btn.clicked.connect(lambda checked, lid=layout_id: self._switch_layout(lid))
            
            self.layout_group.addButton(btn)
            self.layout_buttons[layout_id] = btn
            toggle_layout.addWidget(btn)
            
        main_layout.addWidget(self.toggle_container)

        # Keyboard Grid
        self.keyboard_container = QWidget()
        self.keyboard_layout = QGridLayout(self.keyboard_container)
        self.keyboard_layout.setSpacing(8)
        self.keyboard_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.keyboard_container)

        # Initial State
        self._switch_layout("hebrew")
        self.layout_buttons["hebrew"].setChecked(True)
        
        # Resize logic
        self.setFixedSize(760, 400)

    def set_target_input(self, input_field: QLineEdit):
        self.target_input = input_field
        self.target_editor = None

    def set_target_editor(self, editor: QTextEdit):
        self.target_editor = editor
        self.target_input = None
        
    def set_layout(self, layout: str):
        """Public method to force switch layout (e.g. from external menu)."""
        normalized = layout
        # Validation and mapping
        if layout == "greek_lower": normalized = "greek"
        if layout == "greek_upper": 
            normalized = "greek"
            self.shift_locked = True
        
        if normalized in LAYOUTS:
            self._switch_layout(normalized)
            if normalized in self.layout_buttons:
                self.layout_buttons[normalized].setChecked(True)

    def _switch_layout(self, layout_name: str):
        """Switch the current keyboard layout."""
        if layout_name not in LAYOUTS:
            return
            
        self.current_layout_name = layout_name
        layout_def = LAYOUTS[layout_name]
        
        # Reset shift states if switching away from a layout that needs them
        if not layout_def.has_shift:
            self.shift_active = False
            self.shift_locked = False
            
        self._render_keyboard(layout_def)
        
        # Update subtitle
        sub = self.findChild(QLabel, "subtitleLabel")
        if sub:
            sub.setText(f"Active Layout: {layout_def.display_name}")

    def _render_keyboard(self, layout: KeyboardLayout):
        """Render the keys for the given layout definition."""
        # Clear existing
        while self.keyboard_layout.count():
            item = self.keyboard_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Calculate grid size (optional optimization, QGrid does it automatically)
        max_cols = max(len(r) for r in layout.rows) if layout.rows else 10
        
        # Render Rows
        for r_idx, row in enumerate(layout.rows):
            for c_idx, char in enumerate(row):
                display_char = self._get_display_char(char, layout)
                btn = self._create_key_button(display_char, display_char)
                self.keyboard_layout.addWidget(btn, r_idx, c_idx)
                
        # Render Control Row (Shift, Space, Backspace)
        control_row = len(layout.rows)
        
        if layout.has_shift:
            shift_btn = QPushButton("⇧ Shift")
            shift_btn.setProperty("class", "controlButton")
            shift_btn.clicked.connect(self._activate_shift)
            if self.shift_active:
                shift_btn.setDown(True)
            self.keyboard_layout.addWidget(shift_btn, control_row, 0, 1, 2)
            
            lock_btn = QPushButton("⇪ Lock")
            lock_btn.setCheckable(True)
            lock_btn.setChecked(self.shift_locked)
            lock_btn.setProperty("class", "controlButton")
            lock_btn.clicked.connect(self._toggle_shift_lock)
            self.keyboard_layout.addWidget(lock_btn, control_row, 2, 1, 2)
            
            # Spacer
            
            backspace_btn = QPushButton("⌫ Backspace")
            backspace_btn.setProperty("class", "backspaceButton")
            backspace_btn.clicked.connect(self._on_backspace)
            self.keyboard_layout.addWidget(backspace_btn, control_row, max_cols-3, 1, 3)
            
        else:
            # Simple control row for non-shift layouts
            
            # Maybe add a Space button? (Optional, not previously present but useful)
            space_btn = QPushButton("Space")
            space_btn.setProperty("class", "controlButton")
            space_btn.clicked.connect(lambda: self._on_char_clicked(" "))
            self.keyboard_layout.addWidget(space_btn, control_row, 0, 1, 2)
            
            backspace_btn = QPushButton("⌫ Backspace")
            backspace_btn.setProperty("class", "backspaceButton")
            backspace_btn.clicked.connect(self._on_backspace)
            self.keyboard_layout.addWidget(backspace_btn, control_row, max_cols-3, 1, 3)

    def _get_display_char(self, char: str, layout: KeyboardLayout) -> str:
        if layout.has_shift and (self.shift_active or self.shift_locked):
            return char.upper()
        return char

    def _create_key_button(self, label: str, value: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setMinimumSize(52, 52) # Bigger targets
        btn.setSizePolicy(
            btn.sizePolicy().horizontalPolicy(), 
            btn.sizePolicy().verticalPolicy()
        )
        
        # Dynamic font sizing
        font = QFont("Segoe UI", 14)
        if len(label) > 1: # Icons or special chars
            font.setPointSize(12)
        btn.setFont(font)
        
        btn.setProperty("class", "keyButton")
        btn.clicked.connect(lambda checked, v=value: self._on_char_clicked(v))
        return btn

    def _activate_shift(self):
        self.shift_active = True
        # Re-render to show uppercase keys
        self._switch_layout(self.current_layout_name)

    def _toggle_shift_lock(self):
        self.shift_locked = not self.shift_locked
        self.shift_active = False # Lock overrides momentary
        self._switch_layout(self.current_layout_name)

    def _on_char_clicked(self, char: str):
        self.character_typed.emit(char)
        
        if self.target_editor:
            self.target_editor.insertPlainText(char)
            self.target_editor.ensureCursorVisible()
            self.target_editor.setFocus()
        elif self.target_input:
            self.target_input.insert(char)
            self.target_input.setFocus()
            
        # Handle momentary shift interaction
        if self.shift_active and not self.shift_locked:
            self.shift_active = False
            self._switch_layout(self.current_layout_name)

    def _on_backspace(self):
        self.backspace_pressed.emit()
        
        if self.target_editor:
            self.target_editor.textCursor().deletePreviousChar()
            self.target_editor.setFocus()
        elif self.target_input:
            self.target_input.backspace()
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
