import sys
import os
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.abspath("src"))

from pillars.astrology.models import AstrologyEvent, ChartRequest, GeoLocation
from pillars.astrology.services import OpenAstroService

def debug_julian_day():
    print("Initializing OpenAstroService...")
    try:
        service = OpenAstroService()
    except Exception as e:
        print(f"Failed to init service: {e}")
        return

    # Create a dummy event
    loc = GeoLocation("Test Loc", 40.7, -74.0)
    event = AstrologyEvent("Test Event", datetime.now(), loc)
    request = ChartRequest(primary_event=event)

    print("Generating Chart...")
    try:
        result = service.generate_chart(request)
        print(f"Chart Generated.")
        print(f"Julian Day in Result: {result.julian_day}")
        
        if result.julian_day is not None and isinstance(result.julian_day, float):
             print("SUCCESS: Julian Day is present and valid.")
        else:
             print("FAIL: Julian Day is None or invalid.")
             
        # Also check fixed stars directly if possible (though they are calculated in UI usually)
        # But OpenAstro might return them if configured?
        fixed_stars = getattr(result, 'fixed_stars', [])
        print(f"Fixed Stars in Result: {len(fixed_stars) if fixed_stars else 'None'}")

    except Exception as e:
        print(f"Error during generation: {e}")

if __name__ == "__main__":
    debug_julian_day()
