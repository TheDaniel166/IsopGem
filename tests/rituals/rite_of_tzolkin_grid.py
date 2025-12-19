import sys
import os
from datetime import date, timedelta

# Add src to path
sys.path.append(os.path.abspath("src"))

def verify_grid_logic():
    print("Beginning the Rite of Tzolkin Grid...")
    
    try:
        from pillars.time_mechanics.services.tzolkin_service import TzolkinService
        service = TzolkinService()
        
        # 1. Verify Grid Dimensions
        rows = len(service._decimal_grid[0]) # 13
        cols = len(service._decimal_grid)    # 20
        # Wait, service._decimal_grid is [Sign][Tone] (20 x 13)
        # UI is [Tone][Sign] (13 x 20)
        
        print(f"1. Service Grid Logic: {cols} Signs x {rows} Tones")
        if rows != 13 or cols != 20:
             print(f"   [FAILURE] Grid dimensions mismatch. Got {cols} x {rows}")
             return False
        else:
             print("   [SUCCESS] Dimensions confirmed.")

        # 2. Simulate Navigation Logic
        print("2. Simulating Click Navigation...")
        current_date = date(2020, 1, 12) # Kin 1
        
        # Target: Row 12 (Tone 13), Col 19 (Sign 20) -> Kin 260
        target_row = 12
        target_col = 19
        
        target_tone = target_row + 1
        target_sign = target_col + 1
        
        # Calculate Kin for (Tone 13, Sign 20)
        # We know Kin 260 corresponds to this.
        # Let's verify our math:
        # Kin K where K % 13 == 0 and K % 20 == 0 -> K = 260.
        
        # Simulate map logic
        kin_map = {}
        for k in range(1, 261):
            t = (k - 1) % 13 + 1
            s = (k - 1) % 20 + 1
            kin_map[(t, s)] = k
            
        target_kin = kin_map.get((target_tone, target_sign))
        print(f"   Target: Tone {target_tone}, Sign {target_sign} -> Kin {target_kin}")
        
        if target_kin != 260:
             print(f"   [FAILURE] Expected Kin 260, got {target_kin}")
             return False

        # Calculate new date
        current_kin = 1
        diff = target_kin - current_kin # 259
        new_date = current_date + timedelta(days=diff)
        
        expected_date = date(2020, 9, 27) # Jan 12 + 259 days
        # Jan 12 + 260 days = Cycle 2, Kin 1 = Sep 28
        # So Kin 260 should be Sep 27.
        
        print(f"   Computed Date: {new_date}")
        if new_date == expected_date:
            print("   [SUCCESS] Navigation Math confirmed.")
        else:
            print(f"   [FAILURE] Date mismatch. Expected {expected_date}, got {new_date}")
            return False

        # 3. Simulate "Prev Cycle" Click
        # If we are at Kin 1, clicking Kin 260 should theoretically go to yesterday?
        # NO. The logic I implemented is `current_date + diff`.
        # Diff = 260 - 1 = 259.
        # So clicking Kin 260 always jumps to Kin 260 of the *current cycle*.
        # It does NOT go to "closest" Kin. It goes to "Kin of Current Cycle".
        # This is acceptable behavior for a calendar grid.
        
        print("   [NOTE] Navigation stays within current cycle boundary logic.")

    except Exception as e:
        print(f"   [CRITICAL FAILURE] {e}")
        import traceback
        traceback.print_exc()
        return False
        
    print("The Rite of the Grid is passed.")
    return True

if __name__ == "__main__":
    success = verify_grid_logic()
    sys.exit(0 if success else 1)
