import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

def verify_dynamis_logic():
    print("Beginning the Rite of Dynamis...")
    
    try:
        from pillars.time_mechanics.services.tzolkin_service import TzolkinService
        service = TzolkinService()
        
        # Test 1: Conrune Logic
        # 1 -> 2, 2 -> 1, 0 -> 0
        input_ditrune = "012012"
        expected = "021021"
        result = service.get_conrune(input_ditrune)
        
        print(f"1. Testing Conrune Inversion '{input_ditrune}' -> '{result}'")
        if result == expected:
             print("   [SUCCESS] Conrune Inversion confirmed.")
        else:
             print(f"   [FAILURE] Expected {expected}, got {result}")
             return False

        # Test 2: Trigram Splitting
        input_ditrune = "111222"
        upper, lower = service.get_trigrams(input_ditrune)
        print(f"2. Testing Trigram Split '{input_ditrune}' -> Upper: {upper}, Lower: {lower}")
        
        if upper == "111" and lower == "222":
            print("   [SUCCESS] Trigrams split correctly.")
        else:
            print(f"   [FAILURE] Split failed.")
            return False

    except Exception as e:
        print(f"   [CRITICAL FAILURE] {e}")
        import traceback
        traceback.print_exc()
        return False
        
    print("The Rite of Dynamis is passed.")
    return True

if __name__ == "__main__":
    success = verify_dynamis_logic()
    sys.exit(0 if success else 1)
