from PyQt6.QtWidgets import (
    QTableView, QStyledItemDelegate, QDialog, QVBoxLayout, 
    QDialogButtonBox, QWidget, QStyle, QMenu, QLineEdit, QApplication
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, pyqtSignal, QEvent
from PyQt6.QtGui import QTextDocument, QAbstractTextDocumentLayout, QPalette, QColor, QAction, QUndoStack, QPen, QFont, QKeyEvent, QKeySequence
from pillars.document_manager.ui.rich_text_editor import RichTextEditor
import json
import re

from pillars.correspondences.services.formula_engine import FormulaEngine

from pillars.correspondences.services.undo_commands import (
    SetCellDataCommand, InsertRowsCommand, RemoveRowsCommand, 
    InsertColumnsCommand, RemoveColumnsCommand
)

# Custom Roles
BorderRole = Qt.ItemDataRole.UserRole + 1

class SpreadsheetModel(QAbstractTableModel):
    """
    The Map of the Grid.
    Adapts the JSON structure to the Qt Table Model.
    """
    def __init__(self, data_json: dict, parent=None):
        super().__init__(parent)
        self._columns = data_json.get("columns", [])
        self._data = data_json.get("data", [])
        # Styles: {(row, col): {"bg": "#hex", "fg": "#hex", "borders": {"top": bool, ...}}}
        # We need to load this from JSON if available, or init empty
        self._styles = {}
        loaded_styles = data_json.get("styles", {})
        # Convert string keys "row,col" back to tuple (row, col) if needed
        for k, v in loaded_styles.items():
            try:
                r, c = map(int, k.split(","))
                self._styles[(r, c)] = v
            except:
                pass
                
        # Run Sanitization to migrate old HTML content to Plain Text
        self._sanitize_data()
        
        self.formula_engine = FormulaEngine(self)
        self.undo_stack = QUndoStack(self)
        
    def _sanitize_data(self):
        """
        One-time cleanup: If cells contain HTML tags (from old edits), 
        strip them down to plain text. We now rely on Roles for styling.
        """
        
        pattern = re.compile(r'<[^>]+>')
        
        for r in range(len(self._data)):
            for c in range(len(self._data[r])):
                val = str(self._data[r][c])
                if "<" in val and ">" in val:
                    # Simple check before regex
                    clean_text = pattern.sub('', val).strip()
                    # If it was ONLY tags, it might become empty.
                    # e.g. <div align="center">foo</div> -> foo
                    # If we accidentally strip too much? 
                    # Assuming basic content. 
                    # Also, we might want to preserve the styling into _styles?
                    # That's harder. For now, user just wants clean text in formula bar.
                    # We accept losing the bold/italic of old dirty cells.
                    self._data[r][c] = clean_text

    def get_cell_value(self, row, col):
        """Helper for Formula Engine to resolve references."""
        if row < 0 or row >= len(self._data): return ""
        if col < 0 or col >= len(self._columns): return ""
        # Return raw value to avoid recursion loops (simple protection)
        return self._data[row][col]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)
        
    def columnCount(self, parent=QModelIndex()):
        return len(self._columns)
        
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
            
        row = index.row()
        col = index.column()
        
        # Guard bounds
        if row >= len(self._data) or col >= len(self._data[row]):
            return None
            
        if role == Qt.ItemDataRole.BackgroundRole:
            style = self._styles.get((row, col), {})
            bg = style.get("bg")
            if bg: return QColor(bg)
            return None
            
        if role == Qt.ItemDataRole.ForegroundRole:
            style = self._styles.get((row, col), {})
            fg = style.get("fg")
            if fg: return QColor(fg)
            return None
            
        if role == Qt.ItemDataRole.FontRole:
            style = self._styles.get((row, col), {})
            font = QFont() # Default font
            
            # 1. Family
            family = style.get("font_family")
            if family: font.setFamily(family)
            
            # 2. Size
            size = style.get("font_size")
            if size: font.setPointSize(int(size))
            
            # 3. Bold
            if style.get("bold"): font.setBold(True)
            
            # 4. Italic
            if style.get("italic"): font.setItalic(True)
            
            # 5. Underline
            if style.get("underline"): font.setUnderline(True)
            
            return font

        if role == BorderRole:
            style = self._styles.get((row, col), {})
            return style.get("borders", {})
            
        raw_value = self._data[row][col]
        
        if role == Qt.ItemDataRole.DisplayRole:
            # Evaluate formulas for display
            return self.formula_engine.evaluate(str(raw_value))
            
        if role == Qt.ItemDataRole.EditRole:
            # Return raw formula for editing
            return str(raw_value)
            
        if role == Qt.ItemDataRole.TextAlignmentRole:
            style = self._styles.get((row, col), {})
            align_str = style.get("align", "left")
            if align_str == "center": return Qt.AlignmentFlag.AlignCenter
            if align_str == "right": return Qt.AlignmentFlag.AlignRight
            if align_str == "left": return Qt.AlignmentFlag.AlignLeft
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid(): return False
        
        if role in (Qt.ItemDataRole.EditRole, Qt.ItemDataRole.BackgroundRole, Qt.ItemDataRole.ForegroundRole, Qt.ItemDataRole.TextAlignmentRole, Qt.ItemDataRole.FontRole, BorderRole):
            # Use Command to allow Undo
            # For Colors, value should be hex string or QColor?
            # SetCellDataCommand expects what we want to store.
            # If QColor passed, let's extract name() if we want strings in JSON.
            store_val = value
            if role in (Qt.ItemDataRole.BackgroundRole, Qt.ItemDataRole.ForegroundRole):
                 if hasattr(value, "name"): store_val = value.name()
                 
            command = SetCellDataCommand(self, index, store_val, role)
            self.undo_stack.push(command)
            return True
            
        return False

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section < len(self._columns):
                    return self._columns[section]
            else:
                return str(section + 1)
        return None

    def insertRows(self, position, rows, parent=QModelIndex()):
        command = InsertRowsCommand(self, position, rows)
        self.undo_stack.push(command)
        return True

    def removeRows(self, position, rows, parent=QModelIndex()):
        command = RemoveRowsCommand(self, position, rows)
        self.undo_stack.push(command)
        return True

    def insertColumns(self, position, columns, parent=QModelIndex()):
        command = InsertColumnsCommand(self, position, columns)
        self.undo_stack.push(command)
        return True

    def removeColumns(self, position, columns, parent=QModelIndex()):
        command = RemoveColumnsCommand(self, position, columns)
        self.undo_stack.push(command)
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    def to_json(self):
        # Serialize styles keys to strings
        styles_str = {f"{r},{c}": v for (r,c), v in self._styles.items()}
        return {
            "columns": self._columns,
            "data": self._data,
            "styles": styles_str
        }

