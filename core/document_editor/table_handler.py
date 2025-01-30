from PyQt5.QtWidgets import (QDialog, QMenu, QPushButton, QAction, QVBoxLayout,
                            QFormLayout, QSpinBox, QDialogButtonBox, QColorDialog,
                            QComboBox, QLabel)
from PyQt5.QtGui import QTextTableFormat, QColor, QPen, QTextCharFormat, QTextFrameFormat
from PyQt5.QtCore import Qt, QSizeF
from PyQt5.QtWidgets import QApplication

class TableHandler:
    def __init__(self, editor):
        self.editor = editor

    def setup_table_actions(self):
        """Create table-related actions and menu"""
        table_button = QPushButton("Table")
        table_menu = QMenu()
        table_button.setMenu(table_menu)
        
        # Insert table actions
        table_menu.addAction(self.create_action("Insert Table...", self.show_table_dialog))
        
        # Add templates submenu
        templates_menu = table_menu.addMenu("Templates")
        templates = {
            "2x2 Simple": (2, 2),
            "3x3 Grid": (3, 3),
            "Calendar": (7, 5),
            "Contact Card": (2, 3)
        }
        for name, (rows, cols) in templates.items():
            action = self.create_action(name, lambda r=rows, c=cols: self.insert_table(r, c))
            templates_menu.addAction(action)
        
        table_menu.addSeparator()
        
        # Row operations
        row_menu = table_menu.addMenu("Row")
        row_menu.addAction(self.create_action("Insert Above", self.insert_row_above))
        row_menu.addAction(self.create_action("Insert Below", self.insert_row_below))
        row_menu.addAction(self.create_action("Delete Row", self.delete_row))
        
        # Column operations
        col_menu = table_menu.addMenu("Column")
        col_menu.addAction(self.create_action("Insert Left", self.insert_column_left))
        col_menu.addAction(self.create_action("Insert Right", self.insert_column_right))
        col_menu.addAction(self.create_action("Delete Column", self.delete_column))
        
        table_menu.addSeparator()
        
        # Table formatting
        table_menu.addAction(self.create_action("Table Properties...", self.show_table_format_dialog))
        table_menu.addAction(self.create_action("Cell Properties...", self.show_cell_format_dialog))
        
        return table_button

    def create_action(self, text, slot, shortcut=None):
        """Helper to create an action"""
        action = QAction(text, self.editor)
        action.triggered.connect(slot)
        if shortcut:
            action.setShortcut(shortcut)
        return action

    def get_current_table(self):
        """Get current table with error checking"""
        cursor = self.editor.editor.textCursor()
        table = cursor.currentTable()
        if not table:
            return None
        
        # Ensure cursor is in a cell
        cell = table.cellAt(cursor)
        if not cell:
            first_cell = table.cellAt(0, 0)
            if first_cell:
                cursor = first_cell.firstCursorPosition()
                self.editor.editor.setTextCursor(cursor)
                QApplication.processEvents()
                return cursor.currentTable()
        return table

    def insert_table(self, rows, cols):
        """Insert table with given dimensions"""
        cursor = self.editor.editor.textCursor()
        
        # Create table format
        table_format = QTextTableFormat()
        table_format.setCellPadding(5)
        table_format.setCellSpacing(0)
        table_format.setBorder(1)
        table_format.setAlignment(Qt.AlignLeft)
        
        # Insert table
        table = cursor.insertTable(rows, cols, table_format)
        QApplication.processEvents()
        
        # Move cursor to first cell
        if table:
            first_cell = table.cellAt(0, 0)
            if first_cell:
                cursor = first_cell.firstCursorPosition()
                self.editor.editor.setTextCursor(cursor)
                QApplication.processEvents()
            
            # Get fresh table reference
            cursor = self.editor.editor.textCursor()
            table = cursor.currentTable()
    
        return table

    def insert_row_above(self):
        """Insert row above current cell"""
        cursor = self.editor.editor.textCursor()
        table = cursor.currentTable()
        if not table:
            return None
            
        # Store current cell position
        cell = table.cellAt(cursor)
        current_row = cell.row()
        current_col = cell.column()
        
        # Insert row
        table.insertRows(current_row, 1)
        QApplication.processEvents()
        
        # Get fresh table reference and move cursor
        cursor = self.editor.editor.textCursor()
        table = cursor.currentTable()
        if table:
            new_cell = table.cellAt(current_row, current_col)
            if new_cell:
                new_cursor = new_cell.firstCursorPosition()
                self.editor.editor.setTextCursor(new_cursor)
                QApplication.processEvents()
        
        return table

    def insert_row_below(self):
        """Insert row below current cell"""
        cursor = self.editor.editor.textCursor()
        table = cursor.currentTable()
        if not table:
            return None
            
        # Store current cell position
        cell = table.cellAt(cursor)
        current_row = cell.row()
        current_col = cell.column()
        
        # Insert row
        table.insertRows(current_row + 1, 1)
        QApplication.processEvents()
        
        # Get fresh table reference and move cursor
        cursor = self.editor.editor.textCursor()
        table = cursor.currentTable()
        if table:
            new_cell = table.cellAt(current_row + 1, current_col)
            if new_cell:
                new_cursor = new_cell.firstCursorPosition()
                self.editor.editor.setTextCursor(new_cursor)
                QApplication.processEvents()
        
        return table

    def delete_row(self):
        """Delete current row"""
        table = self.get_current_table()
        if not table:
            return
            
        cursor = self.editor.editor.textCursor()
        cell = table.cellAt(cursor)
        table.removeRows(cell.row(), 1)
        QApplication.processEvents()

    def insert_column_left(self):
        """Insert column to the left of current cell"""
        cursor = self.editor.editor.textCursor()
        table = cursor.currentTable()
        if not table:
            return None
            
        # Store current cell position
        cell = table.cellAt(cursor)
        current_row = cell.row()
        current_col = cell.column()
        
        # Insert column
        table.insertColumns(current_col, 1)
        QApplication.processEvents()
        
        # Get fresh table reference and move cursor
        cursor = self.editor.editor.textCursor()
        table = cursor.currentTable()
        if table:
            new_cell = table.cellAt(current_row, current_col)
            if new_cell:
                new_cursor = new_cell.firstCursorPosition()
                self.editor.editor.setTextCursor(new_cursor)
                QApplication.processEvents()
        
        return table

    def insert_column_right(self):
        """Insert column to the right of current cell"""
        cursor = self.editor.editor.textCursor()
        table = cursor.currentTable()
        if not table:
            return None
            
        # Store current cell position
        cell = table.cellAt(cursor)
        current_row = cell.row()
        current_col = cell.column()
        
        # Insert column
        table.insertColumns(current_col + 1, 1)
        QApplication.processEvents()
        
        # Get fresh table reference and move cursor
        cursor = self.editor.editor.textCursor()
        table = cursor.currentTable()
        if table:
            new_cell = table.cellAt(current_row, current_col + 1)
            if new_cell:
                new_cursor = new_cell.firstCursorPosition()
                self.editor.editor.setTextCursor(new_cursor)
                QApplication.processEvents()
        
        return table

    def delete_column(self):
        """Delete current column"""
        table = self.get_current_table()
        if not table:
            return
            
        cursor = self.editor.editor.textCursor()
        cell = table.cellAt(cursor)
        table.removeColumns(cell.column(), 1)
        QApplication.processEvents()

    def merge_selected_cells(self):
        """Merge selected cells"""
        table = self.get_current_table()
        if not table:
            return
            
        cursor = self.editor.editor.textCursor()
        if not cursor.hasSelection():
            return
            
        table.mergeCells(cursor)
        QApplication.processEvents()

    def split_cell(self):
        """Split current cell"""
        table = self.get_current_table()
        if not table:
            return
            
        cursor = self.editor.editor.textCursor()
        cell = table.cellAt(cursor)
        if cell.columnSpan() > 1 or cell.rowSpan() > 1:
            table.splitCell(cell.row(), cell.column(), 1, 1)
            QApplication.processEvents()

    def show_table_dialog(self):
        """Show dialog for table insertion"""
        dialog = TableDialog(self.editor)
        if dialog.exec_() == QDialog.Accepted:
            rows = dialog.rows_spin.value()
            cols = dialog.cols_spin.value()
            self.insert_table(rows, cols)

    def show_table_format_dialog(self):
        """Show dialog for table formatting"""
        cursor = self.editor.editor.textCursor()
        table = cursor.currentTable()
        if table:
            dialog = TableFormatDialog(self.editor, table.format())
            if dialog.exec_() == QDialog.Accepted:
                table.setFormat(dialog.get_format())

    def show_cell_format_dialog(self):
        """Show dialog for cell formatting"""
        # TODO: Implement cell format dialog
        pass

class TableDialog(QDialog):
    """Dialog for table insertion"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Insert Table")
        layout = QVBoxLayout(self)
        
        # Rows and columns
        form_layout = QFormLayout()
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 50)
        self.rows_spin.setValue(3)
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 50)
        self.cols_spin.setValue(3)
        
        form_layout.addRow("Rows:", self.rows_spin)
        form_layout.addRow("Columns:", self.cols_spin)
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

class TableFormatDialog(QDialog):
    """Dialog for table formatting"""
    def __init__(self, parent, table_format):
        super().__init__(parent)
        self.table_format = table_format
        self.setup_ui()
        
    def setup_ui(self):
        # TODO: Implement table format dialog UI
        pass 