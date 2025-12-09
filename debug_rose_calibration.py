
import sys
from datetime import datetime, timezone

def verify_calibration():
    # J2000 Epoch
    J2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    # 1. Test Math
    # Earth at J2000 should be at 100.46 deg
    # In my logic: (L_EARTH_J2000 + days * deg_per_day_e) % 360.0
    # days = 0
    # result = 100.46. Correct.
    
    # Check 1 year later (approx)
    dt_future = datetime(2001, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    delta = dt_future - J2000
    days = delta.total_seconds() / 86400.0 # 366.0 days (Leap year 2000)
    
    deg_per_day_e = 360.0 / 365.256
    pos_e = (100.46 + days * deg_per_day_e) % 360.0
    print(f"Earth Pos at 2001-01-01: {pos_e:.2f} deg")
    
    # Should be close to 100.46 + slightly more than 360 (since 366 > 365.256)
    expected_drift = (366 - 365.256) * deg_per_day_e
    expected_pos = (100.46 + expected_drift) % 360
    print(f"Expected Pos: {expected_pos:.2f} deg")
    
    # 2. Test Import / Class Structure (Mocking Qt)
    try:
        # We can't fully instantiate QGraphicsScene without QApplication
        # but we can try to import
        from pillars.astrology.ui.venus_rose_window import RoseScene, VenusRoseWindow
        print("Import successful.")
        return True
    except ImportError:
        print("Import failed.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    import os
    sys.path.append(os.path.join(os.getcwd(), "src"))
    verify_calibration()