class RichTextDelegate(QStyledItemDelegate):
    """
    The Scribe.
    Renders HTML content in cells and opens the RichTextEditor for editing.
    """

    SELECTION_COLORS = [
        "#FF5733", "#33FF57", "#3357FF", "#FF33F5", "#F5FF33", 
        "#33FFF5", "#FFA833", "#8E44AD", "#2ECC71", "#E74C3C"
    ]

    def paint(self, painter, option, index):

        options = option
        self.initStyleOption(options, index)
        
        style = options.widget.style() if options.widget else None
        doc = QTextDocument()
        
        # Apply Alignment from Model
        from PyQt6.QtGui import QTextOption
        text_option = QTextOption()
        text_option.setAlignment(options.displayAlignment)
        doc.setDefaultTextOption(text_option)
        
        # Apply Font (Bold, Italic, Family, Size)
        doc.setDefaultFont(options.font)
        
        doc.setHtml(options.text)
        
        # Setup painting context
        painter.save()
        painter.setClipRect(options.rect)
        
        # 1. Draw Background (from Role or Selection)
        bg_color = index.data(Qt.ItemDataRole.BackgroundRole)
        
        if options.state & QStyle.StateFlag.State_Selected:
            # We handle selection fill at the end (layering 3) to be on top of content?
            # Actually standard practice is Background -> Content -> Selection Overlay.
            # So we SKIP filling here, and do it at step 3.
            pass
        elif bg_color and isinstance(bg_color, QColor) and bg_color.isValid():
            painter.fillRect(options.rect, bg_color)
            
        # 2. Draw Borders and Grid
        # "Excel Style": Default Grid is Light Gray Right/Bottom.
        # Custom Borders override this.
        
        borders = index.data(BorderRole) or {}
        if not isinstance(borders, dict): borders = {}
        
        rect = options.rect
        # Helper vars
        pen_default = QPen(QColor("#d9d9d9"), 1) # Standard Excel Gray
        
        def get_pen(side_config):
            """Parse config dict or bool legacy."""
            if side_config is True: # Legacy
                return QPen(Qt.GlobalColor.black, 1)
                
            if isinstance(side_config, dict):
                color = QColor(side_config.get("color", "#000000"))
                width = int(side_config.get("width", 1))
                style_str = side_config.get("style", "solid")
                
                # Debug rendering
                # print(f"[DEBUG] Painting Border: {style_str} w={width} c={color.name()}")
                
                style_map = {
                    "solid": Qt.PenStyle.SolidLine,
                    "dash": Qt.PenStyle.DashLine,
                    "dot": Qt.PenStyle.DotLine
                }
                style = style_map.get(style_str, Qt.PenStyle.SolidLine)
                return QPen(color, width, style)
                
            return None

        # --- Top ---
        pen = get_pen(borders.get("top"))
        if pen:
            painter.setPen(pen)
            painter.drawLine(rect.topLeft(), rect.topRight())
            
        # --- Left ---
        pen = get_pen(borders.get("left"))
        if pen:
            painter.setPen(pen)
            painter.drawLine(rect.topLeft(), rect.bottomLeft())
            
        # --- Bottom ---
        pen = get_pen(borders.get("bottom"))
        if pen:
            painter.setPen(pen)
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        else:
            # Default Grid (Bottom)
            painter.setPen(pen_default)
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        # --- Right ---
        pen = get_pen(borders.get("right"))
        if pen:
            painter.setPen(pen)
            painter.drawLine(rect.topRight(), rect.bottomRight())
        else:
            # Default Grid (Right)
            painter.setPen(pen_default)
            painter.drawLine(rect.topRight(), rect.bottomRight())
        
        # Translate to cell area
        painter.translate(options.rect.left(), options.rect.top())
        
        # Clip to cell limits
        # clip = options.rect.translated(-options.rect.left(), -options.rect.top())
        doc.setTextWidth(options.rect.width())
        
        # Draw text
        ctx = QAbstractTextDocumentLayout.PaintContext()
        
        # Apply Palette (Foreground Color matches Role because initStyleOption sets options.palette.text)
        ctx.palette = options.palette
        
        if options.state & QStyle.StateFlag.State_Selected:
            # Keep original text color (don't invert to white)
            # ctx.palette.setColor(QPalette.ColorRole.Text, options.palette.highlightedText().color())
            pass
            
        doc.documentLayout().draw(painter, ctx)
        
        # 3. Draw Selection / Highlights
        # Resolve Window State
        view = self.parent()
        top_window = view.window()
        is_editing = getattr(top_window, "_is_editing_formula", False)
        source_index = getattr(top_window, "_edit_source_index", None)
        
        # A. Draw Source Cell Highlight (The one being edited)
        # Even if not selected in view (because we clicked elsewhere)
        if is_editing and source_index and source_index == index:
            # Special Style for Source: Blue Dashed Outline
            painter.save()
            pen = QPen(QColor("#0078D7"), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            # No fill, just outline to show "This is where the result goes"
            painter.drawRect(options.rect.adjusted(1, 1, -2, -2))
            painter.restore()

        # B. Draw Selection (Fill + Outline)
        if options.state & QStyle.StateFlag.State_Selected:
            
            # Default: Standard Blue
            base_color = QColor("#0078D7")
            fill_color = QColor("#0078D7")
            fill_color.setAlpha(30) # Default Tint

            # Formula Coloring
            if is_editing:
                 # Outline = Dynamic Color
                 h = (index.row() * 13 + index.column() * 7) % len(self.SELECTION_COLORS)
                 base_color = QColor(self.SELECTION_COLORS[h])
                 
                 # Fill = Light Grey (Fixed, as requested)
                 fill_color = QColor("#E0E0E0")
                 fill_color.setAlpha(150) # More visible grey
            
            # Fill
            painter.fillRect(options.rect, fill_color)
            
            # Outline (Solid)
            pen = QPen(base_color, 2)
            painter.setPen(pen)
            painter.drawRect(options.rect.adjusted(1, 1, -2, -2))
        
        painter.restore()

    def createEditor(self, parent, option, index):
        """Custom Editor to fix clipping and style issues."""
        editor = QLineEdit(parent)
        editor.setFrame(False) # Seamless
        
        # Wire to View for Unified Workflow
        view = self.parent()
        if view:
            view.active_editor = editor
            editor.textChanged.connect(view.editor_text_changed.emit)
            # Unified Workflow: Hijack Keys
            top_window = view.window()
            if top_window:
                editor.installEventFilter(top_window)
            
        # Strict Styling to prevent clipping
        editor.setStyleSheet("QLineEdit { border: none; margin: 0px; padding: 0px; background: transparent; }")
        
        return editor

    def updateEditorGeometry(self, editor, option, index):
        """Ensure editor fills the cell exactly."""
        editor.setGeometry(option.rect)
        
    def setEditorData(self, editor, index):
        """Get raw data (formula) for editing."""
        text = index.data(Qt.ItemDataRole.EditRole)
        editor.setText(str(text) if text is not None else "")
        
    def setModelData(self, editor, model, index):
        """Save text back to model."""
        text = editor.text()
        model.setData(index, text, Qt.ItemDataRole.EditRole)
        
        # Clear active editor ref
        view = self.parent()
        if view:
            view.active_editor = None

class CellEditorDialog(QDialog):
    """
    Popup window for editing a cell with full Rich Text capabilities.
    """
    def __init__(self, initial_html, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Cell")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        self.editor = RichTextEditor()
        self.editor.set_html(initial_html)
        layout.addWidget(self.editor)
        
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        
    def get_html(self):
        return self.editor.get_html()

class SpreadsheetView(QTableView):
    # Signals
    formula_return_pressed = pyqtSignal()
    editor_text_changed = pyqtSignal(str) # For unified formula bar syncing

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_editor = None # Track inline editor for click hijacking
        self.setItemDelegate(RichTextDelegate(self))
        self.setAlternatingRowColors(True)
        
        # 1. Main Grid Menu (Cells)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_cell_menu)
        
        # 2. Row Header Menu
        v_header = self.verticalHeader()
        v_header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        v_header.customContextMenuRequested.connect(self._show_row_menu)
        
        # 3. Column Header Menu
        h_header = self.horizontalHeader()
        h_header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        h_header.customContextMenuRequested.connect(self._show_col_menu)
        
        # Border UI refs
        self._border_actions = []
        self._border_settings_actions = []
        self._border_style_menu = None
        self._border_width_menu = None
        
    def set_border_ui(self, actions, settings, style_menu, width_menu):
        """Receive Actions from Window."""
        self._border_actions = actions
        self._border_settings_actions = settings
        self._border_style_menu = style_menu
        self._border_width_menu = width_menu

    def _on_double_click(self, index):
        if not index.isValid():
            return
            
        current_html = index.data(Qt.ItemDataRole.DisplayRole)
        dialog = CellEditorDialog(current_html, self)
        if dialog.exec():
            new_html = dialog.get_html()
            self.model().setData(index, new_html, Qt.ItemDataRole.EditRole)

    def _show_cell_menu(self, pos):
        """Menu for the Grid Cells (Copy, Paste, Format, etc)."""
        index = self.indexAt(pos)
        menu = QMenu(self)
        
        # Edit
        act_edit = QAction("Edit Cell", self)
        act_edit.triggered.connect(lambda: self._on_double_click(index))
        act_edit.setEnabled(index.isValid())
        menu.addAction(act_edit)
        
        menu.addSeparator()
        
        # Copy
        act_copy = QAction("Copy", self)
        # act_copy.setShortcut(QKeySequence.StandardKey.Copy) # Shortcuts don't show in context menu usually unless added to widget, but helpful hint
        act_copy.triggered.connect(self._copy_selection)
        menu.addAction(act_copy)
        
        act_copy_val = QAction("Copy Values Only", self)
        act_copy_val.triggered.connect(self._copy_selection_values)
        menu.addAction(act_copy_val)
        
        # Paste
        act_paste = QAction("Paste", self)
        # act_paste.setShortcut(QKeySequence.StandardKey.Paste)
        act_paste.triggered.connect(self._paste_from_clipboard)
        menu.addAction(act_paste)
        
        menu.addSeparator()
        
        # Borders Submenu
        if self._border_actions:
            border_sub = menu.addMenu("Borders")
            for act in self._border_actions:
                border_sub.addAction(act)
                
            border_sub.addSeparator()
            
            # Add Settings
            for act in self._border_settings_actions:
                border_sub.addAction(act)
                
            # Add Style/Width menus
            # Note: QMenu.addMenu() doesn't take ownership but adds it.
            # But the menu already exists in the toolbar.
            # Adding it here might move it?
            # Re-adding a QMenu that is already in another menu might be tricky in Qt.
            # It might perform a reparenting.
            # Safer: duplicate or just leave as is. 
            # Ideally we'd share Actions, not Menus.
            # But "Line Style" is a Menu.
            # Let's try adding it. If it disappears from Toolbar, we know why.
            # Alternative: Create NEW submenu "Line Style" and add actions from original.
            # But we didn't save actions for style/width in list form.
            # Let's assume standard behavior: we act on ACTIONS.
            # We can get actions from the menu?
            
            if self._border_style_menu:
                # Create duplicate submenu to avoid stealing visual widget
                s_menu = border_sub.addMenu("Line Style")
                for action in self._border_style_menu.actions():
                    s_menu.addAction(action)
                    
            if self._border_width_menu:
                w_menu = border_sub.addMenu("Line Width")
                for action in self._border_width_menu.actions():
                    w_menu.addAction(action)

        menu.exec(self.viewport().mapToGlobal(pos))

    def _show_row_menu(self, pos):
        """Menu for Row Header."""
        header = self.verticalHeader()
        logical_index = header.logicalIndexAt(pos)
        
        menu = QMenu(self)
        
        act_add_row_above = QAction("Insert Row Above", self)
        act_add_row_above.triggered.connect(lambda: self._insert_row(logical_index, above=True))
        
        act_add_row_below = QAction("Insert Row Below", self)
        act_add_row_below.triggered.connect(lambda: self._insert_row(logical_index, above=False))
        
        act_del_row = QAction("Delete Row", self)
        act_del_row.triggered.connect(lambda: self._remove_row(logical_index))
        
        menu.addAction(act_add_row_above)
        menu.addAction(act_add_row_below)
        menu.addSeparator()
        menu.addAction(act_del_row)
        
        menu.exec(header.mapToGlobal(pos))

    def _show_col_menu(self, pos):
        """Menu for Column Header."""
        header = self.horizontalHeader()
        logical_index = header.logicalIndexAt(pos)
        
        menu = QMenu(self)
        
        act_add_col_left = QAction("Insert Column Left", self)
        act_add_col_left.triggered.connect(lambda: self._insert_col(logical_index, left=True))

        act_add_col_right = QAction("Insert Column Right", self)
        act_add_col_right.triggered.connect(lambda: self._insert_col(logical_index, left=False))

        act_del_col = QAction("Delete Column", self)
        act_del_col.triggered.connect(lambda: self._remove_col(logical_index))
        
        menu.addAction(act_add_col_left)
        menu.addAction(act_add_col_right)
        menu.addSeparator()
        menu.addAction(act_del_col)
        
        menu.exec(header.mapToGlobal(pos))

    def _insert_row(self, row_idx, above=True):
        model = self.model()
        if row_idx == -1: 
            # If nothing selected, append to end
            model.insertRows(model.rowCount(), 1)
        else:
            pos = row_idx if above else row_idx + 1
            model.insertRows(pos, 1)

    def _remove_row(self, row_idx):
        if row_idx != -1:
            self.model().removeRows(row_idx, 1)

    def _insert_col(self, col_idx, left=True):
        model = self.model()
        if col_idx == -1:
            model.insertColumns(model.columnCount(), 1)
        else:
            pos = col_idx if left else col_idx + 1
            model.insertColumns(pos, 1)


    def keyPressEvent(self, event: QKeyEvent):
        """Intercept Copy/Paste Shortcuts."""
        # Check for Ctrl+C
        if event.matches(QKeySequence.StandardKey.Copy) or (event.key() == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self._copy_selection()
            event.accept()
            return
            
        # Check for Ctrl+V
        if event.matches(QKeySequence.StandardKey.Paste) or (event.key() == Qt.Key.Key_V and event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self._paste_from_clipboard()
            event.accept()
            return

        super().keyPressEvent(event)

    def _copy_selection(self):
        """Copy selected cells to clipboard as TSV."""
        selection = self.selectionModel()
        indexes = selection.selectedIndexes()
        
        if not indexes:
            return

        # Sort indexes
        indexes = sorted(indexes, key=lambda x: (x.row(), x.column()))
        
        # Determine bounds
        min_row = indexes[0].row()
        min_col = indexes[0].column()
        max_row = indexes[-1].row()
        max_col = indexes[-1].column()
        
        # Build Table
        # sparse grid map
        grid = {}
        for idx in indexes:
            grid[(idx.row(), idx.column())] = idx.data(Qt.ItemDataRole.EditRole)
            
        tsv_rows = []
        # We must iterate strictly from min to max to preserve structure, even if some cells are NOT selected in a sparse selection (?)
        # Standard behavior: Copy rectangular bounds of selection.
        
        # Check if selection is contiguous or not?
        # Excel copies the bounding box usually.
        
        # Let's verify bounding box logic:
        # Determine strict bounds of ALL selected cells.
        rows = sorted(list(set(idx.row() for idx in indexes)))
        cols = sorted(list(set(idx.column() for idx in indexes)))
        if not rows or not cols: return
        
        min_r, max_r = rows[0], rows[-1]
        min_c, max_c = cols[0], cols[-1]
        
        text_buffer = []
        for r in range(min_r, max_r + 1):
            row_data = []
            for c in range(min_c, max_c + 1):
                # Only include if actually selected? 
                # Excel fills gaps with empty if you control-click disjoint.
                # Simplest: Just use bounding box.
                val = grid.get((r, c), "")
                row_data.append(str(val) if val is not None else "")
            text_buffer.append("\t".join(row_data))
            
        result = "\n".join(text_buffer)
        QApplication.clipboard().setText(result)

    def _copy_selection_values(self):
        """Copy selected cells to clipboard as TSV (Values Only)."""
        selection = self.selectionModel()
        indexes = selection.selectedIndexes()
        
        if not indexes:
            return

        # Sort indexes
        indexes = sorted(indexes, key=lambda x: (x.row(), x.column()))
        
        # Determine bounds
        rows = sorted(list(set(idx.row() for idx in indexes)))
        cols = sorted(list(set(idx.column() for idx in indexes)))
        if not rows or not cols: return
        
        min_r, max_r = rows[0], rows[-1]
        min_c, max_c = cols[0], cols[-1]

        # Build Table
        # sparse grid map
        grid = {}
        for idx in indexes:
            grid[(idx.row(), idx.column())] = idx.data(Qt.ItemDataRole.DisplayRole)
            
        text_buffer = []
        for r in range(min_r, max_r + 1):
            row_data = []
            for c in range(min_c, max_c + 1):
                val = grid.get((r, c), "")
                row_data.append(str(val) if val is not None else "")
            text_buffer.append("\t".join(row_data))
            
        result = "\n".join(text_buffer)
        QApplication.clipboard().setText(result)

    def _paste_from_clipboard(self):
        """Paste TSV from clipboard starting at current index."""
        text = QApplication.clipboard().text()
        if not text: return
        
        # Start at current index (Top-Left)
        start_idx = self.currentIndex()
        if not start_idx.isValid(): return
        
        r_start = start_idx.row()
        c_start = start_idx.column()
        
        rows = text.split('\n')
        
        model = self.model()
        
        # Use Undo Macro
        if hasattr(model, "undo_stack"):
            model.undo_stack.beginMacro("Paste")
            
        try:
            for i, row_str in enumerate(rows):
                # row_str might have \r depending on OS
                cols = row_str.replace('\r', '').split('\t')
                target_row = r_start + i
                
                if target_row >= model.rowCount(): break
                
                for j, val in enumerate(cols):
                    target_col = c_start + j
                    if target_col >= model.columnCount(): break
                    
                    idx = model.index(target_row, target_col)
                    if idx.isValid():
                         model.setData(idx, val, Qt.ItemDataRole.EditRole)
        finally:
            if hasattr(model, "undo_stack"):
                model.undo_stack.endMacro()
