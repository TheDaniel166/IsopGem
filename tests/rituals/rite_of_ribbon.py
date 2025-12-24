import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QAction

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from pillars.document_manager.ui.ribbon_widget import RibbonWidget
except ImportError as e:
    print(f"FAILED: Could not import RibbonWidget: {e}")
    sys.exit(1)

def rite_of_ribbon():
    app = QApplication(sys.argv)
    
    # Test 1: Instantiation
    try:
        ribbon = RibbonWidget()
        print("[✓] Saturn: Structure is sound (RibbonWidget instantiated).")
    except Exception as e:
        print(f"[X] Saturn: Failed to instantiate RibbonWidget: {e}")
        return

    # Test 2: Add Tab (Category)
    try:
        tab = ribbon.add_ribbon_tab("Test Home")
        print("[✓] Jupiter: Expansion successful (Tab added).")
    except Exception as e:
        print(f"[X] Jupiter: Failed to add tab: {e}")
        return

    # Test 3: Add Group (Panel)
    try:
        group = tab.add_group("Test Group")
        print("[✓] Mars: Boundaries established (Group added).")
    except Exception as e:
        print(f"[X] Mars: Failed to add group: {e}")
        return

    # Test 4: Add Action (Button)
    try:
        action = QAction("Test Action", ribbon)
        group.add_action(action)
        print("[✓] Sun: Vitality confirmed (Action added to group).")
    except Exception as e:
        print(f"[X] Sun: Failed to add action: {e}")
        return

    print("All Seals Broken. The Ribbon is functional.")

if __name__ == "__main__":
    rite_of_ribbon()
