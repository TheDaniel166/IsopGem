from PyQt6.QtGui import (
    QTextListFormat, QTextBlockFormat, QTextCursor, QAction, QIcon
)
from PyQt6.QtWidgets import QToolButton, QMenu
from PyQt6.QtCore import Qt

class ListFeature:
    """
    Manages list operations (bullets, numbers) and indentation
    for the RichTextEditor.
    """
    def __init__(self, editor, parent=None):
        self.editor = editor
        self.parent = parent # The main window or widget, for parenting actions/menus

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
                block_fmt.setObjectIndex(-1) # Remove list association
                cursor.setBlockFormat(block_fmt)
            else:
                # specific style change (e.g. bullet -> number)
                list_fmt = QTextListFormat()
                list_fmt.setStyle(style)
                current_list.setFormat(list_fmt)
        else:
            # Create new list
            list_fmt = QTextListFormat()
            list_fmt.setStyle(style)
            cursor.createList(list_fmt)
            
        cursor.endEditBlock()
        # Ensure focus remains
        self.editor.setFocus()

    def indent(self):
        """Increase indentation or list level."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        
        current_list = cursor.currentList()
        if current_list:
            # Inside a list: Create a sub-list (new list with higher indent) for selected items
            # We need to get the current list format to preserve style (bullet/number)
            fmt = current_list.format()
            current_indent = fmt.indent()
            
            # Create a new list format based on the old one
            new_list_fmt = QTextListFormat()
            new_list_fmt.setStyle(fmt.style())
            new_list_fmt.setIndent(current_indent + 1)
            
            # This will effectively split the current list or create a nested structure
            # for the currently selected blocks.
            cursor.createList(new_list_fmt)
        else:
            # Standard Paragraph: Increase margin
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
            # Inside a list: Decrease nesting level
            fmt = current_list.format()
            current_indent = fmt.indent()
            
            if current_indent > 1:
                # Decrease indentation level
                new_list_fmt = QTextListFormat()
                new_list_fmt.setStyle(fmt.style())
                new_list_fmt.setIndent(current_indent - 1)
                cursor.createList(new_list_fmt)
            else:
                # Break out of list (level 1 -> 0)
                # Removing the list format effectively turns it into a standard block
                block_fmt = QTextBlockFormat()
                block_fmt.setObjectIndex(-1)
                # We might want to remove indent completely or keep paragraph indent?
                # Standard behavior: remove list bullet/number, keep paragraph indent 0
                block_fmt.setIndent(0) 
                cursor.setBlockFormat(block_fmt)
        else:
            # Standard Paragraph: Decrease margin
            block_fmt = cursor.blockFormat()
            current_indent = block_fmt.indent()
            if current_indent > 0:
                block_fmt.setIndent(current_indent - 1)
                cursor.setBlockFormat(block_fmt)
                
        cursor.endEditBlock()
