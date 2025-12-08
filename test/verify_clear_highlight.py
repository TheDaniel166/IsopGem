from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
import sys
from pillars.document_manager.ui.rich_text_editor import RichTextEditor

def verify_clear_highlight():
    app = QApplication(sys.argv)
    editor = RichTextEditor()
    
    # Check if _clear_highlight method exists
    if not hasattr(editor, '_clear_highlight'):
        print("FAIL: _clear_highlight method missing")
        return False
        
    # Simulate setting a color
    editor.editor.setTextBackgroundColor(QColor("red"))
    
    # Call clear
    editor._clear_highlight()
    
    # Check current color (should be transparent/invalid or white depending on implement)
    # Qt.GlobalColor.transparent is what we set
    current_bg = editor.editor.textBackgroundColor()
    if current_bg == QColor(Qt.GlobalColor.transparent):
         print("SUCCESS: Highlight cleared to transparent")
         return True
    
    print(f"FAIL: Color is {current_bg.name()}")
    return False

if __name__ == "__main__":
    verify_clear_highlight()
