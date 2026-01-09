from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QTextCharFormat
import sys
from pillars.document_manager.ui.rich_text_editor import RichTextEditor

def verify_semantic_headings():
    app = QApplication(sys.argv)
    editor = RichTextEditor()
    editor.show()
    
    # Check if styles dict exists
    if not hasattr(editor, 'styles'):
        print("FAIL: 'styles' dictionary not found")
        return False

    # Insert text and select it (IMPORTANT)
    editor.editor.setPlainText("Test Content")
    cursor = editor.editor.textCursor()
    cursor.select(cursor.SelectionType.Document)
    editor.editor.setTextCursor(cursor)
        
    # Manual Test
    print("DEBUG: Manual format test - setting Arial 24 Bold")
    cursor = editor.editor.textCursor()
    fmt_manual = QTextCharFormat()
    fmt_manual.setFontFamily("Arial")
    fmt_manual.setFontPointSize(24.0)
    fmt_manual.setFontWeight(QFont.Weight.Bold)
    cursor.mergeCharFormat(fmt_manual)
    # Apply back to editor? Merge changes the selection.
    
    check_fmt = cursor.charFormat()
    print(f"DEBUG: Manual Result (Same Cursor) size={check_fmt.fontPointSize()} family={check_fmt.fontFamily()} weight={check_fmt.fontWeight()}")
    
    # New cursor
    cursor_new = editor.editor.textCursor()
    check_fmt = cursor_new.charFormat()
    print(f"DEBUG: Manual Result (New Cursor) size={check_fmt.fontPointSize()} family={check_fmt.fontFamily()} weight={check_fmt.fontWeight()}")
    
    # Test "Heading 1"
    print("DEBUG: Testing _apply_style('Heading 1')")
    editor._apply_style("Heading 1")
    
    cursor = editor.editor.textCursor()
    fmt = cursor.charFormat()
    print(f"DEBUG: Heading 1 Result size={fmt.fontPointSize()} family={fmt.fontFamily()} weight={fmt.fontWeight()}")
    
    # Heading 1 should be 24pt and Bold
    if int(fmt.fontPointSize()) != 24:
        print(f"FAIL: Heading 1 size is {fmt.fontPointSize()}, expected 24")
        return False
        
    if fmt.fontWeight() != QFont.Weight.Bold:
        print(f"FAIL: Heading 1 weight is {fmt.fontWeight()}")
        return False
        
    # Test "Normal"
    editor._apply_style("Normal")
    fmt = cursor.charFormat()
    
    if int(fmt.fontPointSize()) != 12:
        print(f"FAIL: Normal size is {fmt.fontPointSize()}, expected 12")
        return False
        
    print("SUCCESS: Semantic styles applied correctly")
    return True

if __name__ == "__main__":
    verify_semantic_headings()
