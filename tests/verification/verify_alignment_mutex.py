from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QActionGroup
import sys
from pillars.document_manager.ui.rich_text_editor import RichTextEditor

def verify_alignment_mutex():
    app = QApplication(sys.argv)
    editor = RichTextEditor()
    
    # Check if actions are in a group
    left = editor.action_align_left
    center = editor.action_align_center
    
    group = left.actionGroup()
    if not group:
        print("FAIL: Left align action not in a group")
        return False
        
    if center.actionGroup() != group:
        print("FAIL: Center align action not in the same group")
        return False
        
    if not group.isExclusive():
        print("FAIL: Action group is not exclusive")
        return False
        
    # Simulate clicks
    left.setChecked(True)
    if not left.isChecked(): 
         print("FAIL: Left should be checked")
         return False
         
    center.setChecked(True) # Should uncheck left
    
    if left.isChecked():
        print("FAIL: Left is still checked after checking Center")
        return False
        
    print("SUCCESS: Alignment buttons are mutually exclusive")
    return True

if __name__ == "__main__":
    verify_alignment_mutex()
