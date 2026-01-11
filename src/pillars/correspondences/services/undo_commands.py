"""
Undo Commands - The Chronicle of Edits.
QUndoCommand implementations for reversible spreadsheet cell, row, column, and sorting operations.
"""
from PyQt6.QtGui import QUndoCommand
from PyQt6.QtCore import QModelIndex, Qt

class SetCellDataCommand(QUndoCommand):
    """
    Command to change a single cell's value.
    """
    def __init__(self, model, index, new_value, role=Qt.ItemDataRole.EditRole):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """
          init   logic.
        
        Args:
            model: Description of model.
            index: Description of index.
            new_value: Description of new_value.
            role: Description of role.
        
        """
        super().__init__()
        self.model = model
        self.row = index.row()
        self.col = index.column()
        self.role = role
        self.new_value = new_value
        
        # We need access to BorderRole, but it's defined in spreadsheet_view.
        # Ideally, we pass the generic integer (UserRole + 1) or import properly.
        # But this file imports from QAbstractTableModel etc.
        # Let's import the constant from View if possible, or just use implicit knowledge?
        # Better: Since this file is a Service, maybe the constant should be in shared?
        # For now, we'll check against Qt.ItemDataRole.UserRole + 1.
        self.BorderRole = Qt.ItemDataRole.UserRole + 1
        
        # Capture old value based on role
        if role in (Qt.ItemDataRole.BackgroundRole, Qt.ItemDataRole.ForegroundRole, Qt.ItemDataRole.TextAlignmentRole, Qt.ItemDataRole.FontRole):
            style = model._styles.get((self.row, self.col), {})  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
            
            if role == Qt.ItemDataRole.BackgroundRole:
                self.key = "bg"
                self.old_value = style.get("bg")
            elif role == Qt.ItemDataRole.ForegroundRole:
                self.key = "fg"
                self.old_value = style.get("fg")
            elif role == Qt.ItemDataRole.TextAlignmentRole:
                self.key = "align"
                self.old_value = style.get("align")
            elif role == Qt.ItemDataRole.FontRole:
                # Expect new_value to be a tuple (key, value) or dict?
                # Let's say we pass (key, value) as new_value for FontRole updates?
                # That's easiest.
                if isinstance(new_value, tuple) and len(new_value) == 2:
                    self.key = new_value[0]
                    self.old_value = style.get(self.key)  # type: ignore[reportUnknownMemberType]
                else:
                    # Fallback or Error
                    self.key = None
                    self.old_value = None
            
        elif role == self.BorderRole:
            style = model._styles.get((self.row, self.col), {})  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
            # Should be a dict of borders
            self.old_value = style.get("borders", {}) # Make copy?
            if isinstance(self.old_value, dict):
                self.old_value = self.old_value.copy()
        else:
            self.old_value = model._data[self.row][self.col]  # type: ignore[reportUnknownMemberType]
            
        self.setText(f"Edit Cell {self.row+1},{self.col+1}")

    def redo(self):
        """
        Redo logic.
        
        """
        idx = self.model.index(self.row, self.col)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        
        if self.role in (Qt.ItemDataRole.BackgroundRole, Qt.ItemDataRole.ForegroundRole, Qt.ItemDataRole.TextAlignmentRole, Qt.ItemDataRole.FontRole):
            if not self.key: return # Invalid FontRole Update
            
            if (self.row, self.col) not in self.model._styles:  # type: ignore[reportUnknownMemberType]
                self.model._styles[(self.row, self.col)] = {}  # type: ignore[reportUnknownMemberType]
            
            if self.role == Qt.ItemDataRole.FontRole:
                 # new_value is (key, value)
                 # We want to store value
                 val = self.new_value[1]
                 if val is None:
                     self.model._styles[(self.row, self.col)].pop(self.key, None)  # type: ignore[reportUnknownMemberType]
                 else:
                     self.model._styles[(self.row, self.col)][self.key] = val  # type: ignore[reportUnknownMemberType]
            else:
                if self.new_value is None:
                    self.model._styles[(self.row, self.col)].pop(self.key, None)  # type: ignore[reportUnknownMemberType]
                else:
                    self.model._styles[(self.row, self.col)][self.key] = self.new_value  # type: ignore[reportUnknownMemberType]
                
        elif self.role == self.BorderRole:
            if (self.row, self.col) not in self.model._styles:  # type: ignore[reportUnknownMemberType]
                self.model._styles[(self.row, self.col)] = {}  # type: ignore[reportUnknownMemberType]
            
            # new_value should be the borders dict
            if not self.new_value:
                self.model._styles[(self.row, self.col)].pop("borders", None)  # type: ignore[reportUnknownMemberType]
            else:
                self.model._styles[(self.row, self.col)]["borders"] = self.new_value  # type: ignore[reportUnknownMemberType]
                
        else:
            self.model._data[self.row][self.col] = self.new_value  # type: ignore[reportUnknownMemberType]
            
        if hasattr(self.model, "clear_eval_cache"):
            self.model.clear_eval_cache()
        self.model.dataChanged.emit(idx, idx, [self.role])

    def undo(self):
        """
        Undo logic.
        
        """
        idx = self.model.index(self.row, self.col)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        
        if self.role in (Qt.ItemDataRole.BackgroundRole, Qt.ItemDataRole.ForegroundRole, Qt.ItemDataRole.TextAlignmentRole, Qt.ItemDataRole.FontRole):
            if not self.key: return

            if (self.row, self.col) not in self.model._styles:  # type: ignore[reportUnknownMemberType]
                self.model._styles[(self.row, self.col)] = {}  # type: ignore[reportUnknownMemberType]
                
            if self.old_value is None:
                self.model._styles[(self.row, self.col)].pop(self.key, None)  # type: ignore[reportUnknownMemberType]
            else:
                self.model._styles[(self.row, self.col)][self.key] = self.old_value  # type: ignore[reportUnknownMemberType]
                
        elif self.role == self.BorderRole:
             if (self.row, self.col) not in self.model._styles:  # type: ignore[reportUnknownMemberType]
                self.model._styles[(self.row, self.col)] = {}  # type: ignore[reportUnknownMemberType]
                
             if not self.old_value:
                 self.model._styles[(self.row, self.col)].pop("borders", None)  # type: ignore[reportUnknownMemberType]
             else:
                 self.model._styles[(self.row, self.col)]["borders"] = self.old_value  # type: ignore[reportUnknownMemberType]
             
        else:
            self.model._data[self.row][self.col] = self.old_value  # type: ignore[reportUnknownMemberType]
            
        if hasattr(self.model, "clear_eval_cache"):
            self.model.clear_eval_cache()
        self.model.dataChanged.emit(idx, idx, [self.role])


