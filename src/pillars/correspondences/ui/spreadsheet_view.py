"""
Spreadsheet View - The Emerald Grid Renderer.
QTableView subclass with SpreadsheetModel, formula evaluation, rich text delegate, and fill handle support.
"""
from PyQt6.QtWidgets import (
    QTableView, QStyledItemDelegate, QDialog, QVBoxLayout,
    QDialogButtonBox, QWidget, QStyle, QMenu, QLineEdit, QApplication, QHeaderView, QStyleOptionViewItem, QRubberBand
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, pyqtSignal, QEvent, QItemSelectionModel, QPoint, QRect, QSize, QTimer
from PyQt6.QtGui import QTextDocument, QAbstractTextDocumentLayout, QPalette, QColor, QAction, QUndoStack, QPen, QFont, QKeyEvent, QKeySequence, QBrush, QPainter, QStandardItemModel, QStandardItem, QMouseEvent, QTextOption
from shared.ui.rich_text_editor import RichTextEditor
import json
import re
import os

from pillars.correspondences.services.formula_engine import FormulaEngine, FormulaHelper

from pillars.correspondences.services.undo_commands import (
    SetCellDataCommand, InsertRowsCommand, RemoveRowsCommand,
    InsertColumnsCommand, RemoveColumnsCommand, SortRangeCommand
)

from pillars.correspondences.services.conditional_formatting import ConditionalManager, ConditionalRule

# Custom Roles
BorderRole = Qt.ItemDataRole.UserRole + 1

class SpreadsheetModel(QAbstractTableModel):
    """
    The Map of the Grid.
    Adapts the JSON structure to the Qt Table Model.
    """
    def __init__(self, data_json: dict, parent=None):
        """
          init   logic.
        
        Args:
            data_json: Description of data_json.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self._columns = data_json.get("columns", [])
        # Support both "data" and "rows" keys
        self._data = data_json.get("data") or data_json.get("rows", [])
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

        # Run Sanitization to migrate old HTML content to Plain Text
        self._sanitize_data()

        self.formula_engine = FormulaEngine(self)
        self.undo_stack = QUndoStack(self)
        self.conditional_manager = ConditionalManager()
        self._eval_cache = {}

    def fill_selection(self, source_range, target_range):
        """
        Fill target_rect with data/pattern from source_rect.
        source_range: QItemSelectionRange
        target_range: QItemSelectionRange
        """
        # Calculate Dimensions
        src_top, src_left = source_range.top(), source_range.left()
        src_h = source_range.bottom() - src_top + 1
        src_w = source_range.right() - src_left + 1

        tgt_top, tgt_left = target_range.top(), target_range.left()
        tgt_bottom, tgt_right = target_range.bottom(), target_range.right()

        # Batch Update setup
        self.beginResetModel() # Heavy hammer, but safe for now

        for r in range(tgt_top, tgt_bottom + 1):
            for c in range(tgt_left, tgt_right + 1):
                # Skip if inside source (don't overwrite source)
                if (src_top <= r <= source_range.bottom() and
                    src_left <= c <= source_range.right()):
                    continue

                # Map to Source
                rel_r = (r - src_top) % src_h # Use src_top as anchor valid?
                # If target is BELOW source, r > src_bottom.
                # Pattern repeats relative to TOP of source.
                # Example: Src rows 0,1. Target 2,3,4.
                # Row 2 should map to 0? ((2-0)%2 = 0). Yes.
                # Row 3 should map to 1? ((3-0)%2 = 1). Yes.

                # Careful if target is ABOVE (not implemented in UI yet but logic should hold)
                # If target r= -1? (-1 - 0) % 2 = 1. (Python modulo is cool).

                # However, usually fill starts from Source.
                # If I drag Right, columns change.
                # If I drag Down, rows change.

                # What if I drag Down from A1:B1?
                # Target A2:B2.
                # A2 maps to A1. B2 maps to B1.
                # rel_c = (c - src_left) % src_w.

                src_r = src_top + ((r - src_top) % src_h)
                src_c = src_left + ((c - src_left) % src_w)

                val = self.get_cell_raw(src_r, src_c)
                style = self._styles.get((src_r, src_c))

                # Formula Adjustment
                if isinstance(val, str) and val.startswith("="):
                    d_row = r - src_r
                    d_col = c - src_c
                    # Optimization: If d_row/d_col is 0 (e.g. dragging sideways means d_row=0),
                    # formula might change if it has col refs.
                    new_val = FormulaHelper.adjust_references(val, d_row, d_col)
                    self._data[r][c] = new_val
                else:
                    self._data[r][c] = val

                # Style Copy
                if style:
                    self._styles[(r, c)] = style.copy()

        self.endResetModel()
        self.clear_eval_cache()
        tl = self.index(target_range.top(), target_range.left())
        br = self.index(target_range.bottom(), target_range.right())
        self.dataChanged.emit(tl, br)


    def clear_eval_cache(self):
        """Reset cached formula evaluations after mutations."""
        self._eval_cache.clear()

    def get_cell_raw(self, row, col):
        """
        Retrieve cell raw logic.
        
        Args:
            row: Description of row.
            col: Description of col.
        
        Returns:
            Result of get_cell_raw operation.
        """
        if row < 0 or row >= len(self._data):
            return ""
        if col < 0 or col >= len(self._columns):
            return ""
        return self._data[row][col]

    def evaluate_cell(self, row, col, visited=None):
        """Return the evaluated value for a cell with cycle protection and caching."""
        key = (row, col)
        if visited is None:
            visited = set()
        if key in visited:
            return "#CYCLE!"
        if key in self._eval_cache:
            return self._eval_cache[key]

        visited.add(key)
        try:
            raw = self.get_cell_raw(row, col)

            if isinstance(raw, str) and raw.startswith("="):
                result = self.formula_engine.evaluate(raw, visited)
            else:
                result = raw

            self._eval_cache[key] = result
            return result
        finally:
            visited.discard(key)

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
        """
        Rowcount logic.
        
        Args:
            parent: Description of parent.
        
        """
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        """
        Columncount logic.
        
        Args:
            parent: Description of parent.
        
        """
        return len(self._columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """
        Data logic.
        
        Args:
            index: Description of index.
            role: Description of role.
        
        """
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
            cond = None
            if hasattr(self, "conditional_manager"):
                cond = self.conditional_manager.get_style(row, col, self.evaluate_cell(row, col))
            color_hex = cond.get("bg") if cond and cond.get("bg") else bg
            if color_hex:
                return QColor(color_hex)
            return None

        if role == Qt.ItemDataRole.ForegroundRole:
            style = self._styles.get((row, col), {})
            cond = None
            if hasattr(self, "conditional_manager"):
                cond = self.conditional_manager.get_style(row, col, self.evaluate_cell(row, col))
            fg = cond.get("fg") if cond and cond.get("fg") else style.get("fg")
            if fg:
                return QColor(fg)
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
            return self.evaluate_cell(row, col)

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
        """
        Setdata logic.
        
        Args:
            index: Description of index.
            value: Description of value.
            role: Description of role.
        
        """
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
        """
        Headerdata logic.
        
        Args:
            section: Description of section.
            orientation: Description of orientation.
            role: Description of role.
        
        """
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section < len(self._columns):
                    return self._columns[section]
            else:
                return str(section + 1)
        return None

    def insertRows(self, position, rows, parent=QModelIndex()):
        """
        Insertrows logic.
        
        Args:
            position: Description of position.
            rows: Description of rows.
            parent: Description of parent.
        
        """
        command = InsertRowsCommand(self, position, rows)
        self.undo_stack.push(command)
        return True

    def removeRows(self, position, rows, parent=QModelIndex()):
        """
        Removerows logic.
        
        Args:
            position: Description of position.
            rows: Description of rows.
            parent: Description of parent.
        
        """
        command = RemoveRowsCommand(self, position, rows)
        self.undo_stack.push(command)
        return True

    def insertColumns(self, position, columns, parent=QModelIndex()):
        """
        Insertcolumns logic.
        
        Args:
            position: Description of position.
            columns: Description of columns.
            parent: Description of parent.
        
        """
        command = InsertColumnsCommand(self, position, columns)
        self.undo_stack.push(command)
        return True

    def removeColumns(self, position, columns, parent=QModelIndex()):
        """
        Removecolumns logic.
        
        Args:
            position: Description of position.
            columns: Description of columns.
            parent: Description of parent.
        
        """
        command = RemoveColumnsCommand(self, position, columns)
        self.undo_stack.push(command)
        return True

    def flags(self, index):
        """
        Flags logic.
        
        Args:
            index: Description of index.
        
        """
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    def to_json(self):
        # Serialize styles keys to strings
        """
        Convert to json logic.
        
        """
        styles_str = {f"{r},{c}": v for (r,c), v in self._styles.items()}
        return {
            "columns": self._columns,
            "data": self._data,
            "styles": styles_str
        }

    def sort_range(self, top, left, bottom, right, key_col, ascending=True):
        """
        Sorts the data in the given range based on key_col.
        key_col is absolute column index.
        Empty cells in the key column always go to the bottom.
        """
        # 1. Capture Old Block
        old_block = []
        for r in range(top, bottom + 1):
            row_data = []
            for c in range(left, right + 1):
                val = self._data[r][c]
                style = self._styles.get((r, c))
                row_data.append((val, style))
            old_block.append(row_data)

        # 2. Separate Data vs Empty
        col_offset = key_col - left

        data_rows = []
        empty_rows = []

        for row in old_block:
            val = row[col_offset][0]
            # Check for empty (None or "")
            if val is None or str(val).strip() == "":
                empty_rows.append(row)
            else:
                data_rows.append(row)

        # 3. Sort Data Rows Only
        def sort_key(row_tuple):
            """
            Sort key logic.
            
            Args:
                row_tuple: Description of row_tuple.
            
            """
            val, _ = row_tuple[col_offset]
            try:
                # Parse number
                s_val = str(val).strip()
                f_val = float(s_val)
                return (0, f_val) # (Type Priority 0=Num, Value)
            except:
                # String
                return (1, str(val).lower()) # (Type Priority 1=Str, Value)

        data_rows.sort(key=sort_key, reverse=not ascending)

        # 4. Recombine
        new_block = data_rows + empty_rows

        # 5. Push Command
        if hasattr(self, "undo_stack"):
            cmd = SortRangeCommand(self, (top, left, bottom, right), old_block, new_block)
            self.undo_stack.push(cmd)
        else:
            # Fallback
            cmd = SortRangeCommand(self, (top, left, bottom, right), old_block, new_block)
            cmd.redo()

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
        """
        Paint logic.
        
        Args:
            painter: Description of painter.
            option: Description of option.
            index: Description of index.
        
        """
        try:
            options = option
            self.initStyleOption(options, index)
            style = options.widget.style() if (options.widget and options.widget.style()) else QApplication.style()
            if not style:
                return # Should not happen but safe guard
            
            # Setup painting context
            painter.save()
            painter.setClipRect(options.rect)

            # --- 1. Background ---
            # Default Widget Background (handle selection later)
            style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, options, painter, options.widget)

            # Manual Background (from Role) if any
            bg_color = index.data(Qt.ItemDataRole.BackgroundRole)
            if bg_color and isinstance(bg_color, QColor) and bg_color.isValid():
                # If selected, we might want to blend or skip?
                # Excel shows selection OVER background.
                painter.fillRect(options.rect, bg_color)

            # --- 2. Text ---
            doc = QTextDocument()
            text_option = QTextOption()
            text_option.setAlignment(options.displayAlignment)
            doc.setDefaultTextOption(text_option)
            doc.setDefaultFont(options.font)

            # Safe String Conversion
            val = index.data(Qt.ItemDataRole.DisplayRole)
            text_val = str(val) if val is not None else ""
            doc.setHtml(text_val)

            # Color Management
            ctx = QAbstractTextDocumentLayout.PaintContext()
            ctx.palette = options.palette
            if options.state & QStyle.StateFlag.State_Selected:
                 # Keep text color readable on selection
                 # ctx.palette.setColor(QPalette.ColorRole.Text, options.palette.highlightedText().color())
                 pass

            # Calculate Text Area
            text_rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, options)
            painter.translate(text_rect.topLeft())

            # Respect Word Wrap
            if options.features & QStyleOptionViewItem.ViewItemFeature.WrapText:
                doc.setTextWidth(text_rect.width())
            else:
                 # No fixed width = No wrap (unless explicit <br>)
                doc.setTextWidth(-1)

            doc.documentLayout().draw(painter, ctx)

            # Reset Transform for Borders
            painter.translate(-text_rect.topLeft().x(), -text_rect.topLeft().y())

            # --- 3. Borders ---
            borders = index.data(BorderRole) or {}
            if isinstance(borders, dict):
                rect = options.rect
                pen_default = QPen(QColor("#d9d9d9"), 1) # Standard Excel Gray

                def get_pen(side_config):
                    """
                    Retrieve pen logic.
                    
                    Args:
                        side_config: Description of side_config.
                    
                    Returns:
                        Result of get_pen operation.
                    """
                    if side_config is True: return QPen(Qt.GlobalColor.black, 1)
                    if isinstance(side_config, dict):
                        color = QColor(side_config.get("color", "#000000"))
                        width = int(side_config.get("width", 1))
                        style_map = {"solid": Qt.PenStyle.SolidLine, "dash": Qt.PenStyle.DashLine, "dot": Qt.PenStyle.DotLine}
                        return QPen(color, width, style_map.get(side_config.get("style", "solid"), Qt.PenStyle.SolidLine))
                    return None

                # Borders Helpers
                def draw_line(p, p1, p2):
                    """
                    Draw line logic.
                    
                    Args:
                        p: Description of p.
                        p1: Description of p1.
                        p2: Description of p2.
                    
                    """
                    if p:
                        painter.setPen(p)
                        painter.drawLine(p1, p2)

                # Grid/Border Logic
                # Bottom
                p_bot = get_pen(borders.get("bottom"))
                if p_bot: draw_line(p_bot, rect.bottomLeft(), rect.bottomRight())
                else: draw_line(pen_default, rect.bottomLeft(), rect.bottomRight()) # Default Grid

                # Right
                p_right = get_pen(borders.get("right"))
                if p_right: draw_line(p_right, rect.topRight(), rect.bottomRight())
                else: draw_line(pen_default, rect.topRight(), rect.bottomRight()) # Default Grid

                # Top/Left (only if explicit)
                p_top = get_pen(borders.get("top"))
                draw_line(p_top, rect.topLeft(), rect.topRight())
                p_left = get_pen(borders.get("left"))
                draw_line(p_left, rect.topLeft(), rect.bottomLeft())

            # --- 4. Selection Highlight ---
            if options.state & QStyle.StateFlag.State_Selected:
                # Default: Standard Blue
                base_color = QColor("#0078D7")
                fill_color = QColor("#0078D7")
                fill_color.setAlpha(30)

                # Draw Fill
                painter.fillRect(options.rect, fill_color)

                # Draw Outline
                pen = QPen(base_color, 2)
                painter.setPen(pen)
                painter.drawRect(options.rect.adjusted(1, 1, -2, -2))

            # --- 5. Fill Handle ---
            view = self.parent()
            # Check (row, col)
            if hasattr(view, '_handle_pos') and view._handle_pos == (index.row(), index.column()):
                # Draw Handle
                h_size = view.HANDLE_SIZE
                h_x = option.rect.right() - (h_size // 2)
                h_y = option.rect.bottom() - (h_size // 2)
                
                # Check bounds
                
                painter.save()
                painter.translate(0, 0) # Reset just in case
                
                painter.fillRect(h_x, h_y, h_size, h_size, QBrush(QColor("#217346")))
                painter.setPen(QColor("white"))
                painter.drawRect(h_x, h_y, h_size, h_size)
                
                painter.restore()

            painter.restore()

        except Exception as e:
            print(f"Paint Error at {index.row()},{index.column()}: {e}")
            painter.save()
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, "ERR")
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
        """
          init   logic.
        
        Args:
            initial_html: Description of initial_html.
            parent: Description of parent.
        
        """
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
        """
        Retrieve html logic.
        
        Returns:
            Result of get_html operation.
        """
        return self.editor.get_html()


class SpreadsheetView(QTableView):
    # Signals
    """
    Spreadsheet View class definition.
    
    Attributes:
        active_editor: Description of active_editor.
        HANDLE_SIZE: Description of HANDLE_SIZE.
        _is_over_handle: Description of _is_over_handle.
        _is_dragging_fill: Description of _is_dragging_fill.
        _border_actions: Description of _border_actions.
        _border_settings_actions: Description of _border_settings_actions.
        _border_style_menu: Description of _border_style_menu.
        _border_width_menu: Description of _border_width_menu.
        _last_custom_colors: Description of _last_custom_colors.
        _fill_drag_rect: Description of _fill_drag_rect.
        _fill_start_pos: Description of _fill_start_pos.
        _handle_pos: Description of _handle_pos.
        _rubber_band: Description of _rubber_band.
    
    """
    formula_return_pressed = pyqtSignal()
    editor_text_changed = pyqtSignal(str) # For unified formula bar syncing

    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
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
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # 3. Column Header Menu
        h_header = self.horizontalHeader()
        h_header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        h_header.customContextMenuRequested.connect(self._show_col_menu)
        h_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # 4. Input handling
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.HANDLE_SIZE = 8
        self._is_over_handle = False
        self._is_dragging_fill = False

        # Border UI refs
        self._border_actions = []
        self._border_settings_actions = []
        self._border_style_menu = None
        self._border_width_menu = None

        # Color Dialog Memory
        self._last_custom_colors = []
        self._fill_drag_rect = None # QRect of the potential fill area
        self._fill_start_pos = None # QPoint
        self._handle_pos = None # (row, col) tuple

        # RubberBand for Drag Preview
        self._rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        # Style it to look like a border
        self._rubber_band.setStyleSheet("background-color: transparent; border: 2px dashed gray;")
    def set_border_ui(self, actions, settings, style_menu, width_menu):
        """Receive Actions from Window."""
        self._border_actions = actions
        self._border_settings_actions = settings
        self._border_style_menu = style_menu
        self._border_width_menu = width_menu

    def autofit(self):
        """Resize all columns and rows to fit content."""
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def resizeEvent(self, event):
        """
        Resizeevent logic.
        
        Args:
            event: Description of event.
        
        """
        super().resizeEvent(event)
        # No overlay to resize

    def selectionChanged(self, selected, deselected):
        """
        Selectionchanged logic.
        
        Args:
            selected: Description of selected.
            deselected: Description of deselected.
        
        """
        super().selectionChanged(selected, deselected)
        # Update Handle Index
        selection = self.selectionModel().selection()
        if not selection.isEmpty():
            r = selection.last()
            # We want the bottom-right index
            idx = self.model().index(r.bottom(), r.right())
            # Store simple logic
            self._handle_pos = (r.bottom(), r.right())
            self.viewport().update() # Trigger repaint for handle
        else:
            self._handle_pos = None
            self.viewport().update()

    def mouseMoveEvent(self, event):
        # 1. Check Handle Hover
        """
        Mousemoveevent logic.
        
        Args:
            event: Description of event.
        
        """
        if not self._is_dragging_fill:
            pos = event.pos()
            # Optimization: Only check if near selection edge?
            # Or just check simple distance if we have a handle index
            if self._handle_pos:
                 hr, hc = self._handle_pos
                 # Get logic rect
                 h_idx = self.model().index(hr, hc)
                 rect = self.visualRect(h_idx)
                 if rect.isValid():
                     hx = rect.right() - (self.HANDLE_SIZE // 2)
                     hy = rect.bottom() - (self.HANDLE_SIZE // 2)
                     # Hitbox
                     if abs(pos.x() - (hx + self.HANDLE_SIZE/2)) < 10 and abs(pos.y() - (hy + self.HANDLE_SIZE/2)) < 10:
                         if not self._is_over_handle:
                             self.setCursor(Qt.CursorShape.CrossCursor)
                             self._is_over_handle = True
                         return

            if self._is_over_handle:
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self._is_over_handle = False

        # 2. Handle Dragging
        if self._is_dragging_fill:
             self._update_drag_rect(event.pos())
             return

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """
        Mousepressevent logic.
        
        Args:
            event: Description of event.
        
        """
        if self._is_over_handle and event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging_fill = True
            self._fill_start_pos = event.pos()

            # Capture Source Range
            ranges = self.selectionModel().selection()
            if ranges.isEmpty():
                return
            self._source_range = ranges.first() # QItemSelectionRange
            return

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Mousereleaseevent logic.
        
        Args:
            event: Description of event.
        
        """
        if self._is_dragging_fill:
            self._is_dragging_fill = False
            self.setCursor(Qt.CursorShape.ArrowCursor)

            # Commit Fill
            if self._fill_drag_rect:
                target_range_rect = self._calculate_target_range_from_rect(self._fill_drag_rect)
                if target_range_rect:
                    self.model().fill_selection(self._source_range, target_range_rect)

            self._fill_drag_rect = None
            self._rubber_band.hide()
            return
            
        super().mouseReleaseEvent(event)

    def _update_drag_rect(self, pos):
        """Calculate and update the drag visual feedback."""
        if not hasattr(self, '_source_range'): return
        
        # Get Source Geometry
        top_idx = self.model().index(self._source_range.top(), self._source_range.left())
        bottom_idx = self.model().index(self._source_range.bottom(), self._source_range.right())
        
        top_rect = self.visualRect(top_idx)
        bottom_rect = self.visualRect(bottom_idx)
        
        source_px_rect = top_rect.united(bottom_rect) 
        
        dy = pos.y() - source_px_rect.bottom()
        dx = pos.x() - source_px_rect.right()
        
        # Find cell under mouse
        idx = self.indexAt(pos)
        if not idx.isValid(): return 
            
        target_cell_rect = self.visualRect(idx)
        union_rect = source_px_rect.united(target_cell_rect)
        
        # Constrain to One Axis
        if dy > dx:
             # Vertical
             union_rect.setLeft(source_px_rect.left())
             union_rect.setRight(source_px_rect.right())
        else:
             # Horizontal
             union_rect.setTop(source_px_rect.top())
             union_rect.setBottom(source_px_rect.bottom())
             
        self._fill_drag_rect = union_rect
        if self._fill_drag_rect:
            self._rubber_band.setGeometry(self._fill_drag_rect)
            self._rubber_band.show()
        else:
            self._rubber_band.hide()

    def _calculate_target_range_from_rect(self, rect):
        """Convert visual rect back to row/col range."""
        from PyQt6.QtCore import QPoint, QItemSelectionRange
        # Sample center of corners to avoid grid lines
        tl = rect.topLeft() + QPoint(5,5)
        br = rect.bottomRight() - QPoint(5,5)
        
        tl_idx = self.indexAt(tl)
        br_idx = self.indexAt(br)
        
        if not tl_idx.isValid() or not br_idx.isValid():
             return None
             
        return QItemSelectionRange(tl_idx, br_idx)

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

    def _remove_col(self, col_idx):
        if col_idx != -1:
            self.model().removeColumns(col_idx, 1)


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

            event.accept()
            return

        # Check for Delete/Backspace
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self._clear_selection()
            event.accept()
            return

        super().keyPressEvent(event)

    def _clear_selection(self):
        """Clear content of selected cells (Undoable)."""
        selection = self.selectionModel()
        indexes = selection.selectedIndexes()
        if not indexes: return
        
        model = self.model()
        if hasattr(model, "undo_stack"):
            model.undo_stack.beginMacro("Clear Cells")
            
        try:
            for idx in indexes:
                model.setData(idx, "", Qt.ItemDataRole.EditRole)
        finally:
            if hasattr(model, "undo_stack"):
                model.undo_stack.endMacro()

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