"""Table management features for RichTextEditor."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QSpinBox, 
    QDoubleSpinBox, QDialogButtonBox, QToolButton, QPushButton,
    QMenu, QWidget, QTextEdit, QComboBox, QColorDialog
)
from PyQt6.QtGui import (
    QAction, QTextTableFormat, QTextLength, 
    QTextCursor, QTextCharFormat, QTextTableCellFormat,
    QTextFrameFormat
)
from PyQt6.QtCore import Qt

class TableDialog(QDialog):
    """Dialog for inserting a new table."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insert Table")
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 100)
        self.rows_spin.setValue(2)
        form.addRow("Rows:", self.rows_spin)
        
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 100)
        self.cols_spin.setValue(2)
        form.addRow("Columns:", self.cols_spin)
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 100)
        self.width_spin.setValue(100)
        self.width_spin.setSuffix("%")
        form.addRow("Width:", self.width_spin)
        
        self.border_spin = QDoubleSpinBox()
        self.border_spin.setRange(0, 10)
        self.border_spin.setValue(1)
        form.addRow("Border Width:", self.border_spin)
        
        self.border_style_combo = QComboBox()
        # QTextDocument only renders solid (or no) borders; keep UI honest.
        self.border_style_combo.addItems([
            "None",
            "Solid"
        ])
        self.border_style_combo.setCurrentText("Solid")
        form.addRow("Border Style:", self.border_style_combo)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def get_data(self):
        return {
            'rows': self.rows_spin.value(),
            'cols': self.cols_spin.value(),
            'width': self.width_spin.value(),
            'border': self.border_spin.value(),
            'border_style': self.border_style_combo.currentText()
        }

class TablePropertiesDialog(QDialog):
    """Dialog for editing table properties."""
    def __init__(self, fmt: QTextTableFormat, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Table Properties")
        self.fmt = fmt
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 100)
        # Try to get current width if it's percentage
        if self.fmt.width().type() == QTextLength.Type.PercentageLength:
            self.width_spin.setValue(int(self.fmt.width().rawValue()))
        else:
            self.width_spin.setValue(100)
        self.width_spin.setSuffix("%")
        form.addRow("Width:", self.width_spin)
        
        self.border_spin = QDoubleSpinBox()
        self.border_spin.setRange(0, 10)
        self.border_spin.setValue(self.fmt.border())
        form.addRow("Border Width:", self.border_spin)
        
        self.border_style_combo = QComboBox()
        self.border_style_combo.addItems([
            "None",
            "Solid"
        ])
        # Get current border style (clamped to supported values)
        current_style = self._get_border_style_name(self.fmt.borderStyle())
        self.border_style_combo.setCurrentText(current_style)
        form.addRow("Border Style:", self.border_style_combo)
        
        self.cell_spacing_spin = QDoubleSpinBox()
        self.cell_spacing_spin.setRange(0, 20)
        self.cell_spacing_spin.setValue(self.fmt.cellSpacing())
        form.addRow("Cell Spacing:", self.cell_spacing_spin)
        
        self.cell_padding_spin = QDoubleSpinBox()
        self.cell_padding_spin.setRange(0, 20)
        self.cell_padding_spin.setValue(self.fmt.cellPadding())
        form.addRow("Cell Padding:", self.cell_padding_spin)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _get_border_style_name(self, style: QTextFrameFormat.BorderStyle) -> str:
        """Convert border style enum to name."""
        style_map = {
            QTextFrameFormat.BorderStyle.BorderStyle_None: "None",
            QTextFrameFormat.BorderStyle.BorderStyle_Solid: "Solid"
        }
        return style_map.get(style, "Solid")
    
    def _get_border_style_enum(self, name: str) -> QTextFrameFormat.BorderStyle:
        """Convert border style name to enum."""
        style_map = {
            "None": QTextFrameFormat.BorderStyle.BorderStyle_None,
            "Solid": QTextFrameFormat.BorderStyle.BorderStyle_Solid
        }
        return style_map.get(name, QTextFrameFormat.BorderStyle.BorderStyle_Solid)
        
    def apply_to_format(self, fmt: QTextTableFormat):
        fmt.setWidth(QTextLength(QTextLength.Type.PercentageLength, self.width_spin.value()))
        fmt.setBorder(self.border_spin.value())
        fmt.setBorderStyle(self._get_border_style_enum(self.border_style_combo.currentText()))
        fmt.setCellSpacing(self.cell_spacing_spin.value())
        fmt.setCellPadding(self.cell_padding_spin.value())

