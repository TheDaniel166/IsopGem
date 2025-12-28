"""
Spreadsheet Window - The Sovereign Tablet Editor.
Main window hosting the spreadsheet view, formula bar, toolbar, and multi-sheet tab navigation.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QToolBar, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QFontComboBox, QSpinBox, QLabel, QColorDialog, QToolButton, QMenu, QLineEdit, QStyle, QFileDialog, QInputDialog
)
import csv
from PyQt6.QtGui import QAction, QIcon, QFont, QColor
from PyQt6.QtCore import Qt, QSize, QEvent
import re

from .spreadsheet_view import SpreadsheetView, SpreadsheetModel
from .scroll_tab_bar import ScrollTabBar
from .find_replace_dialog import FindReplaceDialog
from pillars.correspondences.services.table_service import TableService
from pillars.correspondences.services.conditional_formatting import ConditionalRule
from shared.ui.virtual_keyboard import get_shared_virtual_keyboard

class SpreadsheetWindow(QMainWindow):
    """
    The Sovereign Window.
    Hosts the Grid and the Toolbar (commands).
    """
    def __init__(self, table_id, name, content, service: TableService, parent=None):
        """
          init   logic.
        
        Args:
            table_id: Description of table_id.
            name: Description of name.
            content: Description of content.
            service: Description of service.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.table_id = table_id
        self.service = service
        self.setWindowTitle(f"Emerald Tablet: {name}")
        self.resize(1200, 800)

        # 1. Data Migration & Model Setup
        self.models = []
        scrolls_data = []
        active_index = 0

        # Detect Format
        if "scrolls" in content:
            # New Format
            scrolls_data = content.get("scrolls", [])
            active_index = content.get("active_scroll_index", 0)
        else:
            # Legacy Format - Wrap in Single Scroll
            scrolls_data = [{
                "name": "Sheet1",
                "columns": content.get("columns", []),
                "data": content.get("data", []) or content.get("rows", []),
                "styles": content.get("styles", {})
            }]
            active_index = 0
            
        # Hydrate Models
        for scroll in scrolls_data:
            m = SpreadsheetModel(scroll)
            # Store name on the model for convenience? Or separate metadata?
            # Model doesn't natively store name, let's attach it.
            m.scroll_name = scroll.get("name", "Sheet") 
            self.models.append(m)
            
        if not self.models:
            # Fallback for empty
            m = SpreadsheetModel({"columns": [], "data": []})
            m.scroll_name = "Sheet1"
            self.models.append(m)

        # Ensure index range
        if active_index >= len(self.models): active_index = 0
        self.current_model_index = active_index
        self.model = self.models[active_index]

        # 2. View Setup
        self.view = SpreadsheetView(self)
        self.view.setModel(self.model)
        self.view.setShowGrid(False)

        # 2. Central Widget Layout
        # We need a container to hold the Formula Bar AND the View (Grid)
        self.container = QWidget()
        self.central_layout = QVBoxLayout(self.container)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        
        # 2a. Formula Bar (Standard separate widget)
        self.formula_bar_container = QWidget()
        # Use QHBoxLayout for the row (Label + Input)
        fb_layout = QHBoxLayout(self.formula_bar_container)
        fb_layout.setContentsMargins(4, 4, 4, 4)
        fb_layout.setSpacing(4)
        
        # FX Button (The Wizard)
        self.btn_fx = QToolButton()
        self.btn_fx.setText("ƒx")
        self.btn_fx.setToolTip("Insert Function")
        self.btn_fx.clicked.connect(self._launch_formula_wizard)
        self.btn_fx.setFixedWidth(24)
        self.btn_fx.setStyleSheet("font-weight: bold; font-style: italic;")
        
        self.formula_bar = QLineEdit()
        self.formula_bar.setPlaceholderText("Formula or Value (Start with =)")
        self.formula_bar.returnPressed.connect(self._on_formula_return)
        
        # Name Box (e.g. A1)
        self.name_box = QLineEdit()
        self.name_box.setReadOnly(True)
        self.name_box.setFixedWidth(80) # Increased from 50
        self.name_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_box.setPlaceholderText("A1")
        self.name_box.setStyleSheet("font-weight: bold; padding-left: 4px; padding-right: 4px;")
        
        fb_layout.addWidget(self.name_box)
        fb_layout.addWidget(self.btn_fx)
        fb_layout.addWidget(self.formula_bar)
        
        self.central_layout.addWidget(self.formula_bar_container)
        self.central_layout.addWidget(self.view)
        
        # 2b. Scroll Tab Bar
        self.tab_bar = ScrollTabBar()
        self.central_layout.addWidget(self.tab_bar)
        
        # Populate Tabs
        for m in self.models:
            self.tab_bar.add_tab(m.scroll_name)
        self.tab_bar.set_current_index(self.current_model_index)
        
        # Connect Signals
        self.tab_bar.tab_added.connect(self._on_scroll_added)
        self.tab_bar.tab_changed.connect(self._on_scroll_changed)
        
        # Menu (Show all sheets)
        def _show_all_sheets_menu():
             names = [m.scroll_name for m in self.models]
             self.tab_bar.update_menu(names)
             self.tab_bar.btn_menu.showMenu()
        self.tab_bar.btn_menu.clicked.connect(_show_all_sheets_menu)

        self.setCentralWidget(self.container)
        
        # Connect Selection Sync
        self.view.selectionModel().currentChanged.connect(self._on_selection_changed)
        self.view.selectionModel().selectionChanged.connect(self._on_range_selection_changed)
        # Connect ONLY current model initialy
        self.model.dataChanged.connect(self._on_data_changed)
        
        # State for point-and-click references
        self._is_editing_formula = False
        self._ref_mode = True # True = Enter Mode (Arrows navigate), False = Edit Mode (Arrows cursor)
        self._edit_source_index = None # The index we are editing (e.g. A1) while clicking B2
        self._phantom_ref_cursor = None # Virtual cursor for arrow navigation (keeps editor open)
        
        # Track manual edits to detect '='
        self.formula_bar.textEdited.connect(self._on_formula_text_edited)
        
        # 3. Toolbar
        self._setup_toolbar()
        
        # 4. Keyboard Dock (Hidden by default)
        from PyQt6.QtWidgets import QDockWidget
        self._kb_dock = QDockWidget("Virtual Keyboard", self)
        self._kb_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self._kb_dock.setWidget(get_shared_virtual_keyboard(self))
        self._kb_dock.hide()
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._kb_dock)
        
        # 5. Unify Workflow: Listen for inline editor
        self.view.editor_text_changed.connect(self._on_inline_text_edited)
        self.view.viewport().installEventFilter(self)

    def eventFilter(self, source, event):
        """
        Hijack mouse clicks and KEY PRESSES on the viewport/editor when in Reference Mode.
        """
        # A. Mouse Click Logic (Existing + New: Click Editor -> Edit Mode)
        if source == self.view.viewport() and event.type() == QEvent.Type.MouseButtonPress:
             if self._is_editing_formula:
                # Calculate cell under mouse
                pos = event.pos()
                index = self.view.indexAt(pos)
                
                # Check if we clicked the cell we are editing (Source)
                is_source = (index == self._edit_source_index)
                
                if index.isValid() and not is_source:
                    # Insert Reference
                    self._insert_reference_manual(index)
                    return True
                
        # B. Key Press Logic (Navigation)
        # We listen on active_editor (which installed us as filter) OR the viewport?
        # Actually editor events come from editor source.
        if event.type() == QEvent.Type.KeyPress:
             # 1. Toggle Mode (Ctrl+E)
             if event.key() == Qt.Key.Key_E and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                 self._ref_mode = not self._ref_mode
                 # Force cursor update?
                 return True # Consume
                 
             # 2. Key Navigation (Arrows)
             if self._is_editing_formula and self._ref_mode:
                 if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
                     self._handle_arrow_navigation(event.key())
                     return True # Swallow event (don't move cursor in text)

        # C. Click on Editor -> Disable Ref Mode (Switch to Edit)
        # Note: Editor is separate widget, so source check needed?
        # C. Click on Editor -> Disable Ref Mode (Switch to Edit)
        # Note: Editor is separate widget, so source check needed?
        if self.view.active_editor and source == self.view.active_editor:
             if event.type() == QEvent.Type.MouseButtonPress:
                 self._ref_mode = False

        return super().eventFilter(source, event)

    def _handle_arrow_navigation(self, key):
        """
        Moves the selection relative to the LAST inserted reference (or current selection).
        And inserts/updates the reference in the formula.
        """
        # 1. Determine Start Position
        # Use Phantom Cursor if exists, else start from Source (Current)
        start_index = self._phantom_ref_cursor if self._phantom_ref_cursor else self.view.currentIndex()
        if not start_index.isValid(): return
        
        row, col = start_index.row(), start_index.column()
        
        # 2. Calculate Delta
        if key == Qt.Key.Key_Up: row -= 1
        elif key == Qt.Key.Key_Down: row += 1
        elif key == Qt.Key.Key_Left: col -= 1
        elif key == Qt.Key.Key_Right: col += 1
        
        # 3. Boundary Check
        row = max(0, min(row, self.model.rowCount() - 1))
        col = max(0, min(col, self.model.columnCount() - 1))
        
        # 4. Move Virtual Cursor
        new_index = self.model.index(row, col)
        self._phantom_ref_cursor = new_index
        
        # 5. Insert Reference
        # This will trigger text update -> parser -> highlighting of new_index
        self._insert_reference_manual(new_index)
        
        # Note: We DO NOT call setCurrentIndex(new_index) because that would close the active editor.
        # The visual highlighting relies on the Formula Engine parsing the new text and drawing the Colored Box.

    def _on_inline_text_edited(self, text):
        """
        Called when user types in the inline cell editor.
        Syncs to Formula Bar and triggers Reference Mode check.
        """
        # 1. Sync Formula Bar (Just text, don't trigger its signals yet)
        self.formula_bar.blockSignals(True)
        self.formula_bar.setText(text)
        self.formula_bar.blockSignals(False)
        
        # 2. Check for Mode Switch (e.g. user typed '=')
        # We manually trigger the logic that normally watches formula bar
        self._on_formula_text_edited(text)
        
        # 3. Ensure we track this cell as the source
        if not self._edit_source_index:
             self._edit_source_index = self.view.currentIndex()
             
        # 4. Auto-Switch to Ref Mode on Operators
        if text and text[-1] in ('=', '+', '-', '*', '/', '(', ','):
            self._ref_mode = True
            self._phantom_ref_cursor = None # Reset virtual cursor to start from Source again

    def _insert_reference_manual(self, index):
        """
        Manually inserts a reference into:
        1. The Formula Bar
        2. The Active Inline Editor (if exists)
        """
        def col_to_letter(col_idx):
            """
            Col to letter logic.
            
            Args:
                col_idx: Description of col_idx.
            
            """
            res = ""
            while col_idx >= 0:
                res = chr((col_idx % 26) + 65) + res
                col_idx = (col_idx // 26) - 1
            return res
            
        ref_str = f"{col_to_letter(index.column())}{index.row() + 1}"
        
        # Insert into Formula Bar
        # Strategy: Insert at cursor position.
        # But where is the cursor?
        # If inline editor is focused, we use its cursor.
        # If formula bar is focused, we use its cursor.
        
        target_widget = self.view.active_editor if self.view.active_editor else self.formula_bar
        
        cursor = target_widget.cursorPosition()
        text = target_widget.text()
        
        new_text = text[:cursor] + ref_str + text[cursor:]
        
        # Update both
        self.formula_bar.setText(new_text)
        if self.view.active_editor:
            self.view.active_editor.setText(new_text)
            self.view.active_editor.setCursorPosition(cursor + len(ref_str))
            
        # Update state
        # (Usually handled by textEdited, but we set programmatically)
        # We need to ensure coloring update happens
        # self._update_toolbar_state(current) # Not quite.
        # Just triggering a viewport update usually helps
        self.view.viewport().update()
        
    def _launch_formula_wizard(self):
        """Summons the Wizard to help insert a function."""
        from .formula_wizard import FormulaWizardDialog, FormulaArgumentDialog
        
        # Stage 1: Function Selection (Modal)
        wiz_dlg = FormulaWizardDialog(engine=self.model.formula_engine, parent=self)
        if wiz_dlg.exec():
            # User selected a function
            metadata = wiz_dlg.get_selected_formula()
            if not metadata: return
            
            # Capture the original target cell AND its content to restore later
            self._wizard_target_index = self.view.currentIndex()
            self._wizard_initial_text = self.formula_bar.text()
            
            # Stage 2: Arguments (Non-Modal)
            # We keep a reference so it doesn't get garbage collected
            self._arg_dialog = FormulaArgumentDialog(metadata, self.model.formula_engine, parent=self)
            self._arg_dialog.accepted.connect(lambda: self._commit_wizard_formula(self._arg_dialog))
            
            # Connect Grid Selection -> Dialog Input
            self.view.selectionModel().selectionChanged.connect(self._on_wizard_selection_change)
            
            # Cleanup when closed
            self._arg_dialog.finished.connect(lambda: self.view.selectionModel().selectionChanged.disconnect(self._on_wizard_selection_change))
            
            self._arg_dialog.show()

    def _commit_wizard_formula(self, dialog):
        """Called when Stage 2 is Accepted."""
        new_part = dialog.get_formula_text()
        
        # Use captured initial text instead of current bar which might be dirty
        base_text = getattr(self, '_wizard_initial_text', "")
        
        if not base_text or base_text == "=":
            final_text = new_part
        else:
             # Append logic
             if base_text.startswith("="):
                 final_text = base_text + new_part[1:] # Skip '='
             else:
                 final_text = new_part
        
        # Restore focus to the original target cell
        if hasattr(self, '_wizard_target_index') and self._wizard_target_index.isValid():
             self.view.setCurrentIndex(self._wizard_target_index)
             
             # Directly commit to model to avoid signal race conditions with bar updates
             self.model.setData(self._wizard_target_index, final_text, Qt.ItemDataRole.EditRole)
             
             # Sync UI
             self.formula_bar.blockSignals(True)
             self.formula_bar.setText(final_text)
             self.formula_bar.blockSignals(False)
             self.view.setFocus()
        
    def _on_wizard_selection_change(self, selected, deselected):
        """
        Syncs grid selection to active Wizard input field.
        Format: A1 or A1:B2 or A1,C3 (if multiple ranges supported later)
        """
        if not hasattr(self, '_arg_dialog') or not self._arg_dialog.isVisible():
            return
            
        indexes = self.view.selectionModel().selectedIndexes()
        if not indexes: return
        
        # Calculate range string using FormulaEngine logic is ideal, 
        # but let's do simple A1:B2 conversion here.
        
        # Find bounds
        min_row = min(idx.row() for idx in indexes)
        max_row = max(idx.row() for idx in indexes)
        min_col = min(idx.column() for idx in indexes)
        max_col = max(idx.column() for idx in indexes)
        
        def col_to_letter(col_idx):
            # 0 -> A, 26 -> AA
            """
            Col to letter logic.
            
            Args:
                col_idx: Description of col_idx.
            
            """
            res = ""
            while col_idx >= 0:
                res = chr((col_idx % 26) + 65) + res
                col_idx = (col_idx // 26) - 1
            return res
            
        start_addr = f"{col_to_letter(min_col)}{min_row + 1}"
        
        if min_row == max_row and min_col == max_col:
            addr = start_addr
        else:
            end_addr = f"{col_to_letter(max_col)}{max_row + 1}"
            addr = f"{start_addr}:{end_addr}"
            
        self._arg_dialog.update_active_input(addr)

    def _setup_toolbar(self):
        toolbar = QToolBar("Tablet Tools")
        icon_size = self.style().pixelMetric(QStyle.PixelMetric.PM_SmallIconSize)
        scaled_size = int(icon_size * 1.5)
        toolbar.setIconSize(QSize(scaled_size, scaled_size))
        self.addToolBar(toolbar)
        
        # --- File Operations ---
        act_save = QAction("💾 Save", self)
        act_save.triggered.connect(self._save_table)
        toolbar.addAction(act_save)
        
        toolbar.addSeparator()
        
        # --- History ---
        stack = self.model.undo_stack
        
        act_undo = stack.createUndoAction(self, "Undo")
        act_undo.setShortcut("Ctrl+Z")
        act_undo.setText("↩ Undo")
        toolbar.addAction(act_undo)
        
        act_redo = stack.createRedoAction(self, "Redo")
        act_redo.setShortcut("Ctrl+Shift+Z")
        act_redo.setText("↪ Redo")
        toolbar.addAction(act_redo)
        
        toolbar.addSeparator()
        
        # --- File I/O ---
        act_import = QAction(QIcon.fromTheme("document-open"), "Import CSV", self)
        act_import.setToolTip("Import CSV")
        act_import.triggered.connect(self._import_csv)
        toolbar.addAction(act_import)
        
        act_export = QAction(QIcon.fromTheme("document-save"), "Export CSV", self)
        act_export.setToolTip("Export CSV")
        act_export.triggered.connect(self._export_csv)
        toolbar.addAction(act_export)
        
        toolbar.addSeparator()

        # --- Font Face & Size ---
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont("Arial"))
        self.font_combo.currentFontChanged.connect(self._on_font_family_changed)
        self.font_combo.setFixedWidth(150)
        toolbar.addWidget(self.font_combo)
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 72)
        self.size_spin.setValue(11)
        self.size_spin.valueChanged.connect(self._on_font_size_changed)
        toolbar.addWidget(self.size_spin)
        
        toolbar.addSeparator()

        # --- Style (Bold, Italic, Underline) ---
        self.act_bold = QAction("𝐁", self)
        self.act_bold.setCheckable(True)
        self.act_bold.triggered.connect(lambda c: self._apply_style("bold", c))
        toolbar.addAction(self.act_bold)
        
        self.act_italic = QAction("𝐼", self)
        self.act_italic.setCheckable(True)
        self.act_italic.triggered.connect(lambda c: self._apply_style("italic", c))
        toolbar.addAction(self.act_italic)

        self.act_underline = QAction("U̲", self)
        self.act_underline.setShortcut("Ctrl+U")
        self.act_underline.triggered.connect(lambda checked: self._apply_format("underline", checked))
        toolbar.addAction(self.act_underline)
        
        toolbar.addSeparator()

        # --- Layout Tools (Autofit & Wrap) ---
        act_autofit = QAction("↔ Fit", self)
        act_autofit.setToolTip("Autofit Columns & Rows")
        act_autofit.triggered.connect(self.view.autofit)
        toolbar.addAction(act_autofit)
        
        self.act_wrap = QAction("ABC", self)
        self.act_wrap.setToolTip("Toggle Word Wrap")
        self.act_wrap.setCheckable(True)
        self.act_wrap.setChecked(False) # Default off like Excel? Or on? Default off usually.
        self.act_wrap.toggled.connect(self.view.setWordWrap) # QTableView slot
        toolbar.addAction(self.act_wrap)
        
        toolbar.addSeparator()
        
        # --- Colors ---
        act_text_color = QAction("A", self)
        act_text_color.setToolTip("Text Color")
        act_text_color.triggered.connect(lambda: self._pick_color("text"))
        toolbar.addAction(act_text_color)
        
        act_bg_color = QAction("Bucket", self)
        act_bg_color.setToolTip("Cell Background Color")
        act_bg_color.triggered.connect(lambda: self._pick_color("background"))
        toolbar.addAction(act_bg_color)
        
        toolbar.addSeparator()
        
        # --- Alignment (Left, Center, Right) ---
        act_left = QAction("Left", self)
        act_left.triggered.connect(lambda: self._apply_align("left"))
        toolbar.addAction(act_left)

        act_center = QAction("Center", self)
        act_center.triggered.connect(lambda: self._apply_align("center"))
        toolbar.addAction(act_center)
        
        act_right = QAction("Right", self)
        act_right.triggered.connect(lambda: self._apply_align("right"))
        toolbar.addAction(act_right)
        
        toolbar.addSeparator()

        # --- Sort ---
        act_sort_asc = QAction("↓A-Z", self)
        act_sort_asc.setToolTip("Sort Ascending")
        act_sort_asc.triggered.connect(lambda: self._sort_selection(True))
        toolbar.addAction(act_sort_asc)

        act_sort_desc = QAction("↓Z-A", self)
        act_sort_desc.setToolTip("Sort Descending")
        act_sort_desc.triggered.connect(lambda: self._sort_selection(False))
        toolbar.addAction(act_sort_desc)
        
        toolbar.addSeparator()

        # --- Find & Replace ---
        act_find = QAction("🔍", self)
        act_find.setToolTip("Find (Ctrl+F)")
        act_find.setShortcut("Ctrl+F")
        act_find.triggered.connect(lambda: self._launch_find_replace("find"))
        toolbar.addAction(act_find)
        
        act_replace = QAction("✎", self)
        act_replace.setToolTip("Replace (Ctrl+H)")
        act_replace.setShortcut("Ctrl+H")
        act_replace.triggered.connect(lambda: self._launch_find_replace("replace"))
        toolbar.addAction(act_replace)
        
        toolbar.addSeparator()

        # --- Conditional Formatting ---
        btn_cond = QToolButton()
        btn_cond.setText("Cond")
        btn_cond.setToolTip("Conditional Formatting")
        btn_cond.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu_cond = QMenu(btn_cond)
        
        act_gt = QAction("Greater Than...", self)
        act_gt.triggered.connect(lambda: self._add_conditional_rule("GT"))
        menu_cond.addAction(act_gt)
        
        act_lt = QAction("Less Than...", self)
        act_lt.triggered.connect(lambda: self._add_conditional_rule("LT"))
        menu_cond.addAction(act_lt)
        
        act_contains = QAction("Text Contains...", self)
        act_contains.triggered.connect(lambda: self._add_conditional_rule("CONTAINS"))
        menu_cond.addAction(act_contains)
        
        menu_cond.addSeparator()
        
        act_clear_rules = QAction("Clear All Rules", self)
        act_clear_rules.triggered.connect(self._clear_conditional_rules)
        menu_cond.addAction(act_clear_rules)
        
        btn_cond.setMenu(menu_cond)
        toolbar.addWidget(btn_cond)

        toolbar.addSeparator()

        # --- Virtual Keyboard ---
        act_keyboard = QAction("⌨ Keyboard", self)
        act_keyboard.setToolTip("Open Virtual Keyboard (Hebrew/Greek)")
        act_keyboard.triggered.connect(self._toggle_keyboard)
        toolbar.addAction(act_keyboard)

        toolbar.addSeparator()

        # --- Borders ---
        # Menu for border options
        btn_border = QToolButton()
        btn_border.setText("⊞")
        btn_border.setToolTip("Borders")
        btn_border.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar.addWidget(btn_border)
        
        self.border_menu = QMenu(self)
        btn_border.setMenu(self.border_menu)
        
        # State for next border application
        self._border_settings = {
            "color": "#000000",
            "style": "solid", # solid, dash, dot
            "width": 1
        }
        
        # Apply Actions
        self.border_actions = []
        actions_data = [
            ("All Borders", "all"),
            ("No Borders", "none"),
            ("Outside Borders", "outside"),
            ("Top Border", "top"),
            ("Bottom Border", "bottom"),
            ("Left Border", "left"),
            ("Right Border", "right"),
        ]
        
        # Inline helper for simple apply
        def _set_border(type_):
            self._apply_borders(type_)
        
        for name, key in actions_data:
            act = QAction(name, self)
            act.triggered.connect(lambda checked, k=key: _set_border(k))
            self.border_menu.addAction(act)
            self.border_actions.append(act)
            
        self.border_menu.addSeparator()
        
        # Settings Actions (Color, Style, Width)
        self.border_style_actions = []
        
        act_color = QAction("Line Color...", self)
        act_color.triggered.connect(self.pick_border_color)
        self.border_menu.addAction(act_color)
        self.border_style_actions.append(act_color)
        
        style_menu = self.border_menu.addMenu("Line Style")
        self.border_style_menu = style_menu
        self.border_width_menu = width_menu = self.border_menu.addMenu("Line Width")
        
        for s in ["solid", "dash", "dot"]:
            a = QAction(s.title(), self)
            # Use self.set_border_style directly
            a.triggered.connect(lambda checked, style=s: self.set_border_style(style))
            style_menu.addAction(a)
            
        for w in [1, 2, 3, 4, 5]:
            a = QAction(f"{w}px", self)
            a.triggered.connect(lambda checked, width=w: self.set_border_width(width))
            self.border_width_menu.addAction(a)

        # Pass to View
        self.view.set_border_ui(self.border_actions, [act_color], style_menu, self.border_width_menu)



    def _on_formula_return(self):
        """Commit Formula Bar content to selected cell."""
        text = self.formula_bar.text()
        idx = self.view.currentIndex()
        if idx.isValid():
            self.model.setData(idx, text, Qt.ItemDataRole.EditRole)
            self.view.setFocus()

    def _update_toolbar_state(self, index):
        """Renamed from old logic inside _on_selection_changed"""
        font = self.model.data(index, Qt.ItemDataRole.FontRole)
        if font:
            self.font_combo.blockSignals(True)
            self.font_combo.setCurrentFont(font)
            self.font_combo.blockSignals(False)
            
            self.size_spin.blockSignals(True)
            self.size_spin.setValue(font.pointSize())
            self.size_spin.blockSignals(False)
            
            self.act_bold.blockSignals(True)
            self.act_bold.setChecked(font.bold())
            self.act_bold.blockSignals(False)
            
            self.act_italic.blockSignals(True)
            self.act_italic.setChecked(font.italic())
            self.act_italic.blockSignals(False)
            
            self.act_underline.blockSignals(True)
            self.act_underline.setChecked(font.underline())
            self.act_underline.blockSignals(False)
        else:
             self.act_bold.setChecked(False)
             self.act_italic.setChecked(False)
             self.act_underline.setChecked(False)

    def _save_table(self):
        """Persist to Database (Multi-Scroll)."""
        try:
            # Serialize all scrolls
            scrolls_list = []
            for m in self.models:
                # model.to_json() returns {columns, data, styles}. We need to add name.
                json_data = m.to_json()
                json_data["name"] = getattr(m, "scroll_name", "Sheet")
                scrolls_list.append(json_data)
                
            final_content = {
                "format_version": "2.0",
                "active_scroll_index": self.current_model_index,
                "scrolls": scrolls_list
            }
            
            self.service.save_content(self.table_id, final_content)
            self.statusBar().showMessage("Tablet saved successfully.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))
            # import traceback
            # traceback.print_exc()
            
    # --- Formatting Helpers ---
    def _apply_borders(self, border_type):
        from .spreadsheet_view import BorderRole
        from ..services.border_engine import BorderEngine
        
        indexes = self.view.selectionModel().selectedIndexes()
        if not indexes: return
        
        print(f"[DEBUG] Apply Borders: Type={border_type}, Settings={self._border_settings}")
        
        # Delegate Calculation
        updates = BorderEngine.calculate_borders(
            self.model, indexes, border_type, self._border_settings, BorderRole
        )
        
        if not updates: return
        
        self.model.undo_stack.beginMacro(f"Set Border {border_type}")
        try:
            for idx, new_borders in updates:
                self.model.setData(idx, new_borders, BorderRole)
        finally:
            self.model.undo_stack.endMacro()

    def _update_selected_borders(self):
        """
        Smart Update: If selected cells ALREADY have borders, update their style/width/color.
        """
        from .spreadsheet_view import BorderRole
        from ..services.border_engine import BorderEngine
        
        indexes = self.view.selectionModel().selectedIndexes()
        if not indexes: return

        # Delegate Calculation
        updates = BorderEngine.update_existing_borders(
            self.model, indexes, self._border_settings, BorderRole
        )
        
        if not updates: return

        # We don't necessarily start a macro here? 
        # But changing border settings usually implies a user interaction that might need undo.
        # But this is triggered by "Settings Change" which might be separate from "Validation".
        # Yes, let's allow undo.
        self.model.undo_stack.beginMacro("Update Border Style")
        try:
            for idx, new_borders in updates:
                self.model.setData(idx, new_borders, BorderRole)
        finally:
            self.model.undo_stack.endMacro()

    # --- Formatting Logic ---
    
    def _apply_cell_property(self, role, value, description):
        """
        The Universal Formatter.
        Applies a specific value to a specific Role for all selected cells,
        wrapped in an Undo Macro. E.g. Set Bold, Set Color, Set Align.
        """
        indexes = self.view.selectionModel().selectedIndexes()
        if not indexes: return

        self.model.undo_stack.beginMacro(description)
        try:
            for idx in indexes:
                if idx.isValid():
                    self.model.setData(idx, value, role)
        finally:
            self.model.undo_stack.endMacro()

    def _apply_to_selection(self, action_name, func, *args):
        """
        Helper for complex operations (like Borders) that need read-modify-write logic.
        """
        indexes = self.view.selectionModel().selectedIndexes()
        if not indexes: return

        self.model.undo_stack.beginMacro(action_name)
        try:
            for idx in indexes:
                if idx.isValid():
                    func(idx, *args)
        finally:
            self.model.undo_stack.endMacro()

    def _apply_style(self, style_type, checked):
        mapping = {
            "bold": ("bold", checked),
            "italic": ("italic", checked),
            "underline": ("underline", checked)
        }
        if style_type in mapping:
            self._apply_cell_property(Qt.ItemDataRole.FontRole, mapping[style_type], f"Apply {style_type}")

    def _apply_align(self, align):
        self._apply_cell_property(Qt.ItemDataRole.TextAlignmentRole, align, f"Align {align}")

    def _on_font_family_changed(self, font):
        self._apply_cell_property(Qt.ItemDataRole.FontRole, ("font_family", font.family()), f"Font Family {font.family()}")

    def _on_font_size_changed(self, size):
        self._apply_cell_property(Qt.ItemDataRole.FontRole, ("font_size", size), f"Font Size {size}")

    def _pick_color(self, target):
        color = QColorDialog.getColor()
        if not color.isValid():
            return
        hex_color = color.name() # setData Command handles name() extraction or we pass QColor directly?
        # Use QColor directly as setData supports it or let Command handle it.
        # Window logic: let's pass QColor object for consistency with type.
        
        if target == "background":
            self._apply_cell_property(Qt.ItemDataRole.BackgroundRole, color, "Set Background Color")
        elif target == "text":
            self._apply_cell_property(Qt.ItemDataRole.ForegroundRole, color, "Set Text Color")

    def _apply_color(self, target, hex_color):
        # Legacy stub if needed, but _pick_color now handles it directly.
        pass

    def _on_selection_changed(self, current, previous):
        """
        Updates the formula bar with the current cell's content,
        UNLESS we are in formula edit mode.
        Also updates the Name Box.
        """
        # Always update Name Box
        if current.isValid():
            def col_to_letter(col_idx):
                """
                Col to letter logic.
                
                Args:
                    col_idx: Description of col_idx.
                
                """
                res = ""
                while col_idx >= 0:
                    res = chr((col_idx % 26) + 65) + res
                    col_idx = (col_idx // 26) - 1
                return res
            addr = f"{col_to_letter(current.column())}{current.row() + 1}"
            self.name_box.setText(addr)
        else:
            self.name_box.setText("")

        # Formatting update
        self._update_toolbar_state(current)
        
        # Force redraw to clear artifacts
        self.view.viewport().update()

        if self._is_editing_formula:
            return

        if current.isValid():
            val = self.model.data(current, Qt.ItemDataRole.EditRole)
            self.formula_bar.blockSignals(True)
            self.formula_bar.setText(str(val) if val is not None else "")
            self.formula_bar.blockSignals(False)
            
    def _on_range_selection_changed(self, selected, deselected):
        """
        If in formula edit mode, inserting range references.
        """
        if not self._is_editing_formula:
            return
            
        indexes = self.view.selectionModel().selectedIndexes()
        if not indexes: return

        # 1. Calculate Range String
        min_row = min(idx.row() for idx in indexes)
        max_row = max(idx.row() for idx in indexes)
        min_col = min(idx.column() for idx in indexes)
        max_col = max(idx.column() for idx in indexes)
        
        def col_to_letter(col_idx):
            """
            Col to letter logic.
            
            Args:
                col_idx: Description of col_idx.
            
            """
            res = ""
            while col_idx >= 0:
                res = chr((col_idx % 26) + 65) + res
                col_idx = (col_idx // 26) - 1
            return res
            
        start_addr = f"{col_to_letter(min_col)}{min_row + 1}"
        if min_row == max_row and min_col == max_col:
            ref_str = start_addr
        else:
            end_addr = f"{col_to_letter(max_col)}{max_row + 1}"
            ref_str = f"{start_addr}:{end_addr}"
        
        # 2. Insert into Formula Bar
        cursor = self.formula_bar.cursorPosition()
        text = self.formula_bar.text()
        
        # Simple Insert
        # Ideally we replace the previous ref if we are "drag-updating", but simple insert is safer for V1.
        # But wait, if I drag A1:B2, standard excel updates the ONE ref.
        # Without tokenizer state, that's hard.
        # Let's just assume the user wants to Insert.
        
        new_text = text[:cursor] + ref_str + text[cursor:]
        self.formula_bar.setText(new_text)
        self.formula_bar.setCursorPosition(cursor + len(ref_str))
        
        # Return focus to bar
        self.formula_bar.setFocus()

    def _on_formula_text_edited(self, text):
        """Detect if user is starting a formula."""
        if text.startswith("="):
            if not self._is_editing_formula:
                # Enter Edit Mode
                self._is_editing_formula = True
                self._edit_source_index = self.view.currentIndex()
        else:
            if self._is_editing_formula and not text.startswith("="):
                self._is_editing_formula = False
                self._edit_source_index = None

    def _on_formula_return(self):
        """Commit the formula."""
        text = self.formula_bar.text()
        
        # Target: explicit edit source OR current selection
        target = self._edit_source_index if (self._is_editing_formula and self._edit_source_index) else self.view.currentIndex()
        
        # Reset State BEFORE changing selection/focus to prevent accidental formula appends
        self._is_editing_formula = False
        self._edit_source_index = None

        if target.isValid():
            self.model.setData(target, text, Qt.ItemDataRole.EditRole)
            # Restore selection to target (since clicking modified it)
            self.view.setCurrentIndex(target)
            self.view.setFocus()

    def _on_scroll_added(self):
        """Create a new scroll."""
        new_name, ok = QInputDialog.getText(self, "New Scroll", "Scroll Name:", text="Sheet")
        if not ok or not new_name: return
        
        content = self._create_default_content()
        m = SpreadsheetModel(content)
        m.scroll_name = new_name
        
        self.models.append(m)
        self.tab_bar.add_tab(new_name)
        
        # Switch to it
        self.tab_bar.set_current_index(len(self.models) - 1)
        
    def _on_scroll_changed(self, index):
        """Switch the active view model."""
        if index < 0 or index >= len(self.models): return
        
        # 1. Disconnect old
        try: self.model.dataChanged.disconnect(self._on_data_changed)
        except: pass
        
        # 2. Switch
        self.current_model_index = index
        self.model = self.models[index]
        self.view.setModel(self.model)
        
        # 3. Connect new
        self.model.dataChanged.connect(self._on_data_changed)
        
        # 4. Refresh UI State
        # Ensure we don't have invalid selection
        self.view.clearSelection()
        self._update_toolbar_state(self.view.currentIndex())
        self.name_box.setText("")
        self.formula_bar.setText("")
        
    def _create_default_content(self):
        # 26 Columns (A-Z)
        cols = [chr(65 + i) for i in range(26)]
        # 100 empty rows of similar width
        # Data format is list of lists
        data = [["" for _ in cols] for _ in range(100)]
        return {
            "columns": cols,
            "data": data,
            "styles": {}
        }

    def _on_data_changed(self, top_left, bottom_right, roles=None):
        """
        If the data in the currently selected cell changes (e.g. via inline edit), 
        update the formula bar to reflect it.
        """
        current = self.view.currentIndex()
        if not current.isValid():
            return
            
        # Check if current index is within the changed range
        if (top_left.row() <= current.row() <= bottom_right.row() and 
            top_left.column() <= current.column() <= bottom_right.column()):
            
            # Update Formula Bar
            raw_data = str(self.model.data(current, Qt.ItemDataRole.EditRole) or "")
            if self.formula_bar.text() != raw_data:
                self.formula_bar.blockSignals(True)
                self.formula_bar.setText(raw_data)
                self.formula_bar.blockSignals(False)

    # --- Border Settings Methods (Instance) ---
    def set_border_style(self, style):
        """
        Configure border style logic.
        
        Args:
            style: Description of style.
        
        """
        self._border_settings["style"] = style
        self.statusBar().showMessage(f"Border Style set to {style.title()}", 3000)
        self._update_selected_borders()

    def set_border_width(self, width):
        """
        Configure border width logic.
        
        Args:
            width: Description of width.
        
        """
        self._border_settings["width"] = width
        self.statusBar().showMessage(f"Border Width set to {width}px", 3000)
        self._update_selected_borders()
        
    def pick_border_color(self):
        """
        Pick border color logic.
        
        """
        c = QColorDialog.getColor()
        if c.isValid():
            self._border_settings["color"] = c.name()
            self.statusBar().showMessage(f"Border Color set to {c.name()}", 3000)
            self._update_selected_borders()
    def _toggle_keyboard(self):
        """Toggle Virtual Keyboard in/out."""
        if self._kb_dock.isVisible():
            self._kb_dock.hide()
        else:
            self._kb_dock.show()

    def _sort_selection(self, ascending=True):
        """
        Sorts the current selection based on the active cell's column.
        """
        selection = self.view.selectionModel()
        if not selection.hasSelection():
            # If nothing selected, maybe select used range?
            # Or assume user wants to sort used range?
            # For safety, require selection or single cell expands to used range?
            # Let's require selection for now to be safe.
            return
            
        indexes = selection.selectedIndexes()
        if not indexes: return
        
        # Calculate Bounding Rect
        rows = [i.row() for i in indexes]
        cols = [i.column() for i in indexes]
        
        top, bottom = min(rows), max(rows)
        left, right = min(cols), max(cols)
        
        # Sort Key: Active Cell Column
        # If active cell is outside range (possible with Ctrl+Click), default to Left column.
        current = self.view.currentIndex()
        key_col = current.column()
        
        if key_col < left or key_col > right:
            key_col = left
            
        self.model.sort_range(top, left, bottom, right, key_col, ascending)
        
    def _add_conditional_rule(self, rule_type):
        """Adds a conditional rule to the selected range."""
        selection = self.view.selectionModel()
        if not selection.hasSelection(): return

        # 1. Ask for Value
        label = "Value:"
        if rule_type == "GT": label = "Greater Than:"
        if rule_type == "LT": label = "Less Than:"
        if rule_type == "CONTAINS": label = "Text Contains:"
        
        val_str, ok = QInputDialog.getText(self, "Conditional Rule", label)
        if not ok or not val_str: return
        
        # 2. Ask for Color (Simple for now: Default Red, or ask?)
        # Let's default to Light Red Fill + Dark Red Text (Excel style)
        # bg: #FFC7CE, fg: #9C0006
        style = {"bg": "#FFC7CE", "fg": "#9C0006"}
        
        # 3. Calculate Ranges
        indexes = selection.selectedIndexes()
        rows = [i.row() for i in indexes]
        cols = [i.column() for i in indexes]
        # Bounding box is safest for rule storage, though irregular selection possible.
        # We store bounding box for now.
        t, b = min(rows), max(rows)
        l, r = min(cols), max(cols)
        
        rule = ConditionalRule(
            rule_type=rule_type,
            value=val_str,
            format_style=style,
            ranges=[(t, l, b, r)]
        )
        
        # 4. Add to Manager
        if hasattr(self.model, "conditional_manager"):
            self.model.conditional_manager.add_rule(rule)
            # Repaint
            self.view.viewport().update()
            
            # Repaint
            self.view.viewport().update()
            
    def _clear_conditional_rules(self):
        """Removes all conditional formatting rules."""
        if hasattr(self.model, "conditional_manager"):
            self.model.conditional_manager.clear_all_rules()
            self.view.viewport().update()
            self.statusBar().showMessage("Cleared all Conditional Formatting rules.", 3000)

    def _export_csv(self):
        """Export grid to CSV (Values or Formulas)."""
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if not path: return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                rows = self.model.rowCount()
                cols = self.model.columnCount()
                
                for r in range(rows):
                    row_data = []
                    for c in range(cols):
                        idx = self.model.index(r, c)
                        val = self.model.data(idx, Qt.ItemDataRole.EditRole)
                        row_data.append(val if val is not None else "")
                    writer.writerow(row_data)
                    
            QMessageBox.information(self, "Export Successful", f"Saved to {path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def _import_csv(self):
        """Import CSV to grid (Resizes grid to fit)."""
        path, _ = QFileDialog.getOpenFileName(self, "Import CSV", "", "CSV Files (*.csv)")
        if not path: return
        
        try:
            with open(path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
            if not rows: return
            
            # 1. Resize Grid
            r_count = len(rows)
            c_count = max(len(r) for r in rows) if rows else 0
            
            current_rows = self.model.rowCount()
            current_cols = self.model.columnCount()
            
            # Add Rows
            if r_count > current_rows:
                self.model.insertRows(current_rows, r_count - current_rows)
                
            # Add Cols
            if c_count > current_cols:
                self.model.insertColumns(current_cols, c_count - current_cols)
            
            # 2. Populate
            for r, row_list in enumerate(rows):
                for c, val in enumerate(row_list):
                    idx = self.model.index(r, c)
                    self.model.setData(idx, val, Qt.ItemDataRole.EditRole)
                    
            QMessageBox.information(self, "Import Successful", f"Loaded {r_count}x{c_count} grid.")
            
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", str(e))

    # --- Find & Replace ---

    def _launch_find_replace(self, mode="find"):
        if not hasattr(self, '_find_dialog'):
            self._find_dialog = FindReplaceDialog(self)
            self._find_dialog.find_next_requested.connect(self._on_find_next)
            self._find_dialog.find_all_requested.connect(self._on_find_all)
            self._find_dialog.replace_requested.connect(self._on_replace)
            self._find_dialog.replace_all_requested.connect(self._on_replace_all)
            self._find_dialog.navigation_requested.connect(self._on_navigate_to_result)
            
        if mode == "replace":
            self._find_dialog.show_replace_mode()
        else:
            self._find_dialog.show_find_mode()

    def _on_navigate_to_result(self, index):
        """Called when user clicks a result in the Find Dialog."""
        if index.isValid():
            self.view.setCurrentIndex(index)
            self.view.scrollTo(index)
            self.view.setFocus()

    def _find_matching_indexes(self, text, options, start_from=None, reverse=False):
        """Helper to iterate grid and yield matches."""
        case_sensitive = options.get("case_sensitive", False)
        match_entire = options.get("match_entire", False)
        target = text if case_sensitive else text.lower()
        
        rows = self.model.rowCount()
        cols = self.model.columnCount()
        
        # Order: Row-Major (A1, B1, C1...)
        # We need to construct a list of ALL indexes, then cycle/slice based on start_from
        all_indexes = []
        for r in range(rows):
            for c in range(cols):
                all_indexes.append(self.model.index(r, c))
                
        # If start_from is provided, rotate list so start_from is last (finding next starts at index+1)
        if start_from and start_from.isValid():
             # Find index in list
             # This is slow O(N) but grid is small enough? 100x26 = 2600. Fast.
             try:
                 # Comparison of QModelIndex might need row/col check
                 start_idx = (start_from.row() * cols) + start_from.column()
                 # Rotate: start checking from start_idx + 1
                 all_indexes = all_indexes[start_idx+1:] + all_indexes[:start_idx+1]
             except:
                 pass
                 
        for idx in all_indexes:
            val = self.model.data(idx, Qt.ItemDataRole.DisplayRole)
            if val is None: val = ""
            val_str = str(val)
            check_val = val_str if case_sensitive else val_str.lower()
            
            match = False
            if match_entire:
                match = (check_val == target)
            else:
                match = (target in check_val)
                
            if match:
                yield idx

    def _on_find_next(self, text, options):
        current = self.view.currentIndex()
        # Generator
        gen = self._find_matching_indexes(text, options, start_from=current)
        try:
            next_idx = next(gen)
            self.view.setCurrentIndex(next_idx)
            self.view.scrollTo(next_idx)
        except StopIteration:
            QMessageBox.information(self, "Find", f"Cannot find '{text}'.")

    def _on_find_all(self, text, options):
        gen = self._find_matching_indexes(text, options, start_from=None)
        
        # Collect all
        matches = list(gen)
        
        # Prepare for Dialog List
        results_data = []
        
        def col_to_letter(col_idx):
             """
             Col to letter logic.
             
             Args:
                 col_idx: Description of col_idx.
             
             """
             res = ""
             while col_idx >= 0:
                 res = chr((col_idx % 26) + 65) + res
                 col_idx = (col_idx // 26) - 1
             return res
             
        for idx in matches:
            addr = f"{col_to_letter(idx.column())}{idx.row() + 1}"
            val = str(self.model.data(idx, Qt.ItemDataRole.DisplayRole) or "")
            # Truncate content for display
            display = f"{addr}: {val}"
            results_data.append((display, idx))
            
        # Send to Dialog
        if hasattr(self, '_find_dialog'):
            self._find_dialog.show_results(results_data)

        if not matches:
             QMessageBox.information(self, "Find", f"Cannot find '{text}'.")
             return
             
        # Select all in Grid
        selection = self.view.selectionModel()
        selection.clearSelection()
        
        from PyQt6.QtCore import QItemSelection, QItemSelectionRange
        qt_selection = QItemSelection()
        for idx in matches:
            qt_selection.select(idx, idx)
            
        selection.select(qt_selection, selection.SelectionFlag.Select)
        
        self.statusBar().showMessage(f"Found {len(matches)} occurrences.", 5000)

    def _on_replace(self, text, replacement, options):
        """Replace current selection if matches, then find next."""
        current = self.view.currentIndex()
        
        # Check if current matches
        matches_current = False
        if current.isValid():
             # Re-verify match
             case_sensitive = options.get("case_sensitive", False)
             match_entire = options.get("match_entire", False)
             val = str(self.model.data(current, Qt.ItemDataRole.DisplayRole) or "")
             target = text if case_sensitive else text.lower()
             check = val if case_sensitive else val.lower()
             
             if match_entire: matches_current = (check == target)
             else: matches_current = (target in check)
        
        if matches_current:
            # Perform replacement
            # If partial match, replace substring. If full match/entire, replace whole.
            val = str(self.model.data(current, Qt.ItemDataRole.DisplayRole) or "")
            
            if match_entire:
                new_val = replacement
            else:
                # String replace
                if not options.get("case_sensitive"):
                    # Case insensitive replace is tricky in Python str.replace
                    # Simple approach: re or simple replace (user expects partial case match?)
                    # Let's stick to simple literal replace if insensitive?
                    # text="abc", val="AbcDef", replace="aaa" -> "aaaDef"?
                    # Python .replace() is case sensitive.
                    
                    # Regex replace for case insensitive
                    import re
                    pattern = re.compile(re.escape(text), re.IGNORECASE)
                    new_val = pattern.sub(replacement, val)
                else:
                    new_val = val.replace(text, replacement)
            
            self.model.setData(current, new_val, Qt.ItemDataRole.EditRole)
            
        # Move to next
        self._on_find_next(text, options)

    def _on_replace_all(self, text, replacement, options):
        gen = self._find_matching_indexes(text, options, start_from=None)
        matches = list(gen)
        
        if not matches:
            QMessageBox.information(self, "Replace", f"Cannot find '{text}'.")
            return
            
        self.model.undo_stack.beginMacro("Replace All")
        count = 0
        try:
            import re
            pattern = re.compile(re.escape(text), re.IGNORECASE) if not options.get("case_sensitive") else None
            
            for idx in matches:
                val = str(self.model.data(idx, Qt.ItemDataRole.DisplayRole) or "")
                
                if options.get("match_entire"):
                    new_val = replacement
                else:
                    if pattern:
                        new_val = pattern.sub(replacement, val)
                    else:
                        new_val = val.replace(text, replacement)
                        
                if val != new_val:
                    self.model.setData(idx, new_val, Qt.ItemDataRole.EditRole)
                    count += 1
        finally:
            self.model.undo_stack.endMacro()
            
        self.statusBar().showMessage(f"Replaced {count} occurrences.", 5000)