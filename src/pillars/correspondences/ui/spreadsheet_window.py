# Spreadsheet Window - The Sovereign Tablet Editor.
# Main window hosting the spreadsheet view, formula bar, toolbar, and multi-sheet tab navigation. 

from typing import Any, Dict, List, Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QDockWidget,
    QToolBar, QMessageBox, QMenu, QToolButton, QStyle,
    QLineEdit, QInputDialog
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QEvent, QSize, QModelIndex

from .spreadsheet_view import SpreadsheetView, SpreadsheetModel
from .scroll_tab_bar import ScrollTabBar
from ..services.table_service import TableService

from pillars.correspondences.services.conditional_formatting import ConditionalRule
from shared.ui.virtual_keyboard import get_shared_virtual_keyboard
from shared.ui.theme import COLORS

# New Components
from .components.formula_bar import FormulaBarWidget
from .components.status_bar import SpreadsheetStatusBar
from ..services.spreadsheet_io import SpreadsheetIO
from .components.search_handler import SearchHandler
from .components.style_handler import StyleHandler
from .components.formula_wizard_handler import FormulaWizardHandler
from ..services.formula_helper import col_to_letter, cell_address, get_reference_cells

class SpreadsheetWindow(QMainWindow):
    # The Sovereign Window.
    # Hosts the Grid and the Toolbar (commands).

    def __init__(self, table_id: int, name: str, content: Dict[str, Any], service: TableService, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        # init logic.
        
        # Args:
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
        
        # 2a. Formula Bar (Component)
        self.formula_bar_widget = FormulaBarWidget()
        self.formula_bar_widget.text_changed.connect(self._on_formula_text_edited)
        self.formula_bar_widget.return_pressed.connect(self._on_formula_return)
        
        # Connect Name Box if we moved it? 
        # Actually in the new component we didn't include Name Box logic.
        # Let's keep Name Box in Window for now, or move it to component in next pass.
        # For now, let's just add the component.
        
        # Note: The component is defined to just have fx label and editor.
        # We need to integrate the Name Box (which is still in Window logic).
        
        # Formula Area Container
        formula_area = QWidget()
        fb_layout = QHBoxLayout(formula_area)
        fb_layout.setContentsMargins(4, 4, 4, 4)
        fb_layout.setSpacing(4)
        
        # Name Box (e.g. A1) - Kept in Window for orchestrator access
        self.name_box = QLineEdit()
        self.name_box.setReadOnly(True)
        self.name_box.setFixedWidth(80) 
        self.name_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_box.setPlaceholderText("A1")
        self.name_box.setStyleSheet("font-weight: bold; padding-left: 4px; padding-right: 4px;")
        
        fb_layout.addWidget(self.name_box)
        fb_layout.addWidget(self.formula_bar_widget)
        
        self.central_layout.addWidget(formula_area)
        self.central_layout.addWidget(self.view)
        
        # Map old self.formula_bar to the new editor for compatibility
        # This allows existing methods like setText to work if we proxy it
        # or we just update the methods. Let's update the methods.
        self.formula_bar = self.formula_bar_widget
        
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
             names = [m.scroll_name for m in self.models]  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
             self.tab_bar.update_menu(names)
             self.tab_bar.btn_menu.showMenu()
        self.tab_bar.btn_menu.clicked.connect(_show_all_sheets_menu)

        self.setCentralWidget(self.container)
        
        # Connect Selection Sync
        self.view.selectionModel().currentChanged.connect(self._on_selection_changed)
        self.view.selectionModel().selectionChanged.connect(self._on_range_selection_changed)
        # Connect ONLY current model initialy
        self.model.dataChanged.connect(self._on_data_changed)  # type: ignore[reportUnknownMemberType]
        
        # State for point-and-click references
        self._is_editing_formula = False
        self._ref_mode = True # True = Enter Mode (Arrows navigate), False = Edit Mode (Arrows cursor)
        self._edit_source_index = None # The index we are editing (e.g. A1) while clicking B2
        self._phantom_ref_cursor = None # Virtual cursor for arrow navigation (keeps editor open)
        
        # Track manual edits to detect '=' (Signal already connected via text_changed above)
        # REMOVED: self.formula_bar.textEdited.connect(self._on_formula_text_edited)
        
        # 3. Toolbar
        self._setup_toolbar()
        
        # 4. Keyboard Dock (Hidden by default)
        self._kb_dock = QDockWidget("Virtual Keyboard", self)
        self._kb_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self._kb_dock.setWidget(get_shared_virtual_keyboard(self))
        self._kb_dock.hide()
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._kb_dock)
        
        # 5. Unify Workflow: Listen for inline editor
        self.view.editor_text_changed.connect(self._on_inline_text_edited)
        self.view.viewport().installEventFilter(self)
        
        # Also install event filter on formula bar for focus changes
        self.formula_bar_widget.editor.installEventFilter(self)
        
        # 6. Status Bar
        self.status_bar = SpreadsheetStatusBar()
        self.status_bar.zoom_changed.connect(self._on_zoom_changed)
        self.setStatusBar(self.status_bar) 

        # 7. Search Handler
        self.search_handler = SearchHandler(self)

        # 8. Style Handler
        self.style_handler = StyleHandler(self)

        # 9. Wizard Handler
        self.wizard_handler = FormulaWizardHandler(self)
        
        # Connect fx button to Formula Wizard
        self.formula_bar_widget.fx_clicked.connect(self.wizard_handler.launch)
        
        # 10. Zoom state - track base sizes for scaling
        self._base_row_height = 25
        self._base_font_size = 10
        self._current_zoom = 100

    def _on_zoom_changed(self, value: int) -> None:
        """Scales the view by adjusting row heights and font size."""
        self._current_zoom = value
        scale = value / 100.0
        
        # 1. Scale row heights
        new_row_height = int(self._base_row_height * scale)
        header = self.view.verticalHeader()
        header.setDefaultSectionSize(new_row_height)
        
        # 2. Scale default font size for new cells
        font = self.view.font()
        font.setPointSize(int(self._base_font_size * scale))
        self.view.setFont(font)
        
        # 3. Force repaint
        self.view.viewport().update()

    def show_status(self, message: str, timeout: int = 0) -> None:
        # Proxy to our component
        self.status_bar.show_message(message, timeout)

    # Override standard statusBar() usage if possible or replace calls?
    # We can replace internal calls to self.status_bar.show_message using regex or manual replace.

    def _is_in_formula_composition_mode(self) -> bool:
        """
        Unified check for formula composition mode.
        
        Returns True when:
        - Formula bar has focus AND text starts with '='
        - OR inline editor is active AND text starts with '='
        
        This mirrors Excel/Google Sheets behavior where cell clicks
        insert references instead of changing selection.
        """
        text = self.formula_bar.text()
        if not text.startswith("="):
            return False
        
        formula_bar_focused = self.formula_bar_widget.hasFocus()
        inline_editor_active = self._is_editing_formula
        
        return formula_bar_focused or inline_editor_active

    def _update_composition_mode_visuals(self) -> None:
        """Update visual indicators based on formula composition state."""
        in_composition = self._is_in_formula_composition_mode()
        
        # Update formula bar glow
        self.formula_bar_widget.set_composition_mode(in_composition)
        
        # Update status bar indicator
        self.status_bar.set_ref_mode(in_composition)

    def eventFilter(self, source: Any, event: QEvent) -> bool:
        # A. Mouse Click Logic - Unified Formula Composition Mode
        if source == self.view.viewport() and event.type() == QEvent.Type.MouseButtonPress:
            # Check unified composition mode (formula bar OR inline editor with '=' prefix)
            if self._is_in_formula_composition_mode():
                # Calculate cell under mouse
                pos = event.pos()  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
                index = self.view.indexAt(pos)
                
                # Check if we clicked the cell we are editing (Source)
                is_source = (index == self._edit_source_index)
                
                if index.isValid() and not is_source:
                    # Insert Reference
                    self._insert_reference_at_cursor(index)
                    return True  # Consume event - don't change selection
                
        # B. Key Press Logic (Navigation)
        if event.type() == QEvent.Type.KeyPress:
            # 1. Toggle Mode (Ctrl+E)
            if event.key() == Qt.Key.Key_E and event.modifiers() & Qt.KeyboardModifier.ControlModifier:  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
                self._ref_mode = not self._ref_mode
                self.status_bar.set_ref_mode(self._ref_mode)
                return True  # Consume
                
            # 2. Key Navigation (Arrows) in composition mode
            if self._is_in_formula_composition_mode() and self._ref_mode:
                if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
                    self._handle_arrow_navigation(event.key())  # type: ignore[reportAttributeAccessIssue, reportUnknownArgumentType, reportUnknownMemberType]
                    return True  # Swallow event (don't move cursor in text)

        # C. Focus events on formula bar -> update composition visuals
        if source == self.formula_bar_widget.editor:
            if event.type() in (QEvent.Type.FocusIn, QEvent.Type.FocusOut):
                # Delay slightly to allow focus to settle
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(10, self._update_composition_mode_visuals)

        # D. Click on Editor -> Disable Ref Mode (Switch to Edit)
        if self.view.active_editor and source == self.view.active_editor:
            if event.type() == QEvent.Type.MouseButtonPress:
                self._ref_mode = False

        return super().eventFilter(source, event)

    def _handle_arrow_navigation(self, key: Qt.Key) -> None:
        # 