class CellBorderDialog(QDialog):
    """Dialog for editing individual cell border styles."""
    def __init__(self, fmt: QTextTableCellFormat, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cell Border Styles")
        self.fmt = fmt
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Border styles for each side
        border_styles = ["None", "Solid"]  # QTextDocument renders only solid/none
        
        # Border Color
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QColor
        self.border_color = self.fmt.topBorderBrush().color() if self.fmt.topBorderBrush().style() != Qt.BrushStyle.NoBrush else QColor(Qt.GlobalColor.black)
        
        self.color_button = QPushButton("Choose Border Color")
        self.color_button.setStyleSheet(f"background-color: {self.border_color.name()}; color: {'white' if self.border_color.lightness() < 128 else 'black'};")
        self.color_button.clicked.connect(self._pick_border_color)
        form.addRow("Border Color:", self.color_button)
        
        # Top Border
        self.top_style = QComboBox()
        self.top_style.addItems(border_styles)
        self.top_style.setCurrentText(self._get_border_style_name(self.fmt.topBorderStyle()))
        
        self.top_width = QDoubleSpinBox()
        self.top_width.setRange(0, 10)
        self.top_width.setValue(self.fmt.topBorder())
        self.top_width.setSuffix(" px")
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.top_style)
        top_layout.addWidget(self.top_width)
        form.addRow("Top Border:", top_layout)
        
        # Right Border
        self.right_style = QComboBox()
        self.right_style.addItems(border_styles)
        self.right_style.setCurrentText(self._get_border_style_name(self.fmt.rightBorderStyle()))
        
        self.right_width = QDoubleSpinBox()
        self.right_width.setRange(0, 10)
        self.right_width.setValue(self.fmt.rightBorder())
        self.right_width.setSuffix(" px")
        
        right_layout = QHBoxLayout()
        right_layout.addWidget(self.right_style)
        right_layout.addWidget(self.right_width)
        form.addRow("Right Border:", right_layout)
        
        # Bottom Border
        self.bottom_style = QComboBox()
        self.bottom_style.addItems(border_styles)
        self.bottom_style.setCurrentText(self._get_border_style_name(self.fmt.bottomBorderStyle()))
        
        self.bottom_width = QDoubleSpinBox()
        self.bottom_width.setRange(0, 10)
        self.bottom_width.setValue(self.fmt.bottomBorder())
        self.bottom_width.setSuffix(" px")
        
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.bottom_style)
        bottom_layout.addWidget(self.bottom_width)
        form.addRow("Bottom Border:", bottom_layout)
        
        # Left Border
        self.left_style = QComboBox()
        self.left_style.addItems(border_styles)
        self.left_style.setCurrentText(self._get_border_style_name(self.fmt.leftBorderStyle()))
        
        self.left_width = QDoubleSpinBox()
        self.left_width.setRange(0, 10)
        self.left_width.setValue(self.fmt.leftBorder())
        self.left_width.setSuffix(" px")
        
        left_layout = QHBoxLayout()
        left_layout.addWidget(self.left_style)
        left_layout.addWidget(self.left_width)
        form.addRow("Left Border:", left_layout)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _pick_border_color(self):
        """Pick border color."""
        from PyQt6.QtGui import QColor
        from PyQt6.QtCore import Qt
        color = QColorDialog.getColor(self.border_color, self, "Select Border Color")
        if color.isValid():
            self.border_color = color
            self.color_button.setStyleSheet(f"background-color: {color.name()}; color: {'white' if color.lightness() < 128 else 'black'};")
    
    def _get_border_style_name(self, style: QTextFrameFormat.BorderStyle) -> str:
        """Convert border style enum to name (limited to supported set)."""
        style_map = {
            QTextFrameFormat.BorderStyle.BorderStyle_None: "None",
            QTextFrameFormat.BorderStyle.BorderStyle_Solid: "Solid"
        }
        return style_map.get(style, "Solid")
    
    def _get_border_style_enum(self, name: str) -> QTextFrameFormat.BorderStyle:
        """Convert border style name to enum (supported set only)."""
        style_map = {
            "None": QTextFrameFormat.BorderStyle.BorderStyle_None,
            "Solid": QTextFrameFormat.BorderStyle.BorderStyle_Solid
        }
        return style_map.get(name, QTextFrameFormat.BorderStyle.BorderStyle_Solid)
    
    def apply_to_format(self, fmt: QTextTableCellFormat):
        """Apply the border settings to the cell format."""
        # Top border
        fmt.setTopBorder(self.top_width.value())
        fmt.setTopBorderStyle(self._get_border_style_enum(self.top_style.currentText()))
        
        # Right border
        fmt.setRightBorder(self.right_width.value())
        fmt.setRightBorderStyle(self._get_border_style_enum(self.right_style.currentText()))
        
        # Bottom border
        fmt.setBottomBorder(self.bottom_width.value())
        fmt.setBottomBorderStyle(self._get_border_style_enum(self.bottom_style.currentText()))
        
        # Left border
        fmt.setLeftBorder(self.left_width.value())
        fmt.setLeftBorderStyle(self._get_border_style_enum(self.left_style.currentText()))
        
        # Also set brush colors for better visibility
        from PyQt6.QtGui import QBrush
        from PyQt6.QtCore import Qt
        brush = QBrush(self.border_color, Qt.BrushStyle.SolidPattern)
        fmt.setTopBorderBrush(brush)
        fmt.setRightBorderBrush(brush)
        fmt.setBottomBorderBrush(brush)
        fmt.setLeftBorderBrush(brush)

