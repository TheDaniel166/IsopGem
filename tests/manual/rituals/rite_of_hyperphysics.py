import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor

sys.path.append(os.path.abspath("src"))
from pillars.time_mechanics.ui.dynamis_window import PillarGauge, TrigramItem, TzolkinDynamisWindow

def rite_of_hyperphysics():
    print("Initiating Rite of Hyper-Physics...")
    app = QApplication(sys.argv)
    
    # 1. Test PillarGauge Logic
    print("Testing PillarGauge Logic...")
    gauge = PillarGauge()
    
    # Odd Column (1)
    gauge.update_state("000", "000", 1)
    if gauge.col_type == "ODD":
        print("  Tone 1 -> ODD Type: CONFIRMED")
    else:
        print(f"  Tone 1 -> ODD Type: FAILED ({gauge.col_type})")
        
    # Even Column (2)
    gauge.update_state("000", "000", 2)
    if gauge.col_type == "EVEN":
        print("  Tone 2 -> EVEN Type: CONFIRMED")
    else:
        print(f"  Tone 2 -> EVEN Type: FAILED ({gauge.col_type})")
        
    # Mystic Column (7)
    gauge.update_state("000", "000", 7)
    if gauge.col_type == "MYSTIC":
        print("  Tone 7 -> MYSTIC Type: CONFIRMED")
    else:
        print(f"  Tone 7 -> MYSTIC Type: FAILED ({gauge.col_type})")

    # 2. Test Window Instantiation & Paint
    print("Summoning Dynamis Window...")
    window = TzolkinDynamisWindow()
    window.show()
    
    print("  Processing Events (Triggering Paint)...")
    # Process events to force paint
    app.processEvents()
    
    if window:
        print("  Window Summoned & Painted: SUCCESS")
    
    print("Rite Complete.")
    # Clean exit
    window.close()

if __name__ == "__main__":
    rite_of_hyperphysics()
