"""
List Features - The Ordinal Forge.
Manages bullet, numbered, and checklist operations for the RichTextEditor.
"""
from PyQt6.QtGui import (
    QTextListFormat, QTextBlockFormat, QTextCursor, QAction, QIcon
)
from PyQt6.QtWidgets import QToolButton, QMenu, QDialog, QVBoxLayout, QFormLayout, QSpinBox, QDialogButtonBox
from PyQt6.QtCore import Qt


# Define all available list styles with friendly names
LIST_STYLES = {
    # Bullet styles
    "Disc (●)": QTextListFormat.Style.ListDisc,
    "Circle (○)": QTextListFormat.Style.ListCircle,
    "Square (■)": QTextListFormat.Style.ListSquare,
    # Number styles
    "Decimal (1, 2, 3)": QTextListFormat.Style.ListDecimal,
    "Lower Alpha (a, b, c)": QTextListFormat.Style.ListLowerAlpha,
    "Upper Alpha (A, B, C)": QTextListFormat.Style.ListUpperAlpha,
    "Lower Roman (i, ii, iii)": QTextListFormat.Style.ListLowerRoman,
    "Upper Roman (I, II, III)": QTextListFormat.Style.ListUpperRoman,
}

# Quick access groups
BULLET_STYLES = ["Disc (●)", "Circle (○)", "Square (■)"]
NUMBER_STYLES = ["Decimal (1, 2, 3)", "Lower Alpha (a, b, c)", "Upper Alpha (A, B, C)", 
                 "Lower Roman (i, ii, iii)", "Upper Roman (I, II, III)"]