class CellPropertiesDialog(QDialog):
    """Dialog for editing cell properties."""
    def __init__(self, fmt: QTextTableCellFormat, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cell Properties")
        self.fmt = fmt
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Padding
        self.pad_top = QDoubleSpinBox()
        self.pad_top.setRange(0, 50)
        self.pad_top.setValue(self.fmt.topPadding())
        form.addRow("Top Padding:", self.pad_top)
        
        self.pad_bottom = QDoubleSpinBox()
        self.pad_bottom.setRange(0, 50)
        self.pad_bottom.setValue(self.fmt.bottomPadding())
        form.addRow("Bottom Padding:", self.pad_bottom)
        
        self.pad_left = QDoubleSpinBox()
        self.pad_left.setRange(0, 50)
        self.pad_left.setValue(self.fmt.leftPadding())
        form.addRow("Left Padding:", self.pad_left)
        
        self.pad_right = QDoubleSpinBox()
        self.pad_right.setRange(0, 50)
        self.pad_right.setValue(self.fmt.rightPadding())
        form.addRow("Right Padding:", self.pad_right)
        
        # Vertical Alignment
        self.v_align = QComboBox()
        self.v_align.addItems(["Top", "Middle", "Bottom"])
        current_align = self.fmt.verticalAlignment()
        if current_align == QTextCharFormat.VerticalAlignment.AlignTop:
            self.v_align.setCurrentText("Top")
        elif current_align == QTextCharFormat.VerticalAlignment.AlignMiddle:
            self.v_align.setCurrentText("Middle")
        elif current_align == QTextCharFormat.VerticalAlignment.AlignBottom:
            self.v_align.setCurrentText("Bottom")
        form.addRow("Vertical Align:", self.v_align)

        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def apply_to_format(self, fmt: QTextTableCellFormat):
        fmt.setTopPadding(self.pad_top.value())
        fmt.setBottomPadding(self.pad_bottom.value())
        fmt.setLeftPadding(self.pad_left.value())
        fmt.setRightPadding(self.pad_right.value())
        
        align_text = self.v_align.currentText()
        if align_text == "Top":
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignTop)
        elif align_text == "Middle":
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignMiddle)
        elif align_text == "Bottom":
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignBottom)

