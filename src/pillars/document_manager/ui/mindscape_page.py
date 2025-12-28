"""
Mindscape Page - The Canvas Editor.
Widget for editing Mindscape documents with ribbon toolbar and infinite canvas support.
"""
import logging
from typing import Any, Optional

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QAction, QFont, QTextCharFormat, QTextListFormat
from PyQt6.QtWidgets import (QColorDialog, QComboBox, QFontComboBox, QFrame,
                             QHBoxLayout, QLabel, QMessageBox, QPushButton,
                             QSlider, QTextEdit, QToolButton, QVBoxLayout,
                             QWidget)

from ..services.document_service import document_service_context
from .canvas.infinite_canvas import InfiniteCanvasView
from .ribbon_widget import RibbonWidget

logger = logging.getLogger(__name__)

class MindscapePageWidget(QWidget):
    """
    Editor for a Mindscape Page (Document).
    Uses InfiniteCanvasView for OneNote-style editing.
    Hosts a Global Ribbon for formatting active text boxes.
    """
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        Returns:
            Result of __init__ operation.
        """
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- Ribbon ---
        self.ribbon = RibbonWidget()
        self.main_layout.addWidget(self.ribbon)
        
        # --- Canvas ---
        self.canvas = InfiniteCanvasView()
        self.main_layout.addWidget(self.canvas)
        
        # --- Status Bar with Zoom Controls ---
        self._init_status_bar()
        
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
        
    def _on_focus_changed(self, _old: Any, new: Any) -> None:
        """Track which text editor is active."""
        if isinstance(new, QTextEdit):
            self.active_editor = new
            # NOTE: Ribbon state sync planned for future enhancement (see ADR-007)
        elif new == self.canvas:
             pass

    # --- Formatting Helpers ---
    
    def _get_active_wrapper(self) -> Optional[Any]:
        """Get the RichTextEditor wrapper for the active editor."""
        if self.active_editor:
            parent = self.active_editor.parent()
            # Duck typing check for our wrapper API
            if parent and hasattr(parent, 'toggle_list'):
                return parent
        return None

    def _apply_format(self, fmt: QTextCharFormat) -> None:
        """Apply format to current editor selection."""
        if self.active_editor:
            self.active_editor.mergeCurrentCharFormat(fmt)
            self.active_editor.setFocus()
            
    def _on_scene_focus_changed(self, new_item: Any, _old_item: Any, _reason: Any) -> None:
        """Track focus within the Graphics Scene."""
        if hasattr(new_item, 'widget_inner'):
             # It's one of our containers
             inner = new_item.widget_inner
             if hasattr(inner, 'rt_editor'):
                 self.active_editor = inner.rt_editor.editor
                 return


    def _toggle_bold(self) -> None:
        """Toggle bold formatting on the active editor's selection."""
        if not self.active_editor: return
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Normal if self.active_editor.fontWeight() > QFont.Weight.Normal else QFont.Weight.Bold)
        self._apply_format(fmt)

    def _toggle_italic(self) -> None:
        """Toggle italic formatting on the active editor's selection."""
        if not self.active_editor: return
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.active_editor.fontItalic())
        self._apply_format(fmt)

    def _toggle_underline(self) -> None:
        """Toggle underline formatting on the active editor's selection."""
        if not self.active_editor: return
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.active_editor.fontUnderline())
        self._apply_format(fmt)
        
    def _set_font_family(self, font: QFont) -> None:
        """Apply the selected font family to the active editor's selection."""
        if not self.active_editor: return
        fmt = QTextCharFormat()
        fmt.setFontFamily(font.family())
        self._apply_format(fmt)
        
    def _set_font_size(self, size_str: str) -> None:
        """Apply the selected font size to the active editor's selection."""
        if not self.active_editor: return
        try:
             size = float(size_str)
             fmt = QTextCharFormat()
             fmt.setFontPointSize(size)
             self._apply_format(fmt)
        except ValueError:
             pass

    def _pick_color(self) -> None:
        """Open color picker and apply selected color to text."""
        if not self.active_editor: return
        color = QColorDialog.getColor(Qt.GlobalColor.black, self, "Select Text Color")
        if color.isValid():
             fmt = QTextCharFormat()
             fmt.setForeground(color)
             self._apply_format(fmt)

    def _set_align(self, alignment: Qt.AlignmentFlag) -> None:
        if self.active_editor:
             self.active_editor.setAlignment(alignment)
             self.active_editor.setFocus()

    def _toggle_list(self, style: QTextListFormat.Style) -> None:
        wrapper = self._get_active_wrapper()
        if wrapper:
             wrapper.toggle_list(style)
             self.active_editor.setFocus()

    def _toggle_strikethrough(self) -> None:
        wrapper = self._get_active_wrapper()
        if wrapper: wrapper.toggle_strikethrough()

    def _toggle_subscript(self) -> None:
        wrapper = self._get_active_wrapper()
        if wrapper: wrapper.toggle_subscript()

    def _toggle_superscript(self) -> None:
        wrapper = self._get_active_wrapper()
        if wrapper: wrapper.toggle_superscript()
        
    def _clear_formatting(self) -> None:
        wrapper = self._get_active_wrapper()
        if wrapper: wrapper.clear_formatting()

    def _pick_highlight(self) -> None:
        """Open color picker and apply selected highlight to text background."""
        if not self.active_editor: return
        color = QColorDialog.getColor(Qt.GlobalColor.yellow, self, "Select Highlight Color")
        if color.isValid():
            wrapper = self._get_active_wrapper()
            if wrapper: wrapper.set_highlight(color)

    def _insert_table(self) -> None:
        """Insert a default 3x3 table at the cursor position."""
        wrapper = self._get_active_wrapper()
        if wrapper: wrapper.insert_table()

    def _insert_image(self) -> None:
        """Open file dialog to insert an image at the cursor position."""
        wrapper = self._get_active_wrapper()
        if wrapper:
            wrapper.insert_image()
             
    # --- UI Initialization ---

    def _show_search(self) -> None:
        """Show the search/replace dialog for the active editor."""
        wrapper = self._get_active_wrapper()
        if wrapper: wrapper.show_search()

    def _start_shape_insert(self, shape_type: type) -> None:
        """Start inserting a shape on the canvas."""
        self.canvas.start_shape_insert(shape_type)
    
    def _show_polygon_dialog(self) -> None:
        """Show polygon configuration dialog."""
        from .shape_features import PolygonConfigDialog
        from .shape_item import PolygonShapeItem
        
        dialog = PolygonConfigDialog(self)
        if dialog.exec():
            sides, skip = dialog.get_config()
            # Create custom insert handler for configured polygon
            self._pending_polygon = (sides, skip)
            self._start_polygon_insert()
    
    def _start_polygon_insert(self) -> None:
        """Start inserting a configured polygon."""
        from PyQt6.QtCore import Qt

        from .shape_item import PolygonShapeItem
        
        sides, skip = self._pending_polygon
        self.canvas._insert_mode = True
        self.canvas._insert_shape_type = PolygonShapeItem
        self.canvas._polygon_config = (sides, skip)
        self.canvas.setCursor(Qt.CursorShape.CrossCursor)
    
    def _init_status_bar(self) -> None:
        """Initialize the status bar containing zoom slider and percentage controls."""
        status_bar = QFrame()
        status_bar.setFrameShape(QFrame.Shape.NoFrame)
        status_bar.setStyleSheet("""
            QFrame {
                background: #f0f0f0;
                border-top: 1px solid #d0d0d0;
            }
            QPushButton {
                background: transparent;
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                padding: 2px 8px;
                min-width: 24px;
            }
            QPushButton:hover { background: #e0e0e0; }
            QPushButton:pressed { background: #d0d0d0; }
            QLabel { padding: 0 8px; }
        """)
        
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(8, 4, 8, 4)
        status_layout.setSpacing(4)
        
        # Left spacer (for future status text)
        status_layout.addStretch()
        
        # Zoom controls (right side)
        btn_zoom_out = QPushButton("−")
        btn_zoom_out.setToolTip("Zoom Out (Ctrl+Wheel Down)")
        btn_zoom_out.clicked.connect(self.canvas.zoom_out)
        status_layout.addWidget(btn_zoom_out)
        
        # Slider
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 400)  # 10% to 400%
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(120)
        self.zoom_slider.setToolTip("Zoom Level")
        self.zoom_slider.valueChanged.connect(self._on_zoom_slider_changed)
        status_layout.addWidget(self.zoom_slider)
        
        btn_zoom_in = QPushButton("+")
        btn_zoom_in.setToolTip("Zoom In (Ctrl+Wheel Up)")
        btn_zoom_in.clicked.connect(self.canvas.zoom_in)
        status_layout.addWidget(btn_zoom_in)
        
        # Percentage label
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(50)
        status_layout.addWidget(self.zoom_label)
        
        # Fit button
        btn_zoom_fit = QPushButton("Fit")
        btn_zoom_fit.setToolTip("Fit to Content")
        btn_zoom_fit.clicked.connect(self.canvas.zoom_fit)
        status_layout.addWidget(btn_zoom_fit)
        
        # Reset button  
        btn_zoom_reset = QPushButton("100%")
        btn_zoom_reset.setToolTip("Reset to 100%")
        btn_zoom_reset.clicked.connect(self.canvas.zoom_reset)
        status_layout.addWidget(btn_zoom_reset)
        
        self.main_layout.addWidget(status_bar)
        
        # Connect canvas zoom signal to update UI
        self.canvas.zoom_changed.connect(self._on_canvas_zoom_changed)
    
    def _on_zoom_slider_changed(self, value: int) -> None:
        """Handle slider value change."""
        self.canvas.set_zoom(value / 100.0)
    
    def _on_canvas_zoom_changed(self, percentage: float) -> None:
        """Update UI when canvas zoom changes."""
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(int(percentage))
        self.zoom_slider.blockSignals(False)
        self.zoom_label.setText(f"{int(percentage)}%")


    def _init_actions(self) -> None:
        """Initialize keyboard-shortcut actions for formatting commands."""
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

    def _init_ribbon(self) -> None:
        """Build the Ribbon UI with Home and Insert tabs containing formatting groups."""
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
        
        # Shapes dropdown
        from PyQt6.QtWidgets import QMenu

        from .shape_item import (ArrowShapeItem, EllipseShapeItem,
                                 LineShapeItem, RectShapeItem,
                                 TriangleShapeItem)
        
        btn_shapes = QToolButton()
        btn_shapes.setText("Shapes")
        btn_shapes.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        menu_shapes = QMenu(btn_shapes)
        for name, shape_cls in [
            ("Rectangle", RectShapeItem),
            ("Ellipse", EllipseShapeItem),
            ("Triangle", TriangleShapeItem),
            ("Line", LineShapeItem),
            ("Arrow", ArrowShapeItem),
        ]:
            action = menu_shapes.addAction(name)
            action.triggered.connect(
                lambda _checked, sc=shape_cls: self._start_shape_insert(sc)
            )
        
        menu_shapes.addSeparator()
        polygon_action = menu_shapes.addAction("Polygon...")
        polygon_action.triggered.connect(self._show_polygon_dialog)
        
        btn_shapes.setMenu(menu_shapes)
        grp_illus.add_widget(btn_shapes)
        
    def load_node(self, doc_id: int, reset_scroll: bool = True) -> None:
        """Load content from Document."""
        if self.current_doc_id == doc_id:
            # Still re-enable just in case
            self.setEnabled(True)
            return
            
        if self.current_doc_id:
            self.save_page()
            
        self.current_doc_id = doc_id
        self.setEnabled(True)
        
        try:
            with document_service_context() as svc:
                doc = svc.get_document(doc_id)
                if doc:
                    # Load canvas data (raw_content should be JSON)
                    # If empty or HTML, load_json_data handles fallback logic
                    content = doc.raw_content or doc.content or ""
                    self.canvas.load_json_data(content, reset_scroll=reset_scroll)
                else:
                    self.canvas.clear_canvas()
                    self.setEnabled(False)
                    
        except Exception as e:
            logger.error(f"Error loading doc {doc_id}: {e}")
            # Fallback error message in a box?
            self.canvas.clear_canvas()
            self.canvas.add_note_container(50, 50, f"Error loading: {e}")

    def highlight_search_term(self, text: str) -> None:
        """Find text in any note container and jump to it."""
        if not text or not self.canvas.scene():
            return

        from .canvas.note_container import NoteContainerItemMovable

        for item in self.canvas.scene().items():
            if isinstance(item, NoteContainerItemMovable):
                editor = item.widget_inner.editor
                if not editor: continue

                # Quick check (case-insensitive for convenience)
                if text.lower() in editor.toPlainText().lower():
                    # Process this item
                    item.setFocus()
                    editor.setFocus()
                    
                    # Highlight in editor
                    # Block signals to prevent "Content Changed" -> Scene Expansion -> View Reset
                    was_blocked = editor.signalsBlocked()
                    editor.blockSignals(True)
                    try:
                        wrapper = item.widget_inner.rt_editor
                        wrapper.search_feature.find_next(text, False, False)
                    finally:
                        editor.blockSignals(was_blocked)
                    
                    # Calculate position based on CONTENT coordinates, not just viewport
                    # This handles the case where the container starts small (scrolled) and then expands
                    rect = editor.cursorRect()
                    content_y = rect.center().y() + editor.verticalScrollBar().value()
                    
                    # Assume editor is at (0, 20) inside the inner widget (due to handle)
                    # We can map precisely if we want, but this logic is robust for the expansion case
                    # editor.pos().y() is usually 20
                    offset_y = editor.pos().y()
                    
                    target_local_y = offset_y + content_y
                    # Map local X normally (scrolling is usually vertical)
                    target_local_x = editor.pos().x() + rect.center().x() + editor.horizontalScrollBar().value()


                    
                    # Force the container to expand NOW so the visual matches our calculated point
                    if hasattr(item, '_auto_resize'):
                        item._auto_resize()
                        
                    # CRITICAL: Since we blocked signals, the Canvas doesn't know it needs to grow.
                    # We must tell it manually before we try to look at the new coordinates.
                    if hasattr(self.canvas, '_update_scene_rect'):
                        self.canvas._update_scene_rect()
                        
                    # Use QTimer to ensure this happens after layout
                    from PyQt6.QtCore import QTimer
                    def do_center():
                        # Recalculate point in case scene transform changed slightly
                        """
                        Do center logic.
                        
                        """
                        final_point = item.mapToScene(QPointF(target_local_x, target_local_y))
                        self.canvas.centerOn(final_point)
                        
                    QTimer.singleShot(10, do_center)
                    return

    def save_page(self) -> None:
        """Persist changes."""
        if not self.current_doc_id:
            return
            
        json_data = self.canvas.get_json_data()
        
        try:
            with document_service_context() as svc:
                # Save JSON to raw_content. 
                # Save extracted text to content for searching.
                searchable_text = self.canvas.get_searchable_text()
                svc.update_document(self.current_doc_id, content=searchable_text, raw_content=json_data)
            logger.info(f"Saved page {self.current_doc_id}")
            # Optional: Toast
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def clear(self) -> None:
        """
        Clear logic.
        
        Returns:
            Result of clear operation.
        """
        self.current_doc_id = None
        self.canvas.clear_canvas()
        self.setEnabled(False)