class InsertRowsCommand(QUndoCommand):
    """
    Insert Rows Command class definition.
    
    Attributes:
        model: Description of model.
        position: Description of position.
        rows: Description of rows.
    
    """
    def __init__(self, model, position, rows):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """
          init   logic.
        
        Args:
            model: Description of model.
            position: Description of position.
            rows: Description of rows.
        
        """
        super().__init__()
        self.model = model
        self.position = position
        self.rows = rows
        self.setText(f"Insert {rows} Rows")

    def redo(self):
        """Insert rows and shift style keys down."""
        self.model.beginInsertRows(QModelIndex(), self.position, self.position + self.rows - 1)
        col_count = len(self.model._columns)
        for _ in range(self.rows):
            self.model._data.insert(self.position, [""] * col_count)
        
        # STYLE KEY SHIFTING: Move styles below insertion point down
        shifted_styles = {}
        for (r, c), style in list(self.model._styles.items()):
            if r >= self.position:
                # Shift this style down by self.rows
                shifted_styles[(r + self.rows, c)] = style
            else:
                # Keep as-is
                shifted_styles[(r, c)] = style
        self.model._styles = shifted_styles
        
        self.model.endInsertRows()
        if hasattr(self.model, "clear_eval_cache"):
            self.model.clear_eval_cache()

    def undo(self):
        """Remove inserted rows and shift style keys back up."""
        self.model.beginRemoveRows(QModelIndex(), self.position, self.position + self.rows - 1)
        for _ in range(self.rows):
            del self.model._data[self.position]
        
        # STYLE KEY SHIFTING: Move styles that were shifted down back up
        shifted_styles = {}
        for (r, c), style in list(self.model._styles.items()):
            if r >= self.position + self.rows:
                # Shift back up
                shifted_styles[(r - self.rows, c)] = style
            elif r >= self.position:
                # These were in the deleted range, skip them
                pass
            else:
                # Keep as-is
                shifted_styles[(r, c)] = style
        self.model._styles = shifted_styles
        
        self.model.endRemoveRows()
        if hasattr(self.model, "clear_eval_cache"):
            self.model.clear_eval_cache()


