import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QAction, QIcon

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from pillars.document_manager.ui.ribbon_widget import RibbonWidget
except ImportError as e:
    print(f"FAILED: Could not import RibbonWidget: {e}")
    sys.exit(1)

def rite_of_ribbon():
    app = QApplication(sys.argv)
    print("Beginning the Rite of Ribbon...")
    
    # 1. Instantiate the Widget (Saturn)
    try:
        ribbon = RibbonWidget()
        ribbon.show()
        print("[✓] Saturn: Structure is sound (RibbonWidget instantiated).")
    except Exception as e:
        print(f"[X] Saturn: Failed to instantiate ribbon. {e}")
        sys.exit(1)
        
    # 2. Add a Tab (Jupiter)
    try:
        tab = ribbon.add_ribbon_tab("Home")
        print("[✓] Jupiter: Expansion successful (Tab added).")
    except Exception as e:
        print(f"[X] Jupiter: Failed to add tab. {e}")
        sys.exit(1)
        
    # 3. Add a Group (Mars)
    try:
        group = tab.add_group("Clipboard")
        print("[✓] Mars: Boundaries established (Group added).")
    except Exception as e:
        print(f"[X] Mars: Failed to add group. {e}")
        sys.exit(1)
        
    # 4. Add an Action (Sun)
    try:
        action = QAction("Paste", ribbon)
        group.add_action(action)
        print("[✓] Sun: Vitality confirmed (Action added to group).")
    except Exception as e:
        print(f"[X] Sun: Failed to add action. {e}")
        sys.exit(1)
        
    # 5. Add Advanced Features (Mercury)
    try:
        # Context Category
        ctx = ribbon.add_context_category("Tools")
        
        # Gallery
        gallery_grp = tab.add_group("Styles")
        gallery = gallery_grp.add_gallery()
        gallery.add_item("Style 1", QIcon())
        
        # QAT
        ribbon.add_quick_access_button(action)
        
        print("[✓] Mercury: Communication channels open (Advanced features added).")
    except Exception as e:
        print(f"[X] Mercury: Failed to add advanced features. {e}")
        sys.exit(1)
        
    print("All Seals Broken. The Ribbon is functional.")

if __name__ == "__main__":
    rite_of_ribbon()
