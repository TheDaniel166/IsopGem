from PyQt6.QtWidgets import QToolBar, QComboBox, QMenu
from PyQt6.QtCore import pyqtSignal
from shared.ui.theme import COLORS

class SpreadsheetToolbar(QToolBar):
    """
    The instruments of the Magus. Handles all toolbar actions and signals.
    """
    # Signals
    font_size_changed = pyqtSignal(int)
    save_requested = pyqtSignal()
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    style_action_triggered = pyqtSignal(str, bool) # action_name, checked
    align_action_triggered = pyqtSignal(str)
    export_json_requested = pyqtSignal()
    export_image_requested = pyqtSignal()
    export_csv_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Spreadsheet Tools", parent)
        self._setup_ui()
        
    def _setup_ui(self):
        self.setMovable(False)
        self.setStyleSheet(f"""
            QToolBar {{
                background: {COLORS['surface']};
                border-bottom: 1px solid {COLORS['border']};
                padding: 4px;
                spacing: 6px;
            }}
            QToolButton {{
                color: {COLORS['text']};
                border-radius: 4px;
                padding: 4px;
            }}
            QToolButton:hover {{
                background: {COLORS['highlight']};
            }}
            QToolButton:checked {{
                background: {COLORS['focus']};
                color: {COLORS['surface']};
            }}
        """)
        
        # File Operations
        self.act_save = self.addAction("Save")
        self.act_save.triggered.connect(self.save_requested.emit)
        
        self.addSeparator()
        
        # History
        self.act_undo = self.addAction("Undo")
        self.act_undo.triggered.connect(self.undo_requested.emit)
        self.act_redo = self.addAction("Redo")
        self.act_redo.triggered.connect(self.redo_requested.emit)
        
        self.addSeparator()
        
        # Font Tools
        self.combo_size = QComboBox()
        self.combo_size.addItems([str(s) for s in [8, 9, 10, 11, 12, 14, 16, 18, 24, 36]])
        self.combo_size.setCurrentText("11")
        self.combo_size.currentTextChanged.connect(lambda t: self.font_size_changed.emit(int(t)))
        self.addWidget(self.combo_size)
        
        self.addSeparator()
        
        # Style Actions
        self.act_bold = self.addAction("B")
        self.act_bold.setCheckable(True)
        self.act_bold.triggered.connect(lambda c: self.style_action_triggered.emit("bold", c))
        
        self.act_italic = self.addAction("I")
        self.act_italic.setCheckable(True)
        self.act_italic.triggered.connect(lambda c: self.style_action_triggered.emit("italic", c))
        
        self.act_underline = self.addAction("U")
        self.act_underline.setCheckable(True)
        self.act_underline.triggered.connect(lambda c: self.style_action_triggered.emit("underline", c))
        
        self.addSeparator()
        
        # Export Menu
        self.act_export_menu = self.addAction("Export")
        self.menu_export = QMenu(self)
        self.act_export_menu.setMenu(self.menu_export)
        # Assuming QToolButton popup mode is set automatically or handled by main window
        # QToolBar addAction doesn't return a QToolButton easily to set popup mode.
        # Let's just add individual actions for now as per original code, or keep it simple.
        
        self.act_export_csv = self.addAction("CSV")
        self.act_export_csv.triggered.connect(self.export_csv_requested.emit)
        
        self.act_export_json = self.addAction("JSON")
        self.act_export_json.triggered.connect(self.export_json_requested.emit)
        
        self.act_export_img = self.addAction("IMG")
        self.act_export_img.triggered.connect(self.export_image_requested.emit)

    def set_font_size(self, size: int):
        self.combo_size.setCurrentText(str(size))
        
    def set_style_state(self, bold: bool, italic: bool, underline: bool):
        self.act_bold.setChecked(bold)
        self.act_italic.setChecked(italic)
        self.act_underline.setChecked(underline)
