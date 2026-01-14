"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: GRANDFATHERED - Needs manual review
- USED BY: Correspondences, Gematria (6 references)
- CRITERION: Unknown - requires categorization

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""


"""Virtual keyboard widget for Hebrew and Greek text input."""
from PyQt6 import sip
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QButtonGroup, QGridLayout, QLabel, QLineEdit, QTextEdit, QLayoutItem,
    QFrame, QGraphicsDropShadowEffect
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
            Qt.WindowType.FramelessWindowHint  # Visual Liturgy: Custom "Floating Temple"
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # For shadows
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the keyboard interface."""
        self.setObjectName("keyboardRoot")
        
        # Visual Liturgy v2.2 - Dark Mode Implementation
        # The Tablet (Void Slate), The Vessel (Stone), The Magus (Violet), The Seeker (Gold)
        self.setStyleSheet(
            """
            /* The Tablet (Window Container) */
            QFrame#MainTablet {
                background-color: #0f172a; /* Void Slate */
                border: 1px solid #334155; /* Dark Ash */
                border-radius: 24px;
            }
            
            /* Typography */
            QLabel#titleLabel {
                color: #f8fafc; /* Cloud */
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 14pt; /* The Header */
                font-weight: 800;
            }
            QLabel#subtitleLabel {
                color: #94a3b8; /* Mist */
                font-size: 10pt; /* The Whisper */
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-weight: 500;
            }
            
            /* Layout Toggle - "The Segmented Control" */
            QFrame#toggleContainer {
                background-color: #1e293b; /* Stone */
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 2px;
            }
            QPushButton.layoutToggle {
                background-color: transparent;
                color: #94a3b8;
                border: none;
                border-radius: 10px;
                padding: 6px 12px;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
            }
            QPushButton.layoutToggle:checked {
                background-color: #334155; /* Active state - lighter stone */
                color: #f8fafc;
                border: 1px solid #475569;
            }
            QPushButton.layoutToggle:hover:!checked {
                color: #e2e8f0;
            }
            
            /* Keys - "The Vessel" / "Stone" */
            QPushButton.keyButton {
                background-color: #1e293b; /* Stone */
                color: #f8fafc; /* Cloud */
                border: 1px solid #334155; /* Ash */
                border-bottom: 3px solid #0f172a; /* Tactile depth */
                border-radius: 12px;
                font-weight: 500;
                font-size: 14pt; /* The Command */
            }
            QPushButton.keyButton:hover {
                background-color: #334155; /* Lighter Stone */
                border-color: #475569;
                margin-top: -1px;
                border-bottom-width: 4px;
            }
            QPushButton.keyButton:pressed {
                background-color: #0f172a;
                border-top: 2px solid #020617;
                border-bottom-width: 1px;
                margin-top: 2px;
            }
            
            /* Control Keys - "The Navigator" (Shift/Lock) */
            QPushButton.controlButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #64748b, stop:1 #475569); /* Void Slate Gradient */
                color: white;
                border: 1px solid #334155;
                border-bottom: 3px solid #1e293b;
                border-radius: 12px;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
            }
            QPushButton.controlButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #94a3b8, stop:1 #64748b);
            }
            QPushButton.controlButton:checked {
                /* "The Seeker" - Active/Locked State */
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:1 #f59e0b);
                color: #020617;
                border: 1px solid #d97706;
            }
            QPushButton.controlButton:pressed {
                background: #475569;
                margin-top: 2px;
                border-bottom-width: 1px;
            }
            
            /* Backspace - "The Destroyer" */
            QPushButton.backspaceButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #b91c1c); /* Crimson */
                color: white;
                border: 1px solid #991b1b;
                border-bottom: 3px solid #7f1d1d;
                border-radius: 12px;
                font-weight: 700;
            }
            QPushButton.backspaceButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f87171, stop:1 #ef4444);
            }
            QPushButton.backspaceButton:pressed {
                background: #b91c1c;
                margin-top: 2px;
                border-bottom-width: 1px;
            }

            /* Close Button - "The Exit" */
            QPushButton#closeButton {
                background: #334155; /* Visible background (Stone) */
                color: #f8fafc; /* Cloud */
                border: 1px solid #475569;
                border-radius: 16px;
                font-weight: 900;
                font-size: 14px;
            }
            QPushButton#closeButton:hover {
                background: #ef4444; /* Crimson */
                color: white;
                border: 1px solid #b91c1c;
            }
            """
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # The Tablet Frame (Holds existing content)
        self.tablet_frame = QFrame()
        self.tablet_frame.setObjectName("MainTablet")
        
        # Add Drop Shadow (The Floating Temple)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 40)) # 15%ish opacity
        self.tablet_frame.setGraphicsEffect(shadow)
        
        main_layout.addWidget(self.tablet_frame)
        
        # Tablet Layout
        tablet_layout = QVBoxLayout(self.tablet_frame)
        tablet_layout.setSpacing(20)
        tablet_layout.setContentsMargins(24, 24, 24, 24)

        # Header Section (Spread layout: Toggles Left, Close Right)
        header = QHBoxLayout()
        
        # Layout Switcher (Segmented Control style)
        self.toggle_container = QFrame()
        self.toggle_container.setObjectName("toggleContainer")
        toggle_layout = QHBoxLayout(self.toggle_container)
        toggle_layout.setContentsMargins(2, 2, 2, 2)
        toggle_layout.setSpacing(0) 
        
        self.layout_group = QButtonGroup(self)
        self.layout_buttons = {}
        
        # Updated Order v2.4
        layout_order = ["hebrew", "greek", "arabic", "sanskrit", "trigrammaton", "astronomicon", "special", "esoteric"]
        
        for layout_id in layout_order:
            if layout_id not in LAYOUTS: continue
            
            layout_def = LAYOUTS[layout_id]
            # Shorten display names if needed for space
            display = layout_def.display_name
            if layout_id == "trigrammaton": display = "Trigram"
            if layout_id == "astronomicon": display = "Astro"
            
            btn = QPushButton(display)
            btn.setCheckable(True)
            btn.setProperty("class", "layoutToggle")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, lid=layout_id: self._switch_layout(lid))
            
            self.layout_group.addButton(btn)
            self.layout_buttons[layout_id] = btn
            toggle_layout.addWidget(btn)
            
        header.addWidget(self.toggle_container)
        header.addStretch() # Push Close button to right
        
        # Add a small spacer before close button
        header.addSpacing(16)

        # Close Button (The EXIT)
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeButton")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        header.addWidget(close_btn)

        tablet_layout.addLayout(header)

        # Keyboard Grid
        self.keyboard_container = QWidget()
        self.keyboard_layout = QGridLayout(self.keyboard_container)
        self.keyboard_layout.setSpacing(6) # Tighter spacing
        self.keyboard_layout.setContentsMargins(0, 4, 0, 0)
        tablet_layout.addWidget(self.keyboard_container)

        # Initial State
        self._switch_layout("hebrew")
        self.layout_buttons["hebrew"].setChecked(True)
        
        # Resize logic - Compact Mode (Wider for more tabs)
        self.setFixedSize(680, 360) 

    def set_target_input(self, input_field: QLineEdit):
        """
        Configure target input logic.
        
        Args:
            input_field: Description of input_field.
        
        """
        self.target_input = input_field
        self.target_editor = None

    def set_target_editor(self, editor: QTextEdit):
        """
        Configure target editor logic.
        
        Args:
            editor: Description of editor.
        
        """
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
                # Pass layout to create_key_button to access font family
                btn = self._create_key_button(display_char, display_char, layout)
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

    def _create_key_button(self, label: str, value: str, layout: KeyboardLayout = None) -> QPushButton:
        btn = QPushButton(label)
        btn.setMinimumSize(42, 42) # Compact Mode (The Pebble)
        btn.setSizePolicy(
            btn.sizePolicy().horizontalPolicy(), 
            btn.sizePolicy().verticalPolicy()
        )
        
        # Dynamic font sizing and family
        font_family = "Inter"
        font_size = 12
        if layout and layout.font_family:
            font_family = layout.font_family
            font_size = 16 # Magickal fonts often need to be bigger
            
            # Force via Stylesheet to override any global theme issues
            btn.setStyleSheet(f"font-family: '{font_family}'; font-size: {font_size}pt;")
            
        font = QFont(font_family, font_size)
        font.setWeight(QFont.Weight.Medium)
        if len(label) > 1: # Icons or special chars
            font.setPointSize(10)
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
        
        # Determine if we need to apply a custom font
        layout = LAYOUTS.get(self.current_layout_name)
        font_family = layout.font_family if layout else None
        
        if self.target_editor:
            if font_family:
                # Use HTML to apply font specifically to this character
                # Note: We append the char in a span
                self.target_editor.insertHtml(f"<span style='font-family: {font_family}; font-size: 16pt;'>{char}</span>")
            else:
                self.target_editor.insertPlainText(char)
                
            self.target_editor.ensureCursorVisible()
            self.target_editor.setFocus()
            
        elif self.target_input:
            # QLineEdit does not support mixed fonts (Rich Text).
            # We must set the font for the whole widget if the user wants to see these chars.
            if font_family:
                 # Check if we should switch the font
                 current_font = self.target_input.font()
                 if current_font.family() != font_family:
                     new_font = QFont(font_family, 14) # Slightly larger for readability
                     self.target_input.setFont(new_font)
            
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

    def showEvent(self, event):
        """Auto-position the keyboard when shown."""
        super().showEvent(event)
        self._position_window()
        
    def _position_window(self):
        """Position the keyboard intelligently relative to the target field."""
        target = self.target_input or self.target_editor
        
        if not target:
            # Fallback to screen center bottom if no specific target
            screen = self.screen().availableGeometry()
            x = screen.x() + (screen.width() - self.width()) // 2
            y = screen.y() + screen.height() - self.height() - 40
            self.move(x, y)
            return

        # Get target global position and geometry
        # Fixed: Removed buggy Qt.QPoint call.
        pos_point = target.mapToGlobal(target.rect().topLeft())
        
        screen_geo = self.screen().availableGeometry()
        
        # Default: Spawn to the RIGHT
        spacing = 20
        x = pos_point.x() + target.width() + spacing
        # Align tops
        y = pos_point.y() 
        
        # Check Right Boundary
        if x + self.width() > screen_geo.right():
            # Not enough space on right, try LEFT
            x = pos_point.x() - self.width() - spacing
        
        # Check Left Boundary (if it failed right and went left, could it go off-screen?)
        if x < screen_geo.left():
            # If both sides fail, fallback to Bottom Center of screen (User preference safety)
            x = screen_geo.center().x() - (self.width() // 2)
            y = screen_geo.bottom() - self.height() - 20
        else:
            # Vertical adjustment if it falls off bottom
            if y + self.height() > screen_geo.bottom():
                y = screen_geo.bottom() - self.height() - 20
                
        self.move(x, y)

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