class ListFeature:
    """
    Manages list operations (bullets, numbers) and indentation
    for the RichTextEditor.
    """
    def __init__(self, editor, parent=None):
        """
          init   logic.
        
        Args:
            editor: Description of editor.
            parent: Description of parent.
        
        """
        self.editor = editor
        self.parent = parent

    def toggle_list(self, style: QTextListFormat.Style):
        """Toggle the specified list style for the current selection."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        
        current_list = cursor.currentList()
        if current_list:
            fmt = current_list.format()
            # If the style matches, turn it off (convert to standard block)
            if fmt.style() == style:
                block_fmt = QTextBlockFormat()
                block_fmt.setObjectIndex(-1)  # Remove list association
                cursor.setBlockFormat(block_fmt)
            else:
                # specific style change (e.g. bullet -> number)
                list_fmt = QTextListFormat()
                list_fmt.setStyle(style)
                list_fmt.setIndent(fmt.indent())  # Preserve indent
                current_list.setFormat(list_fmt)
        else:
            # Create new list
            list_fmt = QTextListFormat()
            list_fmt.setStyle(style)
            cursor.createList(list_fmt)
            
        cursor.endEditBlock()
        self.editor.setFocus()

    def set_list_style_by_name(self, name: str):
        """Set list style using the friendly name."""
        if name in LIST_STYLES:
            self.toggle_list(LIST_STYLES[name])

    def set_start_number(self, start: int = 1):
        """Set the starting number for a numbered list."""
        cursor = self.editor.textCursor()
        current_list = cursor.currentList()
        if current_list:
            fmt = current_list.format()
            # Only applies to numbered lists
            if fmt.style() in [QTextListFormat.Style.ListDecimal,
                              QTextListFormat.Style.ListLowerAlpha,
                              QTextListFormat.Style.ListUpperAlpha,
                              QTextListFormat.Style.ListLowerRoman,
                              QTextListFormat.Style.ListUpperRoman]:
                fmt.setStart(start)
                current_list.setFormat(fmt)

    def show_start_number_dialog(self):
        """Show dialog to set the starting number for a list."""
        from PyQt6.QtWidgets import QMessageBox
        
        cursor = self.editor.textCursor()
        current_list = cursor.currentList()
        
        if not current_list:
            QMessageBox.information(
                self.parent, 
                "Not in a List", 
                "Please place your cursor inside a numbered list first."
            )
            return
        
        # Check if it's a numbered list
        style = current_list.format().style()
        if style not in [QTextListFormat.Style.ListDecimal,
                        QTextListFormat.Style.ListLowerAlpha,
                        QTextListFormat.Style.ListUpperAlpha,
                        QTextListFormat.Style.ListLowerRoman,
                        QTextListFormat.Style.ListUpperRoman]:
            QMessageBox.information(
                self.parent,
                "Not a Numbered List",
                "Start number can only be set for numbered lists, not bullet lists."
            )
            return
        
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Set Start Number")
        dialog.setMinimumWidth(250)
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        
        start_spin = QSpinBox()
        start_spin.setRange(1, 9999)
        start_spin.setValue(current_list.format().start() if current_list.format().start() > 0 else 1)
        form.addRow("Start at:", start_spin)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.set_start_number(start_spin.value())

    def remove_list(self):
        """Remove list formatting from the current selection."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        
        current_list = cursor.currentList()
        if current_list:
            block_fmt = QTextBlockFormat()
            block_fmt.setObjectIndex(-1)
            block_fmt.setIndent(0)
            cursor.setBlockFormat(block_fmt)
        
        cursor.endEditBlock()
        self.editor.setFocus()

    def indent(self):
        """Increase indentation or list level."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        
        current_list = cursor.currentList()
        if current_list:
            fmt = current_list.format()
            current_indent = fmt.indent()
            
            new_list_fmt = QTextListFormat()
            new_list_fmt.setStyle(fmt.style())
            new_list_fmt.setIndent(current_indent + 1)
            cursor.createList(new_list_fmt)
        else:
            block_fmt = cursor.blockFormat()
            current_indent = block_fmt.indent()
            block_fmt.setIndent(current_indent + 1)
            cursor.setBlockFormat(block_fmt)
            
        cursor.endEditBlock()

    def outdent(self):
        """Decrease indentation or list level."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        
        current_list = cursor.currentList()
        if current_list:
            fmt = current_list.format()
            current_indent = fmt.indent()
            
            if current_indent > 1:
                new_list_fmt = QTextListFormat()
                new_list_fmt.setStyle(fmt.style())
                new_list_fmt.setIndent(current_indent - 1)
                cursor.createList(new_list_fmt)
            else:
                block_fmt = QTextBlockFormat()
                block_fmt.setObjectIndex(-1)
                block_fmt.setIndent(0)
                cursor.setBlockFormat(block_fmt)
        else:
            block_fmt = cursor.blockFormat()
            current_indent = block_fmt.indent()
            if current_indent > 0:
                block_fmt.setIndent(current_indent - 1)
                cursor.setBlockFormat(block_fmt)
                
        cursor.endEditBlock()

    def get_current_list_style_name(self) -> str:
        """Get the name of the current list style, or None."""
        cursor = self.editor.textCursor()
        current_list = cursor.currentList()
        if current_list:
            style = current_list.format().style()
            for name, s in LIST_STYLES.items():
                if s == style:
                    return name
        return None

    def toggle_checklist(self):
        """Toggle checklist style (☐ / ☑) for the current line(s)."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        
        # We need to iterate over selected blocks if there's a selection
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        cursor.setPosition(start)
        block = cursor.block()
        
        # Define checklist states
        unchecked = "☐ "
        checked = "☑ "
        
        while block.isValid() and block.position() <= end:
            cursor.setPosition(block.position())
            text = block.text()
            
            if text.startswith(unchecked):
                # Toggle to checked
                cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor, 2)
                cursor.insertText(checked)
            elif text.startswith(checked):
                # Toggle to unchecked (or remove? standard behavior is toggle)
                cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor, 2)
                cursor.insertText(unchecked)
            else:
                # Add checkbox
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                cursor.insertText(unchecked)
                
            block = block.next()
            
        cursor.endEditBlock()
        self.editor.setFocus()
