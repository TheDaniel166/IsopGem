
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QTextEdit
from PyQt6.QtCore import Qt

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from pillars.document_manager.ui.rich_text_editor import RichTextEditor
from pillars.document_manager.utils.parsers import DocumentParser

def verify_editor_ltr():
    app = QApplication(sys.argv)
    editor = RichTextEditor()
    
    # Check default direction
    direction = editor.editor.layoutDirection()
    expected = Qt.LayoutDirection.LeftToRight
    
    if direction == expected:
        print("PASS: RichTextEditor initialized with LTR direction.")
    else:
        print(f"FAIL: RichTextEditor has direction {direction}, expected {expected}")
        sys.exit(1)

    # Check set_html enforcement
    editor.set_html("<p dir='rtl'>Some RTL content attempt</p>")
    direction = editor.editor.layoutDirection()
    if direction == expected:
        print("PASS: RichTextEditor maintained LTR after set_html.")
    else:
        print(f"FAIL: RichTextEditor switched to {direction} after set_html.")
        sys.exit(1)

def verify_parser_integrity():
    # We can't easily test docx without a file, but we can ensure the function exists and doesn't crash on import
    try:
        if hasattr(DocumentParser, '_parse_docx'):
            print("PASS: DocumentParser has _parse_docx method.")
        else:
            print("FAIL: _parse_docx missing.")
    except Exception as e:
        print(f"FAIL: Parser check failed: {e}")

if __name__ == "__main__":
    verify_editor_ltr()
    verify_parser_integrity()
