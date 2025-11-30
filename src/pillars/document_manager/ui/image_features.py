"""Image management features for RichTextEditor."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QSpinBox, 
    QDialogButtonBox, QFileDialog, QWidget, QTextEdit,
    QMenu, QMessageBox
)
from PyQt6.QtGui import QTextCursor, QTextImageFormat, QIcon, QAction
from PyQt6.QtCore import Qt

class ImagePropertiesDialog(QDialog):
    """Dialog for editing image properties."""
    def __init__(self, fmt: QTextImageFormat, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Properties")
        self.fmt = fmt
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 2000)
        self.width_spin.setValue(int(self.fmt.width()))
        form.addRow("Width:", self.width_spin)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 2000)
        self.height_spin.setValue(int(self.fmt.height()))
        form.addRow("Height:", self.height_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def apply_to_format(self, fmt: QTextImageFormat):
        fmt.setWidth(self.width_spin.value())
        fmt.setHeight(self.height_spin.value())

class ImageFeature:
    """Manages image operations for the RichTextEditor."""
    
    def __init__(self, editor: QTextEdit, parent: QWidget):
        self.editor = editor
        self.parent = parent
        self._init_actions()

    def _init_actions(self):
        self.action_insert = QAction("Insert Image...", self.parent)
        self.action_insert.setToolTip("Insert Image")
        self.action_insert.triggered.connect(self._insert_image)
        
        self.action_props = QAction("Image Properties...", self.parent)
        self.action_props.triggered.connect(self._edit_image_properties)

    def create_toolbar_action(self) -> QAction:
        """Return the insert image action for the toolbar."""
        return self.action_insert

    def extend_context_menu(self, menu: QMenu):
        """Add image actions to context menu if applicable."""
        # Check if we are near an image
        cursor = self.editor.textCursor()
        
        # Check char before
        fmt_before = cursor.charFormat()
        is_img_before = fmt_before.isImageFormat()
        
        # Check char after
        cursor_after = QTextCursor(cursor)
        cursor_after.movePosition(QTextCursor.MoveOperation.Right)
        fmt_after = cursor_after.charFormat()
        is_img_after = fmt_after.isImageFormat()
        
        if is_img_before or is_img_after:
            menu.addSeparator()
            menu.addAction(self.action_props)

    def _insert_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, 
            "Select Image", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            cursor = self.editor.textCursor()
            image_fmt = QTextImageFormat()
            image_fmt.setName(file_path)
            cursor.insertImage(image_fmt)

    def _edit_image_properties(self):
        cursor = self.editor.textCursor()
        
        # Determine which image we are editing and select it
        fmt_before = cursor.charFormat()
        
        cursor_after = QTextCursor(cursor)
        cursor_after.movePosition(QTextCursor.MoveOperation.Right)
        fmt_after = cursor_after.charFormat()
        
        target_fmt = None
        
        if fmt_before.isImageFormat():
            target_fmt = fmt_before.toImageFormat()
            # Select the character before
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
        elif fmt_after.isImageFormat():
            target_fmt = fmt_after.toImageFormat()
            # Select the character after
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
            
        if target_fmt:
            dialog = ImagePropertiesDialog(target_fmt, self.parent)
            if dialog.exec():
                dialog.apply_to_format(target_fmt)
                # Apply the updated format to the selection
                # Note: We need to ensure the cursor has the selection we made above
                # But wait, 'cursor' is a copy if we got it from textCursor()?
                # Yes, textCursor() returns a copy. We need to set it back to the editor 
                # OR use the editor's cursor to make the selection.
                
                # Let's do this properly:
                # 1. Create a cursor that selects the image
                # 2. Apply format
                
                edit_cursor = self.editor.textCursor()
                # Re-detect position logic since we are in a new scope/cursor
                # Actually, we can just use the logic we just did but on the editor's cursor
                
                f_before = edit_cursor.charFormat()
                c_after = QTextCursor(edit_cursor)
                c_after.movePosition(QTextCursor.MoveOperation.Right)
                f_after = c_after.charFormat()
                
                if f_before.isImageFormat():
                    edit_cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
                elif f_after.isImageFormat():
                    edit_cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
                
                # Now apply
                edit_cursor.setCharFormat(target_fmt)
