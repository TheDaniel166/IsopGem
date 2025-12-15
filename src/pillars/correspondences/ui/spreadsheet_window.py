
from PyQt6.QtWidgets import (
    QMainWindow, QToolBar, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QFontComboBox, QSpinBox, QLabel, QColorDialog, QToolButton, QMenu, QLineEdit, QStyle
)
from PyQt6.QtGui import QAction, QIcon, QFont, QColor
from PyQt6.QtCore import Qt, QSize, QEvent
import re

from .spreadsheet_view import SpreadsheetView, SpreadsheetModel
from shared.ui.virtual_keyboard import get_shared_virtual_keyboard

class SpreadsheetWindow(QMainWindow):
    """
    The Sovereign Window.
    Hosts the Grid and the Toolbar (commands).
    """
    def __init__(self, table_id, name, content, repo, parent=None):
        super().__init__(parent)
        self.table_id = table_id
        self.repo = repo
        self.setWindowTitle(f"Emerald Tablet: {name}")
        self.resize(1200, 800)

        # 1. Setup Model & View
        self.model = SpreadsheetModel(content)
        self.view = SpreadsheetView(self)
        self.view.setModel(self.model)
        self.view.setShowGrid(False) # Set showGrid to False

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
        
        self.setCentralWidget(self.container)
        
        # Connect Selection Sync
        self.view.selectionModel().currentChanged.connect(self._on_selection_changed)
        self.view.selectionModel().selectionChanged.connect(self._on_range_selection_changed)
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
        
        # 4. Unify Workflow: Listen for inline editor
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
        self.act_underline.setCheckable(True)
        self.act_underline.triggered.connect(lambda c: self._apply_style("underline", c))
        toolbar.addAction(self.act_underline)
        
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
        
        act_right = QAction("Right", self)
        act_right.triggered.connect(lambda: self._apply_align("right"))
        toolbar.addAction(act_right)
        
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
        """Persist to Database."""
        try:
            content = self.model.to_json()
            # Fix for 'TableRepository' object has no attribute 'update_content'
            self.repo.update_content(self.table_id, content)
            self.statusBar().showMessage(f"Saved update at {content.get('updated_at', 'now')}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))
            
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
        self._border_settings["style"] = style
        self.statusBar().showMessage(f"Border Style set to {style.title()}", 3000)
        self._update_selected_borders()

    def set_border_width(self, width):
        self._border_settings["width"] = width
        self.statusBar().showMessage(f"Border Width set to {width}px", 3000)
        self._update_selected_borders()
        
    def pick_border_color(self):
        c = QColorDialog.getColor()
        if c.isValid():
            self._border_settings["color"] = c.name()
            self.statusBar().showMessage(f"Border Color set to {c.name()}", 3000)
            self._update_selected_borders()
        


    def _toggle_keyboard(self):
        """Toggle the virtual keyboard linked to the formula bar."""
        kb = get_shared_virtual_keyboard()
        kb.set_target_input(self.formula_bar)
        
        if kb.isVisible():
            kb.hide()
        else:
            kb.show()
            kb.raise_()
            kb.activateWindow()
