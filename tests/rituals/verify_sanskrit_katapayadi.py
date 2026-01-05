"""Rite of Sanskrit Integration Verification.

This ritual verifies that the Sanskrit Katapayadi Gematria system has been corrected
integrated into the codebase, including shared services and keyboard layouts.
It also verifies the specific positional integer logic.
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

def verify_integration():
    """Verify Sanskrit Gematria integration."""
    print("🕉️ Beginning Rite of Sanskrit Integration Verification...")
    
    # 1. Verify Shared Services Export
    try:
        from shared.services.gematria import SanskritKatapayadiCalculator
        print("✅ Sanskrit calculator successfully exported from shared services.")
    except ImportError as e:
        print(f"❌ Failed to import Sanskrit calculator: {e}")
        return False

    # 2. Verify Keyboard Layout
    try:
        from shared.ui.keyboard_layouts import LAYOUTS
        if "sanskrit" in LAYOUTS:
            print("✅ Sanskrit keyboard layout registered in LAYOUTS.")
            layout = LAYOUTS["sanskrit"]
            if layout.name == "sanskrit" and len(layout.rows) == 3:
                 print("✅ Sanskrit layout structure appears correct.")
            else:
                 print("❌ Sanskrit layout structure mismatch.")
        else:
            print("❌ 'sanskrit' key missing from LAYOUTS.")
            return False
    except ImportError as e:
        print(f"❌ Failed to import LAYOUTS: {e}")
        return False

    # 3. Verify Calculation Logic
    try:
        calc = SanskritKatapayadiCalculator()
        
        # Check Engine
        try:
            import katapayadi
            print("ℹ️  'katapayadi' library found (Engine: Hybrid).")
        except ImportError:
            print("ℹ️  'katapayadi' library MISSING or BROKEN (Engine: Manual Fallback).")
        except Exception:
             print("ℹ️  'katapayadi' library BROKEN (Engine: Manual Fallback).")
        
        # Test Case 1: Gopi (Ga=3, Pa=1) -> 31
        # ग (Ga) = 3
        # प (Pa) = 1 (plus 'i' matra which is ignored)
        # Note: We need to construct valid Devanagari string.
        # "Gopi" = ग (Ga) + ो (o matra) + प (Pa) + ी (i matra)
        # Actually in Katapayadi, 'Go' is Ga + o. 
        # Ga (3). o is vowel, ignored as matra.
        # Pi is Pa + i.
        # Pa (1). i is vowel, ignored as matra.
        # Result: 31.
        
        text1 = "गोपी" # Gopi
        val1 = calc.calculate(text1)
        print(f"🧮 Calculation Test: '{text1}' (Gopi)")
        print(f"   Expected: 31")
        print(f"   Actual:   {val1}")
        
        if val1 == 31:
             print("✅ Gopi verified.")
        else:
             print(f"❌ Gopi failed. Got {val1}.")
             return False

        # Test Case 2: Pi Value (classic verse)
        # "Go-pi-bha-gya-ma-dhu-vra-ta-shri-ngi-sho-da-dhi-san-dhi-ga..."
        # Just test first few chars: "Gopibhagya" -> 3141592...
        # ga=3, pa=1, bha=4, ya=1, ma=5, dhu=9, ra=2...
        # गोपीभाग्य
        # Go (3)
        # Pi (1)
        # Bha (4)
        # Gya (Gy = Ga + Ya). Ga ignored (conjunct), Ya counts (1).
        # Expected: 3141
        
        text2 = "गोपीभाग्य" 
        val2 = calc.calculate(text2)
        print(f"🧮 Calculation Test: '{text2}' (Gopibhagya)")
        print(f"   Expected: 3141")
        print(f"   Actual:   {val2}")
        
        if val2 == 3141:
             print("✅ Pi Fragment verified.")
        else:
             print(f"❌ Pi Fragment failed. Got {val2}.")
             return False

    except Exception as e:
        print(f"❌ Calculation verification error: {e}")
        return False

    print("\n✨ Rite of Sanskrit Integration Complete. The System is Whole.")
    return True

if __name__ == "__main__":
    if verify_integration():
        sys.exit(0)
    else:
        sys.exit(1)
