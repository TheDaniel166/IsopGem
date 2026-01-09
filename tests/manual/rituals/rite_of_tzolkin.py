import sys
import os
from datetime import date, timedelta

# Add src to path
sys.path.append(os.path.abspath("src"))

def verify_tzolkin_logic():
    print("Beginning the Rite of Tzolkin...")
    
    try:
        from pillars.time_mechanics.services.tzolkin_service import TzolkinService
        service = TzolkinService()
        
        # Test 1: Epoch (Jan 12, 2020) -> Kin 1, Cycle 1
        epoch = date(2020, 1, 12)
        tz_epoch = service.from_gregorian(epoch)
        
        print(f"1. Testing Epoch: {epoch}")
        print(f"   Result: {tz_epoch}")
        
        if tz_epoch.kin == 1 and tz_epoch.cycle == 1:
            print("   [SUCCESS] Kin 1, Cycle 1 confirmed.")
        else:
            print(f"   [FAILURE] Expected Kin 1, Cycle 1. Got Kin {tz_epoch.kin}, Cycle {tz_epoch.cycle}")
            return False

        # Test 2: Epoch + 1 Day -> Kin 2
        d2 = epoch + timedelta(days=1)
        tz_d2 = service.from_gregorian(d2)
        print(f"2. Testing Epoch + 1: {d2}")
        if tz_d2.kin == 2:
            print(f"   [SUCCESS] Kin 2 confirmed. ({tz_d2.sign_name})")
        else:
            print(f"   [FAILURE] Expected Kin 2. Got {tz_d2.kin}")
            return False

        # Test 3: Epoch + 260 Days -> Kin 1, Cycle 2
        d260 = epoch + timedelta(days=260)
        tz_d260 = service.from_gregorian(d260)
        print(f"3. Testing Cycle Boundary (Epoch + 260): {d260}")
        if tz_d260.kin == 1 and tz_d260.cycle == 2:
             print("   [SUCCESS] Kin 1, Cycle 2 confirmed.")
        else:
             print(f"   [FAILURE] Expected Kin 1, Cycle 2. Got Kin {tz_d260.kin}, Cycle {tz_d260.cycle}")
             return False

        # Test 4: Ditrune Lookup (Checking valid non-zero values)
        print(f"4. Checking Ditrune Data for Kin 1...")
        if tz_epoch.ditrune_decimal > 0:
            print(f"   [SUCCESS] Ditrune found: {tz_epoch.ditrune_decimal} ({tz_epoch.ditrune_ternary})")
        else:
             print("   [FAILURE] Ditrune seems to be 0 or missing.")
             return False
             
        # Test 5: Negative Date (Before Epoch)
        # Jan 11, 2020 should be Kin 260, Cycle 0
        d_neg = epoch - timedelta(days=1)
        tz_neg = service.from_gregorian(d_neg)
        print(f"5. Testing Pre-Epoch (Jan 11, 2020): {d_neg}")
        print(f"   Result: {tz_neg}")
        if tz_neg.kin == 260 and tz_neg.cycle == 0:
            print("   [SUCCESS] Kin 260, Cycle 0 confirmed.")
        else:
             print(f"   [FAILURE] Expected Kin 260, Cycle 0. Got Kin {tz_neg.kin}, Cycle {tz_neg.cycle}")
             return False

    except Exception as e:
        print(f"   [CRITICAL FAILURE] Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    print("The Rite of Tzolkin is passed.")
    return True

if __name__ == "__main__":
    success = verify_tzolkin_logic()
    sys.exit(0 if success else 1)
