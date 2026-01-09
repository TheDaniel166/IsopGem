
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

def rite_of_saturn():
    print("Beginning the Rite of Saturn (Import Verification)...")
    
    # We need to mock QApplication if we want to instantiate QMainWindow or QWidget
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    try:
        from shared.database import init_db
        init_db()
        print("   [SUCCESS] Database initialized.")
    except Exception as e:
        print(f"   [WARNING] DB Init failed: {e}")

    try:
        print("1. Summoning the Time Mechanics Hub...")
        from pillars.time_mechanics.ui import TimeMechanicsHub
        hub = TimeMechanicsHub()
        print("   [SUCCESS] Hub instantiated.")
    except Exception as e:
        print(f"   [FAILURE] Hub could not be summoned: {e}")
        return False

    try:
        print("2. Summoning the Main Window (Integration Check)...")
        # We need to mock QApplication if we want to instantiate QMainWindow
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        
        from main import IsopGemMainWindow
        window = IsopGemMainWindow()
        
        # Check if Time Mechanics tab is present (index 7 or simply by checking existence)
        found = False
        for i in range(window.tabs.count()):
            name = window.tabs.tabText(i)
            print(f"   - Found Tab: {name}")
            if "Time Mechanics" in name:
                found = True
        
        if found:
            print("   [SUCCESS] Time Mechanics Pillar found in Temple.")
        else:
            print("   [FAILURE] Time Mechanics Pillar NOT found in Temple tabs.")
            return False
            
    except Exception as e:
        print(f"   [FAILURE] Main Window crashed: {e}")
        return False
        
    print("The Rite of Saturn is passed.")
    return True

if __name__ == "__main__":
    success = rite_of_saturn()
    sys.exit(0 if success else 1)
