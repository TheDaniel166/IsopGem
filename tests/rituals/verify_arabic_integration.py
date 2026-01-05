"""Rite of Arabic Integration Verification.

This ritual verifies that the Arabic Abjad Gematria system has been correctly
integrated into the codebase, including shared services and keyboard layouts.
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

def verify_integration():
    """Verify Arabic Gematria integration."""
    print("🔮 Beginning Rite of Arabic Integration Verification...")
    
    # 1. Verify Shared Services Export
    try:
        from shared.services.gematria import (
            ArabicGematriaCalculator, ArabicMaghrebiCalculator,
            ArabicSmallValueCalculator, ArabicOrdinalCalculator
        )
        print("✅ Arabic calculators successfully exported from shared services.")
    except ImportError as e:
        print(f"❌ Failed to import Arabic calculators: {e}")
        return False

    # 2. Verify Keyboard Layout
    try:
        from shared.ui.keyboard_layouts import LAYOUTS
        if "arabic" in LAYOUTS:
            print("✅ Arabic keyboard layout registered in LAYOUTS.")
            # Verify explicit check
            layout = LAYOUTS["arabic"]
            if layout.name == "arabic" and len(layout.rows) == 3:
                 print("✅ Arabic layout structure appears correct.")
            else:
                 print("❌ Arabic layout structure mismatch.")
        else:
            print("❌ 'arabic' key missing from LAYOUTS.")
            return False
    except ImportError as e:
        print(f"❌ Failed to import LAYOUTS: {e}")
        return False
        
    try:
        from shared.ui.virtual_keyboard import VirtualKeyboard # Inspecting class (not instantiating without app)
        # We can't easily check internal list of a class without instantiation or source inspection,
        # but if the code runs, at least the file is valid.
        pass
    except ImportError:
        print("❌ Failed to import VirtualKeyboard.")
        return False

    # 3. Verify Calculation Logic
    try:
        calc = ArabicGematriaCalculator()
        
        # Test Case 1: Allah (God) -> Aleph(1) + Lam(30) + Lam(30) + Ha(5) = 66
        # Note: We need to use the exact characters defined in the map.
        # Mapping: 'ا': 1, 'ل': 30, 'ه': 5
        text = "الله" 
        # Breakdown:
        # ا (Aleph) = 1
        # ل (Lam) = 30
        # ل (Lam) = 30
        # ه (Ha) = 5
        # Total = 66
        
        value = calc.calculate(text)
        print(f"🧮 Calculation Test: '{text}'")
        print(f"   Expected: 66")
        print(f"   Actual:   {value}")
        
        if value == 66:
             print("✅ Calculation accuracy verified (Allah = 66).")
        else:
             print(f"❌ Calculation accuracy failed. Got {value}.")
             return False
             
        # Test Case 2: Bism (In the name) -> Ba(2) + Sin(60) + Mim(40) = 102
        text2 = "بسم"
        value2 = calc.calculate(text2)
        if value2 == 102:
            print("✅ Calculation accuracy verified (Bism = 102).")
        else:
            print(f"❌ Calculation accuracy failed for Bism. Got {value2}.")
            return False

    except Exception as e:
        print(f"❌ Calculation verification error: {e}")
        return False

    print("\n✨ Rite of Arabic Integration Complete. The System is Whole.")
    return True

if __name__ == "__main__":
    if verify_integration():
        sys.exit(0)
    else:
        sys.exit(1)
