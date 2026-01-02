
import sys
import os
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QScrollArea, QGroupBox

# Set pythonpath
sys.path.append(os.getcwd())

from src.shared.ui.rich_text_editor.image_features import ImageEditorDialog

def run():
    app = QApplication(sys.argv)
    # Instantiate with None (no parent needed for test)
    dialog = ImageEditorDialog(None)
    
    # Check Main Layout
    layout = dialog.layout()
    if not isinstance(layout, QHBoxLayout):
        print("FAIL: Main layout is not Horizontal (QHBoxLayout)")
        sys.exit(1)
        
    print(f"Main Layout Item Count: {layout.count()}")
    if layout.count() < 2:
        print("FAIL: Expected at least 2 panels (Left/Right)")
        sys.exit(1)
        
    # Check Right Panel for ScrollArea
    # Items in layout wrap widgets
    # right panel is usually the last one
    right_widget = layout.itemAt(layout.count() - 1).widget()
    if not right_widget:
         print("FAIL: Right item is not a widget")
         sys.exit(1)
         
    scrolls = right_widget.findChildren(QScrollArea)
    if not scrolls:
        print("FAIL: No QScrollArea found in right panel")
        sys.exit(1)
        
    print("PASS: Layout structure verified (Horizontal, 2-Pane, ScrollArea present).")
    
    # Verify Critical Attributes (Regressions)
    if not hasattr(dialog, 'lbl_loading'):
        print("FAIL: lbl_loading attribute missing!")
        sys.exit(1)
        
    print("PASS: Critical attributes verified.")

if __name__ == "__main__":
    run()
