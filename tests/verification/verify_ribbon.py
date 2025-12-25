from PyQt6.QtWidgets import QApplication
import sys
from pillars.document_manager.ui.rich_text_editor import RichTextEditor
from pillars.document_manager.ui.ribbon_widget import RibbonWidget

def verify_ribbon():
    app = QApplication(sys.argv)
    
    editor = RichTextEditor()
    
    # Check if 'ribbon' attribute exists
    if not hasattr(editor, 'ribbon'):
        print("FAIL: editor.ribbon not found")
        return False
        
    # Check if it is indeed a RibbonWidget
    if not isinstance(editor.ribbon, RibbonWidget):
        print(f"FAIL: editor.ribbon is {type(editor.ribbon)}, expected RibbonWidget")
        return False
        
    # Check if we have tabs (Home, Insert)
    if editor.ribbon.count() < 2:
        print(f"FAIL: Ribbon has {editor.ribbon.count()} tabs, expected >= 2")
        return False
        
    print("SUCCESS: RichTextEditor uses RibbonWidget with tabs.")
    return True

if __name__ == "__main__":
    verify_ribbon()