class RemoveRowsCommand(QUndoCommand):
    """
    Remove Rows Command class definition.
    
    Attributes:
        model: Description of model.
        position: Description of position.
        rows: Description of rows.
        deleted_data: Description of deleted_data.
    
    """
    def __init__(self, model, position, rows):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """Initialize RemoveRowsCommand and capture data + styles."""
        super().__init__()
        self.model = model
        self.position = position
        self.rows = rows
        self.setText(f"Remove {rows} Rows")
        
        # Capture deleted data for undo
        self.deleted_data = []
        for i in range(rows):
            self.deleted_data.append(list(model._data[position + i]))  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        
        # Capture deleted styles for undo
        self.deleted_styles = {}
        for (r, c), style in list(model._styles.items()):
            if position <= r < position + rows:
                # This style will be deleted, save it
                self.deleted_styles[(r, c)] = style.copy()

    def redo(self):
        """Remove rows and shift style keys up."""
        self.model.beginRemoveRows(QModelIndex(), self.position, self.position + self.rows - 1)
        for _ in range(self.rows):
            del self.model._data[self.position]
        
        # STYLE KEY SHIFTING: Remove deleted range and shift styles up
        shifted_styles = {}
        for (r, c), style in list(self.model._styles.items()):
            if r < self.position:
                # Keep as-is (before deleted range)
                shifted_styles[(r, c)] = style
            elif r >= self.position + self.rows:
                # Shift up by self.rows
                shifted_styles[(r - self.rows, c)] = style
            # else: r is in deleted range, skip it
        self.model._styles = shifted_styles
        
        self.model.endRemoveRows()
        if hasattr(self.model, "clear_eval_cache"):
            self.model.clear_eval_cache()

    def undo(self):
        """Re-insert rows and restore styles."""
        self.model.beginInsertRows(QModelIndex(), self.position, self.position + self.rows - 1)
        for i, row_data in enumerate(self.deleted_data):  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
            self.model._data.insert(self.position + i, row_data)
        
        # STYLE KEY SHIFTING: Shift existing styles down and restore deleted styles
        shifted_styles = {}
        for (r, c), style in list(self.model._styles.items()):
            if r < self.position:
                # Keep as-is (before insertion point)
                shifted_styles[(r, c)] = style
            else:
                # Shift down by self.rows
                shifted_styles[(r + self.rows, c)] = style
        
        # Restore deleted styles
        for (r, c), style in self.deleted_styles.items():
            shifted_styles[(r, c)] = style
        
        self.model._styles = shifted_styles
        
        self.model.endInsertRows()
        if hasattr(self.model, "clear_eval_cache"):
            self.model.clear_eval_cache()


class InsertColumnsCommand(QUndoCommand):
    """
    Insert Columns Command class definition.
    
    Attributes:
        model: Description of model.
        position: Description of position.
        columns: Description of columns.
    
    """
    def __init__(self, model, position, columns):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """
          init   logic.
        
        Args:
            model: Description of model.
            position: Description of position.
            columns: Description of columns.
        
        """
        super().__init__()
        self.model = model
        self.position = position
        self.columns = columns
        self.setText(f"Insert {columns} Columns")

    def redo(self):
        """Insert columns and shift style keys right."""
        self.model.beginInsertColumns(QModelIndex(), self.position, self.position + self.columns - 1)
        # Add new column headers
        for i in range(self.columns):
            self.model._columns.insert(self.position + i, f"NewCol_{len(self.model._columns)+1}")  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        
        # Add entry to every row
        for row in self.model._data:
            for _ in range(self.columns):
                row.insert(self.position, "")
        
        # STYLE KEY SHIFTING: Move styles right of insertion point
        shifted_styles = {}
        for (r, c), style in list(self.model._styles.items()):
            if c >= self.position:
                # Shift right by self.columns
                shifted_styles[(r, c + self.columns)] = style
            else:
                # Keep as-is
                shifted_styles[(r, c)] = style
        self.model._styles = shifted_styles
        
        self.model.endInsertColumns()
        if hasattr(self.model, "clear_eval_cache"):
            self.model.clear_eval_cache()

    def undo(self):
        """Remove inserted columns and shift style keys back left."""
        self.model.beginRemoveColumns(QModelIndex(), self.position, self.position + self.columns - 1)
        # Remove headers
        for _ in range(self.columns):
            del self.model._columns[self.position]
            
        # Remove data
        for row in self.model._data:
            for _ in range(self.columns):
                del row[self.position]
        
        # STYLE KEY SHIFTING: Move styles that were shifted right back left
        shifted_styles = {}
        for (r, c), style in list(self.model._styles.items()):
            if c >= self.position + self.columns:
                # Shift back left
                shifted_styles[(r, c - self.columns)] = style
            elif c >= self.position:
                # These were in the deleted range, skip them
                pass
            else:
                # Keep as-is
                shifted_styles[(r, c)] = style
        self.model._styles = shifted_styles
        
        self.model.endRemoveColumns()
        if hasattr(self.model, "clear_eval_cache"):
            self.model.clear_eval_cache()


