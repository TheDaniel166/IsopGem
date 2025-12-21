from .canvas.infinite_canvas import InfiniteCanvasView
from .ribbon_widget import RibbonWidget
from ..services.document_service import document_service_context
from PyQt6.QtWidgets import QApplication, QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QMessageBox, QComboBox, QFontComboBox, QColorDialog, QToolButton, QFrame
from PyQt6.QtGui import QFont, QTextCharFormat, QAction, QIcon, QColor, QTextListFormat
from PyQt6.QtCore import Qt, pyqtSlot
import logging

logger = logging.getLogger(__name__)

class MindscapePageWidget(QWidget):
    """
    Editor for a Mindscape Page (Document).
    Uses InfiniteCanvasView for OneNote-style editing.
    Hosts a Global Ribbon for formatting active text boxes.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # --- Ribbon ---
        self.ribbon = RibbonWidget()
        self.layout.addWidget(self.ribbon)
        
        # --- Canvas ---
        self.canvas = InfiniteCanvasView()
        self.layout.addWidget(self.canvas)
        
        self.current_doc_id = None
        self.active_editor = None
        
        # Initialize Ribbon Actions and UI
        self._init_actions()
        self._init_ribbon()
        
        # Focus Tracking
        # QApplication.focusChanged is unreliable with ProxyWidgets.
        # We use the Scene's focusItemChanged signal instead.
        if self.canvas.scene():
             self.canvas.scene().focusItemChanged.connect(self._on_scene_focus_changed)
             
        # Also keep Listen for "regular" focus changes just in case, or disable?
        # Let's keep it but prioritize scene events if they work.
        # Actually, let's rely on scene focus for the canvas context.
        
    def _on_focus_changed(self, old, new):
        """Track which text editor is active."""
        if isinstance(new, QTextEdit):
            self.active_editor = new
            # TODO: Update Ribbon UI to reflect current selection state (Bold/Italic status)
        elif new == self.canvas:
             pass

    # --- Formatting Helpers ---
    
    def _get_active_wrapper(self):
        """Get the RichTextEditor wrapper for the active editor."""
        if self.active_editor and self.active_editor.parent():
             parent = self.active_editor.parent()
             # Duck typing check for our wrapper API
             if hasattr(parent, 'toggle_list'):
                 return parent
        return None

    def _apply_format(self, fmt: QTextCharFormat):
        """Apply format to current editor selection."""
        if self.active_editor:
            self.active_editor.mergeCurrentCharFormat(fmt)
            self.active_editor.setFocus()
            
    def _on_scene_focus_changed(self, new_item, old_item, reason):
        """Track focus within the Graphics Scene."""
        if hasattr(new_item, 'widget_inner'):
             # It's one of our containers
             inner = new_item.widget_inner
             if hasattr(inner, 'rt_editor'):
                 self.active_editor = inner.rt_editor.editor
                 return

    # --- Formatting Helpers ---
    
    def _get_active_wrapper(self):
        """Get the RichTextEditor wrapper for the active editor."""
        if self.active_editor and self.active_editor.parent():
            parent = self.active_editor.parent()
            # Duck typing check for our wrapper API
            if hasattr(parent, 'toggle_list'):
                return parent
        return None

    def _apply_format(self, fmt: QTextCharFormat):
        """Apply format to current editor selection."""
        print(f"[Format] Applying format to {self.active_editor}")
        if self.active_editor:
            self.active_editor.mergeCurrentCharFormat(fmt)
            self.active_editor.setFocus()
        else:
            print("[Format] No active editor!")

    def _toggle_bold(self):
        if not self.active_editor: return
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Normal if self.active_editor.fontWeight() > QFont.Weight.Normal else QFont.Weight.Bold)
        self._apply_format(fmt)

    def _toggle_italic(self):
        if not self.active_editor: return
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.active_editor.fontItalic())
        self._apply_format(fmt)

    def _toggle_underline(self):
        if not self.active_editor: return
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.active_editor.fontUnderline())
        self._apply_format(fmt)
        
    def _set_font_family(self, font: QFont):
        if not self.active_editor: return
        fmt = QTextCharFormat()
        fmt.setFontFamily(font.family())
        self._apply_format(fmt)
        
    def _set_font_size(self, size_str):
        if not self.active_editor: return
        try:
             size = float(size_str)
             fmt = QTextCharFormat()
             fmt.setFontPointSize(size)
             self._apply_format(fmt)
        except ValueError:
             pass

    def _pick_color(self):
        if not self.active_editor: return
        color = QColorDialog.getColor(Qt.GlobalColor.black, self, "Select Text Color")
        if color.isValid():
             fmt = QTextCharFormat()
             fmt.setForeground(color)
             self._apply_format(fmt)

    def _set_align(self, alignment):
        if self.active_editor:
             self.active_editor.setAlignment(alignment)
             self.active_editor.setFocus()

    def _toggle_list(self, style):
        wrapper = self._get_active_wrapper()
        if wrapper:
             wrapper.toggle_list(style)
             self.active_editor.setFocus()

    def _toggle_strikethrough(self):
        wrapper = self._get_active_wrapper()
        if wrapper: wrapper.toggle_strikethrough()

    def _toggle_subscript(self):
        wrapper = self._get_active_wrapper()
        if wrapper: wrapper.toggle_subscript()

    def _toggle_superscript(self):
        wrapper = self._get_active_wrapper()
        if wrapper: wrapper.toggle_superscript()
        
    def _clear_formatting(self):
        wrapper = self._get_active_wrapper()
        if wrapper: wrapper.clear_formatting()

    def _pick_highlight(self):
        if not self.active_editor: return
        color = QColorDialog.getColor(Qt.GlobalColor.yellow, self, "Select Highlight Color")
        if color.isValid():
            wrapper = self._get_active_wrapper()
            if wrapper: wrapper.set_highlight(color)

    def _insert_table(self):
        wrapper = self._get_active_wrapper()
        if wrapper: wrapper.insert_table() # Default 3x3

    def _insert_image(self):
        wrapper = self._get_active_wrapper()
        if wrapper:
            wrapper.insert_image()
             
    # --- UI Initialization ---

    def _show_search(self):
        wrapper = self._get_active_wrapper()
        if wrapper: wrapper.show_search()

    def _init_actions(self):
        # Basic Formatting
        self.act_save = QAction("Save", self)
        self.act_save.setShortcut("Ctrl+S")
        self.act_save.triggered.connect(self.save_page)
        
        self.act_bold = QAction("Bold", self)
        self.act_bold.setShortcut("Ctrl+B")
        self.act_bold.triggered.connect(self._toggle_bold)
        
        self.act_italic = QAction("Italic", self)
        self.act_italic.setShortcut("Ctrl+I")
        self.act_italic.triggered.connect(self._toggle_italic)
        
        self.act_underline = QAction("Underline", self)
        self.act_underline.setShortcut("Ctrl+U")
        self.act_underline.triggered.connect(self._toggle_underline)

    def _init_ribbon(self):
        tab_home = self.ribbon.add_ribbon_tab("Home")
        
        # File Group
        grp_file = tab_home.add_group("File")
        grp_file.add_action(self.act_save)
        
        # Font Group (Extended)
        grp_font = tab_home.add_group("Font")
        
        # Font/Size ComboBoxes
        font_box = QWidget()
        font_layout = QHBoxLayout(font_box) # Use QHBoxLayout
        font_layout.setContentsMargins(0,0,0,0)
        
        self.font_combo = QFontComboBox()
        self.font_combo.setMaximumWidth(150)
        self.font_combo.currentFontChanged.connect(self._set_font_family)
        font_layout.addWidget(self.font_combo)
        
        self.size_combo = QComboBox()
        self.size_combo.setEditable(True)
        self.size_combo.setMaximumWidth(60)
        self.size_combo.addItems([str(s) for s in [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 36, 48]])
        self.size_combo.setCurrentText("12")
        self.size_combo.currentTextChanged.connect(self._set_font_size)
        font_layout.addWidget(self.size_combo)
        
        grp_font.add_widget(font_box)
        
        # Buttons
        grp_font.add_action(self.act_bold, Qt.ToolButtonStyle.ToolButtonTextOnly)
        grp_font.add_action(self.act_italic, Qt.ToolButtonStyle.ToolButtonTextOnly)
        grp_font.add_action(self.act_underline, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        # Advanced Font Actions (Strike, Sub, Sup)
        act_strike = QAction("S̶", self)
        act_strike.triggered.connect(self._toggle_strikethrough)
        grp_font.add_action(act_strike, Qt.ToolButtonStyle.ToolButtonTextOnly)

        act_sub = QAction("X₂", self)
        act_sub.triggered.connect(self._toggle_subscript)
        grp_font.add_action(act_sub, Qt.ToolButtonStyle.ToolButtonTextOnly)

        act_sup = QAction("X²", self)
        act_sup.triggered.connect(self._toggle_superscript)
        grp_font.add_action(act_sup, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        # Color & Highlight
        btn_color = QToolButton()
        btn_color.setText("Color")
        btn_color.clicked.connect(self._pick_color)
        grp_font.add_widget(btn_color)
        
        btn_high = QToolButton()
        btn_high.setText("High")
        btn_high.clicked.connect(self._pick_highlight)
        grp_font.add_widget(btn_high)
        
        act_clear = QAction("Clear", self)
        act_clear.triggered.connect(self._clear_formatting)
        grp_font.add_action(act_clear, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        # Paragraph Group
        grp_para = tab_home.add_group("Paragraph")
        
        # Alignment
        btn_left = QToolButton()
        btn_left.setText("Left")
        btn_left.clicked.connect(lambda: self._set_align(Qt.AlignmentFlag.AlignLeft))
        grp_para.add_widget(btn_left)
        
        btn_center = QToolButton()
        btn_center.setText("Center")
        btn_center.clicked.connect(lambda: self._set_align(Qt.AlignmentFlag.AlignCenter))
        grp_para.add_widget(btn_center)
        
        btn_right = QToolButton()
        btn_right.setText("Right")
        btn_right.clicked.connect(lambda: self._set_align(Qt.AlignmentFlag.AlignRight))
        grp_para.add_widget(btn_right)
        
        # Lists
        grp_para.add_separator()
        
        act_bullet = QAction("• List", self)
        act_bullet.triggered.connect(lambda: self._toggle_list(QTextListFormat.Style.ListDisc))
        grp_para.add_action(act_bullet, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        act_number = QAction("1. List", self)
        act_number.triggered.connect(lambda: self._toggle_list(QTextListFormat.Style.ListDecimal))
        grp_para.add_action(act_number, Qt.ToolButtonStyle.ToolButtonTextOnly)

        # Edit Group
        grp_edit = tab_home.add_group("Editing")
        
        act_find = QAction("Find", self)
        act_find.setShortcut("Ctrl+F")
        act_find.triggered.connect(self._show_search)
        grp_edit.add_action(act_find, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        # === TAB: INSERT ===
        tab_insert = self.ribbon.add_ribbon_tab("Insert")
        
        # Group: Tables
        grp_tables = tab_insert.add_group("Tables")
        btn_table = QToolButton()
        btn_table.setText("Table")
        btn_table.clicked.connect(self._insert_table)
        grp_tables.add_widget(btn_table)

        # Group: Illustrations
        grp_illus = tab_insert.add_group("Illustrations")
        btn_img = QToolButton()
        btn_img.setText("Image")
        btn_img.clicked.connect(self._insert_image)
        grp_illus.add_widget(btn_img)
        
    def load_node(self, doc_id: int):
        """Load content from Document."""
        if self.current_doc_id == doc_id:
            return
            
        if self.current_doc_id:
            self.save_page()
            
        self.current_doc_id = doc_id
        self.setEnabled(True)
        # self.update_view_mode()
        
        try:
            with document_service_context() as svc:
                doc = svc.get_document(doc_id)
                if doc:
                    # Load canvas data (raw_content should be JSON)
                    # If empty or HTML, load_json_data handles fallback logic
                    content = doc.raw_content or doc.content or ""
                    self.canvas.load_json_data(content)
                else:
                    self.canvas.clear_canvas()
                    self.setEnabled(False)
                    
        except Exception as e:
            logger.error(f"Error loading doc {doc_id}: {e}")
            # Fallback error message in a box?
            self.canvas.clear_canvas()
            self.canvas.add_note_container(50, 50, f"Error loading: {e}")

    def save_page(self):
        """Persist changes."""
        if not self.current_doc_id:
            return
            
        json_data = self.canvas.get_json_data()
        
        try:
            with document_service_context() as svc:
                # Save JSON to raw_content. 
                # For 'content', maybe save a text-only dump?
                # Or just save JSON to raw_content and dummy to content.
                svc.update_document(self.current_doc_id, content="[Canvas Data]", raw_content=json_data)
            logger.info(f"Saved page {self.current_doc_id}")
            # Optional: Toast
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def clear(self):
        self.current_doc_id = None
        self.canvas.clear_canvas()
        self.setEnabled(False)