#         Moves the selection relative to the LAST inserted reference (or current selection).
#         And inserts/updates the reference in the formula.
        # 
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
        row = max(0, min(row, self.model.rowCount() - 1))  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        col = max(0, min(col, self.model.columnCount() - 1))  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        
        # 4. Move Virtual Cursor
        new_index = self.model.index(row, col)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        self._phantom_ref_cursor = new_index
        
        # 5. Insert Reference
        # This will trigger text update -> parser -> highlighting of new_index
        self._insert_reference_at_cursor(new_index)
        
        # Note: We DO NOT call setCurrentIndex(new_index) because that would close the active editor.
        # The visual highlighting relies on the Formula Engine parsing the new text and drawing the Colored Box.

    def _on_inline_text_edited(self, text: str) -> None:
        # 
#         Called when user types in the inline cell editor.
#         Syncs to Formula Bar and triggers Reference Mode check.
        # 
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
            self.status_bar.set_ref_mode(True)

    def _insert_reference_at_cursor(self, index: QModelIndex) -> None:
        """
        Inserts a cell reference at the cursor position in:
        1. The Formula Bar
        2. The Active Inline Editor (if exists)
        
        This preserves focus and cursor position, mirroring Excel behavior.
        """
        ref_str = cell_address(index.row(), index.column())
        
        # Determine which widget has the cursor
        # Priority: inline editor > formula bar
        if self.view.active_editor and self.view.active_editor.hasFocus():
            target_widget = self.view.active_editor
        else:
            target_widget = self.formula_bar_widget.editor
        
        cursor = target_widget.cursorPosition()
        text = target_widget.text()
        
        # Insert reference at cursor
        new_text = text[:cursor] + ref_str + text[cursor:]
        new_cursor = cursor + len(ref_str)
        
        # Update formula bar
        self.formula_bar.blockSignals(True)
        self.formula_bar.setText(new_text)
        self.formula_bar.setCursorPosition(new_cursor)
        self.formula_bar.blockSignals(False)
        
        # Update inline editor if active
        if self.view.active_editor:
            self.view.active_editor.setText(new_text)
            self.view.active_editor.setCursorPosition(new_cursor)
        
        # Return focus to original widget
        target_widget.setFocus()
        target_widget.setCursorPosition(new_cursor)
        
        # Trigger viewport update for visual highlighting
        self.view.viewport().update()
        
    def _launch_formula_wizard(self) -> None:
        self.wizard_handler.launch()

    def _on_formula_return(self) -> None:
        """Triggered by Formula Bar 'Enter' or Wizard commit."""
        self._commit_formula()

    def _commit_formula(self) -> None:
        """Commits the current formula bar content to the target cell."""
        text = self.formula_bar.text()
        
        # Target: explicit edit source OR current selection
        target = self._edit_source_index if (self._is_editing_formula and self._edit_source_index) else self.view.currentIndex()
        
        # Reset State BEFORE changing selection/focus to prevent accidental formula appends
        self._is_editing_formula = False
        self._edit_source_index = None
        self._phantom_ref_cursor = None
        
        # Reset visual indicators
        self._update_composition_mode_visuals()

        if target.isValid():
            self.model.setData(target, text, Qt.ItemDataRole.EditRole)
            # Restore selection to target (since clicking modified it)
            self.view.setCurrentIndex(target)
            self.view.setFocus()
        


    def _setup_toolbar(self) -> None:
        """Configures the main toolbar with all actions."""
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
        stack = self.model.undo_stack  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        
        act_undo = stack.createUndoAction(self, "Undo")
        act_undo.setShortcut("Ctrl+Z")
        act_undo.setText("↩ Undo")
        toolbar.addAction(act_undo)
        
        act_redo = stack.createRedoAction(self, "Redo")
        act_redo.setShortcut("Ctrl+Shift+Z")
        act_redo.setText("↪ Redo")
        toolbar.addAction(act_redo)
        
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
        self.border_width_menu = self.border_menu.addMenu("Line Width")
        
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





    def _update_toolbar_state(self, index: QModelIndex) -> None:
        """Updates toolbar state based on selected cell formatting.
        
        Note: Font/style widgets are optional and may not exist if using
        the new modular SpreadsheetToolbar component.
        """
        if not index.isValid():
            return
            
        font = self.model.data(index, Qt.ItemDataRole.FontRole)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        
        # Font Combo (optional - may be in SpreadsheetToolbar)
        if hasattr(self, 'font_combo') and self.font_combo and font:
            self.font_combo.blockSignals(True)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            self.font_combo.setCurrentFont(font)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            self.font_combo.blockSignals(False)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
        
        # Size Spin (optional)
        if hasattr(self, 'size_spin') and self.size_spin and font:
            self.size_spin.blockSignals(True)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            self.size_spin.setValue(font.pointSize())  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            self.size_spin.blockSignals(False)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
        
        # Style Actions (optional)
        if font:
            bold = font.bold()
            italic = font.italic()
            underline = font.underline()
        else:
            bold = italic = underline = False
            
        if hasattr(self, 'act_bold') and self.act_bold:
            self.act_bold.blockSignals(True)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            self.act_bold.setChecked(bold)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            self.act_bold.blockSignals(False)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            
        if hasattr(self, 'act_italic') and self.act_italic:
            self.act_italic.blockSignals(True)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            self.act_italic.setChecked(italic)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            self.act_italic.blockSignals(False)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            
        if hasattr(self, 'act_underline') and self.act_underline:
            self.act_underline.blockSignals(True)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            self.act_underline.setChecked(underline)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            self.act_underline.blockSignals(False)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType]

    def _save_table(self) -> None:
        """Persists the table to the database (Multi-Scroll format)."""
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
            self.status_bar.show_message("Tablet saved successfully.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))
            # import traceback
            # traceback.print_exc()
            
    # --- Formatting Helpers ---
    # --- Formatting Logic delegated to StyleHandler ---

    def _on_selection_changed(self, current: QModelIndex, previous: QModelIndex) -> None:
        """Updates formula bar, Name Box, and reference highlights when selection changes."""
        # Always update Name Box
        if current.isValid():
            addr = cell_address(current.row(), current.column())
            self.name_box.setText(addr)
        else:
            self.name_box.setText("")

        # Formatting update
        self._update_toolbar_state(current)
        
        # Force redraw to clear artifacts
        self.view.viewport().update()

        if self._is_editing_formula:
            return

        # --- Update Reference Highlights (Persistence) ---
        # When selecting a cell with a formula, highlight the referenced cells
        if current.isValid():
            val = self.model.data(current, Qt.ItemDataRole.EditRole)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
            formula_str = str(val) if val is not None else ""
            
            self.formula_bar.blockSignals(True)
            self.formula_bar.setText(formula_str)
            self.formula_bar.blockSignals(False)
            
            # If it's a formula, extract and highlight references
            if formula_str.startswith("="):
                highlights = get_reference_cells(formula_str)
                self.view.set_reference_highlights(highlights)
            else:
                self.view.clear_reference_highlights()
        else:
            self.view.clear_reference_highlights()
            
    def _on_range_selection_changed(self, selected: Any, deselected: Any) -> None:
        """Handles range selection for formula reference insertion."""
        if not self._is_editing_formula:
            return
            
        indexes = self.view.selectionModel().selectedIndexes()
        if not indexes: return

        # 1. Calculate Range String
        min_row = min(idx.row() for idx in indexes)
        max_row = max(idx.row() for idx in indexes)
        min_col = min(idx.column() for idx in indexes)
        max_col = max(idx.column() for idx in indexes)
        
        start_addr = cell_address(min_row, min_col)
        if min_row == max_row and min_col == max_col:
            ref_str = start_addr
        else:
            end_addr = cell_address(max_row, max_col)
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

    def _on_formula_text_edited(self, text: str) -> None:
        """Detects if user is starting a formula (text starts with '=')."""
        if text.startswith("="):
            if not self._is_editing_formula:
                # Enter Edit Mode
                self._is_editing_formula = True
                self._edit_source_index = self.view.currentIndex()
            
            # Update reference highlights as user types
            highlights = get_reference_cells(text)
            self.view.set_reference_highlights(highlights)
        else:
            if self._is_editing_formula and not text.startswith("="):
                self._is_editing_formula = False
                self._edit_source_index = None
            self.view.clear_reference_highlights()
        
        # Update visual indicators (glow, REF mode)
        self._update_composition_mode_visuals()



    def _on_scroll_added(self) -> None:
        """Creates a new scroll/sheet in the workbook."""
        new_name, ok = QInputDialog.getText(self, "New Scroll", "Scroll Name:", text="Sheet")
        if not ok or not new_name: return
        
        content = self._create_default_content()
        m = SpreadsheetModel(content)
        m.scroll_name = new_name
        
        self.models.append(m)
        self.tab_bar.add_tab(new_name)
        
        # Switch to it
        self.tab_bar.set_current_index(len(self.models) - 1)
        
    def _on_scroll_changed(self, index: int) -> None:
        """Switches the active view to the selected scroll."""
        if index < 0 or index >= len(self.models): return
        
        # 1. Disconnect old model signal safely
        try:
            self.model.dataChanged.disconnect(self._on_data_changed)  # type: ignore[reportUnknownMemberType]
        except (TypeError, RuntimeError):
            pass  # Already disconnected or never connected
        
        # 2. Switch
        self.current_model_index = index
        self.model = self.models[index]
        self.view.setModel(self.model)
        
        # 3. Connect new
        self.model.dataChanged.connect(self._on_data_changed)  # type: ignore[reportUnknownMemberType]
        
        # 4. Refresh UI State
        # Ensure we don't have invalid selection
        self.view.clearSelection()
        self._update_toolbar_state(self.view.currentIndex())
        self.name_box.setText("")
        self.formula_bar.setText("")
        
    def _create_default_content(self) -> Dict[str, Any]:
        """Creates default content structure for a new scroll."""
        cols = [chr(65 + i) for i in range(26)]
        # 100 empty rows of similar width
        # Data format is list of lists
        data = [["" for _ in cols] for _ in range(100)]
        return {
            "columns": cols,
            "data": data,
            "styles": {}
        }

    def _on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: Optional[List[int]] = None) -> None:
        """Updates formula bar when cell data changes."""
        current = self.view.currentIndex()
        if not current.isValid():
            return
            
        # Check if current index is within the changed range
        if (top_left.row() <= current.row() <= bottom_right.row() and 
            top_left.column() <= current.column() <= bottom_right.column()):
            
            # Update Formula Bar
            raw_data = str(self.model.data(current, Qt.ItemDataRole.EditRole) or "")  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            if self.formula_bar.text() != raw_data:
                self.formula_bar.blockSignals(True)
                self.formula_bar.setText(raw_data)
                self.formula_bar.blockSignals(False)

    # --- Border Settings Methods (Instance) ---
    # --- Border Logic delegated to StyleHandler ---

    def _apply_borders(self, border_type: str) -> None:
        """Proxy to StyleHandler for border application."""
        self.style_handler.apply_borders(border_type)

    def pick_border_color(self) -> None:
        """Proxy to StyleHandler for border color picker."""
        self.style_handler.pick_border_color()

    def set_border_style(self, style: str) -> None:
        """Proxy to StyleHandler for border style."""
        self.style_handler.set_border_style(style)

    def set_border_width(self, width: int) -> None:
        """Proxy to StyleHandler for border width."""
        self.style_handler.set_border_width(width)

    def _toggle_keyboard(self) -> None:
        """Toggles the Virtual Keyboard dock visibility."""
        if self._kb_dock.isVisible():
            self._kb_dock.hide()
        else:
            self._kb_dock.show()

    def _sort_selection(self, ascending: bool = True) -> None:
        """Sorts selection based on active cell column."""
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
        
    def _add_conditional_rule(self, rule_type: str) -> None:
        """Adds a conditional formatting rule to the selected range."""
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
        # Default: Light Red Fill + Dark Red Text (Theme Aligned)
        style = {"bg": COLORS['destroyer_disabled'], "fg": COLORS['destroyer']}
        
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
            self.model.conditional_manager.add_rule(rule)  # type: ignore[reportUnknownMemberType]
            # Repaint
            self.view.viewport().update()
            
            # Repaint
            self.view.viewport().update()
            
    def _clear_conditional_rules(self) -> None:
        """Removes all conditional formatting rules."""
        if hasattr(self.model, "conditional_manager"):
            self.model.conditional_manager.clear_all_rules()  # type: ignore[reportUnknownMemberType]
            self.view.viewport().update()
            self.status_bar.show_message("Cleared all Conditional Formatting rules.", 3000)




    def _export_csv(self) -> None:
        """Exports the current sheet to CSV format."""
        SpreadsheetIO.export_csv(self, self.model)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]

    def _export_json(self) -> None:
        """Exports the current sheet to JSON format."""
        SpreadsheetIO.export_json(self, self.model)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]

    def _export_image(self) -> None:
        """Exports the current view as an image."""
        SpreadsheetIO.export_image(self, self.view)

    def _import_csv(self) -> None:
        """Imports data from a CSV file."""
        SpreadsheetIO.import_csv(self, self.model)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]

    # --- Find & Replace ---



    def _launch_find_replace(self, mode: str = "find") -> None:
        """Launches the Find/Replace dialog."""
        self.search_handler.launch(mode)
        