class RemoveColumnsCommand(QUndoCommand):
    """
    Remove Columns Command class definition.
    
    Attributes:
        model: Description of model.
        position: Description of position.
        columns: Description of columns.
        deleted_headers: Description of deleted_headers.
        deleted_data: Description of deleted_data.
    
    """
    def __init__(self, model, position, columns):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """Initialize RemoveColumnsCommand and capture data + styles."""
        super().__init__()
        self.model = model
        self.position = position
        self.columns = columns
        self.setText(f"Remove {columns} Columns")
        
        # Capture data
        self.deleted_headers = []
        self.deleted_data = []  # List of lists (one per row, containing deleted cols)
        
        for i in range(columns):
            self.deleted_headers.append(model._columns[position + i])  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            
        for row in model._data:
            cols_data = []
            for i in range(columns):
                cols_data.append(row[position + i])
            self.deleted_data.append(cols_data)
        
        # Capture deleted styles for undo
        self.deleted_styles = {}
        for (r, c), style in list(model._styles.items()):
            if position <= c < position + columns:
                # This style will be deleted, save it
                self.deleted_styles[(r, c)] = style.copy()

    def redo(self):
        """Remove columns and shift style keys left."""
        self.model.beginRemoveColumns(QModelIndex(), self.position, self.position + self.columns - 1)
        # Remove headers
        for _ in range(self.columns):
            del self.model._columns[self.position]
        # Remove data
        for row in self.model._data:
            for _ in range(self.columns):
                del row[self.position]
        
        # STYLE KEY SHIFTING: Remove deleted range and shift styles left
        shifted_styles = {}
        for (r, c), style in list(self.model._styles.items()):
            if c < self.position:
                # Keep as-is (before deleted range)
                shifted_styles[(r, c)] = style
            elif c >= self.position + self.columns:
                # Shift left by self.columns
                shifted_styles[(r, c - self.columns)] = style
            # else: c is in deleted range, skip it
        self.model._styles = shifted_styles
        
        self.model.endRemoveColumns()
        if hasattr(self.model, "clear_eval_cache"):
            self.model.clear_eval_cache()

    def undo(self):
        """Re-insert columns and restore styles."""
        self.model.beginInsertColumns(QModelIndex(), self.position, self.position + self.columns - 1)
        # Restore headers
        for i, header in enumerate(self.deleted_headers):  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
            self.model._columns.insert(self.position + i, header)
            
        # Restore data
        for r_idx, row in enumerate(self.model._data):  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
            saved_cols = self.deleted_data[r_idx]
            for c_idx, val in enumerate(saved_cols):
                row.insert(self.position + c_idx, val)
        
        # STYLE KEY SHIFTING: Shift existing styles right and restore deleted styles
        shifted_styles = {}
        for (r, c), style in list(self.model._styles.items()):
            if c < self.position:
                # Keep as-is (before insertion point)
                shifted_styles[(r, c)] = style
            else:
                # Shift right by self.columns
                shifted_styles[(r, c + self.columns)] = style
        
        # Restore deleted styles
        for (r, c), style in self.deleted_styles.items():
            shifted_styles[(r, c)] = style
        
        self.model._styles = shifted_styles
        
        self.model.endInsertColumns()
        if hasattr(self.model, "clear_eval_cache"):
            self.model.clear_eval_cache()

class SortRangeCommand(QUndoCommand):
    """
    Command to sort a range of cells.
    Holds the old and new state of the data block (including styles).
    """
    def __init__(self, model, range_rect, old_block, new_block):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """
          init   logic.
        
        Args:
            model: Description of model.
            range_rect: Description of range_rect.
            old_block: Description of old_block.
            new_block: Description of new_block.
        
        """
        super().__init__()
        self.model = model
        self.top, self.left, self.bottom, self.right = range_rect  # type: ignore[reportUnknownMemberType]
        self.old_block = old_block
        self.new_block = new_block
        self.setText("Sort Range")

    def _apply_block(self, block):
        # block is list of rows, where each item is (value, style_dict)
        for r_offset, row_data in enumerate(block):
            r = self.top + r_offset
            for c_offset, (val, style) in enumerate(row_data):  # type: ignore[reportUnknownArgumentType, reportUnknownVariableType]
                c = self.left + c_offset
                
                # Update Data
                self.model._data[r][c] = val
                
                # Update Styles
                # Remove all styles for this cell first?
                self.model._styles.pop((r, c), None)
                if style:
                    self.model._styles[(r, c)] = style.copy()
                    
        # Emit generic data changed for the whole rect
        tl = self.model.index(self.top, self.left)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        br = self.model.index(self.bottom, self.right)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        self.model.dataChanged.emit(tl, br, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])
        if hasattr(self.model, "clear_eval_cache"):
            self.model.clear_eval_cache()

    def redo(self):
        """
        Redo logic.
        
        """
        self._apply_block(self.new_block)

    def undo(self):
        """
        Undo logic.
        
        """
        self._apply_block(self.old_block)