class ColumnPropertiesDialog(QDialog):
    """Dialog for editing column properties."""
    def __init__(self, length: QTextLength, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Column Properties")
        self.length = length
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Variable (Auto)", "Percentage", "Fixed (Pixels)"])
        
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(0, 10000)
        
        # Set initial values
        if self.length.type() == QTextLength.Type.VariableLength:
            self.type_combo.setCurrentIndex(0)
            self.value_spin.setEnabled(False)
        elif self.length.type() == QTextLength.Type.PercentageLength:
            self.type_combo.setCurrentIndex(1)
            self.value_spin.setValue(self.length.rawValue())
            self.value_spin.setSuffix("%")
        elif self.length.type() == QTextLength.Type.FixedLength:
            self.type_combo.setCurrentIndex(2)
            self.value_spin.setValue(self.length.rawValue())
            self.value_spin.setSuffix(" px")
            
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        
        form.addRow("Width Type:", self.type_combo)
        form.addRow("Width Value:", self.value_spin)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def _on_type_changed(self, index):
        if index == 0: # Variable
            self.value_spin.setEnabled(False)
            self.value_spin.setSuffix("")
        elif index == 1: # Percentage
            self.value_spin.setEnabled(True)
            self.value_spin.setSuffix("%")
            self.value_spin.setRange(0, 100)
        elif index == 2: # Fixed
            self.value_spin.setEnabled(True)
            self.value_spin.setSuffix(" px")
            self.value_spin.setRange(0, 10000)

    def get_length(self) -> QTextLength:
        idx = self.type_combo.currentIndex()
        val = self.value_spin.value()
        
        if idx == 0:
            return QTextLength(QTextLength.Type.VariableLength, 0)
        elif idx == 1:
            return QTextLength(QTextLength.Type.PercentageLength, val)
        elif idx == 2:
            return QTextLength(QTextLength.Type.FixedLength, val)
        return QTextLength()

class TableFeature:
    """Manages table operations for the RichTextEditor."""
    
    def __init__(self, editor: QTextEdit, parent: QWidget):
        self.editor = editor
        self.parent = parent
        self.menu = QMenu(parent)
        self.actions = {}

    def create_toolbar_button(self) -> QToolButton:
        """Create and configure the toolbar button for tables."""
        btn = QToolButton()
        btn.setText("Table")
        btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        self.menu.aboutToShow.connect(self._update_menu_state)
        btn.setMenu(self.menu)
        
        self._init_menu_actions()
        return btn

    def _init_menu_actions(self):
        """Initialize menu actions."""
        # Insert Table
        action_insert = QAction("Insert Table...", self.parent)
        action_insert.triggered.connect(self._insert_table)
        self.menu.addAction(action_insert)
        
        self.menu.addSeparator()
        
        # Rows
        self.actions['row_above'] = QAction("Insert Row Above", self.parent)
        self.actions['row_above'].triggered.connect(self._insert_row_above)
        self.menu.addAction(self.actions['row_above'])
        
        self.actions['row_below'] = QAction("Insert Row Below", self.parent)
        self.actions['row_below'].triggered.connect(self._insert_row_below)
        self.menu.addAction(self.actions['row_below'])
        
        # Cols
        self.actions['col_left'] = QAction("Insert Column Left", self.parent)
        self.actions['col_left'].triggered.connect(self._insert_col_left)
        self.menu.addAction(self.actions['col_left'])
        
        self.actions['col_right'] = QAction("Insert Column Right", self.parent)
        self.actions['col_right'].triggered.connect(self._insert_col_right)
        self.menu.addAction(self.actions['col_right'])
        
        self.menu.addSeparator()
        
        # Sizing
        self.actions['col_width'] = QAction("Column Width...", self.parent)
        self.actions['col_width'].triggered.connect(self._edit_column_width)
        self.menu.addAction(self.actions['col_width'])
        
        self.actions['distribute_cols'] = QAction("Distribute Columns Evenly", self.parent)
        self.actions['distribute_cols'].triggered.connect(self._distribute_columns)
        self.menu.addAction(self.actions['distribute_cols'])
        
        self.menu.addSeparator()
        
        # Delete
        self.actions['del_row'] = QAction("Delete Row", self.parent)
        self.actions['del_row'].triggered.connect(self._delete_row)
        self.menu.addAction(self.actions['del_row'])
        
        self.actions['del_col'] = QAction("Delete Column", self.parent)
        self.actions['del_col'].triggered.connect(self._delete_col)
        self.menu.addAction(self.actions['del_col'])
        
        self.actions['del_table'] = QAction("Delete Table", self.parent)
        self.actions['del_table'].triggered.connect(self._delete_table)
        self.menu.addAction(self.actions['del_table'])
        
        self.menu.addSeparator()
        
        # Merge/Split
        self.actions['merge'] = QAction("Merge Cells", self.parent)
        self.actions['merge'].triggered.connect(self._merge_cells)
        self.menu.addAction(self.actions['merge'])
        
        self.actions['split'] = QAction("Split Cells", self.parent)
        self.actions['split'].triggered.connect(self._split_cells)
        self.menu.addAction(self.actions['split'])
        
        self.menu.addSeparator()
        
        # Cell Properties
        self.actions['cell_color'] = QAction("Cell Background Color...", self.parent)
        self.actions['cell_color'].triggered.connect(self._set_cell_background)
        self.menu.addAction(self.actions['cell_color'])
        
        self.actions['cell_borders'] = QAction("Cell Border Styles...", self.parent)
        self.actions['cell_borders'].triggered.connect(self._edit_cell_borders)
        self.menu.addAction(self.actions['cell_borders'])

        self.actions['cell_props'] = QAction("Cell Properties...", self.parent)
        self.actions['cell_props'].triggered.connect(self._edit_cell_properties)
        self.menu.addAction(self.actions['cell_props'])
        
        self.menu.addSeparator()
        
        # Properties
        self.actions['props'] = QAction("Table Properties...", self.parent)
        self.actions['props'].triggered.connect(self._edit_table_properties)
        self.menu.addAction(self.actions['props'])

    def _update_menu_state(self):
        """Update enabled state of table actions."""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        in_table = table is not None
        
        for key in ['row_above', 'row_below', 'col_left', 'col_right', 
                   'del_row', 'del_col', 'del_table', 'props', 'cell_color', 
                   'cell_borders', 'cell_props', 'col_width', 'distribute_cols']:
            self.actions[key].setEnabled(in_table)
        
        # Merge/Split logic
        if in_table:
            self.actions['merge'].setEnabled(True) 
            self.actions['split'].setEnabled(True)
        else:
            self.actions['merge'].setEnabled(False)
            self.actions['split'].setEnabled(False)

    def extend_context_menu(self, menu: QMenu):
        """Add table actions to a context menu."""
        cursor = self.editor.textCursor()
        if not cursor.currentTable():
            return

        menu.addSeparator()
        table_menu = menu.addMenu("Table")
        if not table_menu:
            return
        
        # Insert
        insert_menu = table_menu.addMenu("Insert")
        if not insert_menu:
            return
        insert_menu.addAction(self.actions['row_above'])
        insert_menu.addAction(self.actions['row_below'])
        insert_menu.addAction(self.actions['col_left'])
        insert_menu.addAction(self.actions['col_right'])
        
        # Delete
        delete_menu = table_menu.addMenu("Delete")
        if not delete_menu:
            return
        delete_menu.addAction(self.actions['del_row'])
        delete_menu.addAction(self.actions['del_col'])
        delete_menu.addAction(self.actions['del_table'])
        
        table_menu.addSeparator()
        
        # Merge/Split
        table_menu.addAction(self.actions['merge'])
        table_menu.addAction(self.actions['split'])
        
        table_menu.addSeparator()
        
        # Sizing
        table_menu.addAction(self.actions['col_width'])
        table_menu.addAction(self.actions['distribute_cols'])
        
        table_menu.addSeparator()
        
        # Properties
        table_menu.addAction(self.actions['cell_color'])
        table_menu.addAction(self.actions['cell_borders'])
        table_menu.addAction(self.actions['cell_props'])
        table_menu.addAction(self.actions['props'])
        
        # Update state
        self._update_menu_state()

    def _insert_table(self):
        dialog = TableDialog(self.parent)
        if dialog.exec():
            data = dialog.get_data()
            cursor = self.editor.textCursor()
            
            fmt = QTextTableFormat()
            fmt.setCellPadding(5)
            fmt.setCellSpacing(0)
            fmt.setBorder(data['border'])
            fmt.setBorderStyle(self._get_border_style_enum(data['border_style']))
            fmt.setWidth(QTextLength(QTextLength.Type.PercentageLength, data['width']))
            
            cursor.insertTable(data['rows'], data['cols'], fmt)
    
    def _get_border_style_enum(self, name: str) -> QTextFrameFormat.BorderStyle:
        """Convert border style name to enum."""
        style_map = {
            "None": QTextFrameFormat.BorderStyle.BorderStyle_None,
            "Solid": QTextFrameFormat.BorderStyle.BorderStyle_Solid
        }
        return style_map.get(name, QTextFrameFormat.BorderStyle.BorderStyle_Solid)

    def _insert_row_above(self):
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            table.insertRows(cell.row(), 1)

    def _insert_row_below(self):
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            table.insertRows(cell.row() + 1, 1)

    def _insert_col_left(self):
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            table.insertColumns(cell.column(), 1)

    def _insert_col_right(self):
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            table.insertColumns(cell.column() + 1, 1)

    def _edit_column_width(self):
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            col_index = cell.column()
            fmt = table.format()
            constraints = fmt.columnWidthConstraints()
            
            # If constraints are empty, initialize them
            if not constraints:
                constraints = [QTextLength(QTextLength.Type.VariableLength, 0)] * table.columns()
            
            current_len = constraints[col_index]
            
            dialog = ColumnPropertiesDialog(current_len, self.parent)
            if dialog.exec():
                new_len = dialog.get_length()
                constraints[col_index] = new_len
                fmt.setColumnWidthConstraints(constraints)
                table.setFormat(fmt)

    def _distribute_columns(self):
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cols = table.columns()
            width_per_col = 100 / cols
            constraints = [QTextLength(QTextLength.Type.PercentageLength, width_per_col)] * cols
            fmt = table.format()
            fmt.setColumnWidthConstraints(constraints)
            table.setFormat(fmt)

    def _delete_row(self):
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            table.removeRows(cell.row(), 1)

    def _delete_col(self):
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            table.removeColumns(cell.column(), 1)

    def _delete_table(self):
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            start = table.firstCursorPosition()
            end = table.lastCursorPosition()
            cursor.setPosition(start.position() - 1)
            cursor.setPosition(end.position() + 1, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()

    def _merge_cells(self):
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            table.mergeCells(cursor)

    def _split_cells(self):
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            table.splitCell(cell.row(), cell.column(), 1, 1)

    def _edit_table_properties(self):
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            fmt = table.format()
            dialog = TablePropertiesDialog(fmt, self.parent)
            if dialog.exec():
                dialog.apply_to_format(fmt)
                table.setFormat(fmt)

    def _set_cell_background(self):
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            fmt = cell.format()
            color = QColorDialog.getColor(fmt.background().color(), self.parent, "Select Cell Background Color")
            if color.isValid():
                fmt.setBackground(color)
                cell.setFormat(fmt)
    
    def _edit_cell_borders(self):
        """Edit individual cell border styles."""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            char_fmt = cell.format()
            fmt = char_fmt.toTableCellFormat()
            
            # Ensure we have a valid table cell format
            if not isinstance(fmt, QTextTableCellFormat):
                new_fmt = QTextTableCellFormat()
                new_fmt.merge(char_fmt)
                fmt = new_fmt
            
            dialog = CellBorderDialog(fmt, self.parent)
            if dialog.exec():
                dialog.apply_to_format(fmt)
                cell.setFormat(fmt)

    def _edit_cell_properties(self):
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            char_fmt = cell.format()
            fmt = char_fmt.toTableCellFormat()
            
            # Ensure we have a valid table cell format
            if not isinstance(fmt, QTextTableCellFormat):
                new_fmt = QTextTableCellFormat()
                new_fmt.merge(char_fmt)
                fmt = new_fmt
            
            dialog = CellPropertiesDialog(fmt, self.parent)
            if dialog.exec():
                dialog.apply_to_format(fmt)
                cell.setFormat(fmt)
