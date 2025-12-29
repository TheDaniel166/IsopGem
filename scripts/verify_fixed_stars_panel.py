import sys
import os
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.abspath("src"))

from PyQt6.QtWidgets import QApplication
from pillars.astrology.ui.advanced_analysis_panel import AdvancedAnalysisPanel
from pillars.astrology.models.chart_models import PlanetPosition, ChartResult
from pillars.astrology.services.fixed_stars_service import FixedStarsService

def verify_logic():
    app = QApplication(sys.argv)
    
    # mimic data
    planets = [
        PlanetPosition(name="Sun", degree=69.5), # ~9 Gemini -> Near Aldebaran (68.5/69)? No Aldebaran is ~9 Gemini. Aldebaran is ~9 deg Gemini -> 69.
        # Spica is ~24 Libra -> 204.
        PlanetPosition(name="Mars", degree=204.0) 
    ]
    
    # Julian Day for J2000 roughly 2451545.0
    jd = 2451545.0
    
    panel = AdvancedAnalysisPanel()
    
    print("Injecting data...")
    # Using the new signature
    panel.set_data(planets=planets, houses=[], julian_day=jd)
    
    # Check internal fixed stars
    print(f"Fixed Stars Count: {len(panel._fixed_stars)}")
    if len(panel._fixed_stars) == 0:
        print("FAIL: Internal fixed stars list is empty.")
        return
        
    # Check table population
    row_count = panel.fixed_stars_table.rowCount()
    print(f"Table Rows: {row_count}")
    
    # Find Aldebaran row
    aldebaran_found = False
    conjunction_found = False
    
    for row in range(row_count):
        name_item = panel.fixed_stars_table.item(row, 0)
        conj_item = panel.fixed_stars_table.item(row, 2)
        star_name = name_item.text()
        
        if "Aldebaran" in star_name:
            aldebaran_found = True
            print(f"Aldebaran Found at row {row}")
            if conj_item and "☉" in conj_item.text() and "☌" in conj_item.text():
                conjunction_found = True
                print(f"Sun Conjunction Found with correct glyphs: {conj_item.text()}")
            break
            
    if aldebaran_found:
        print("SUCCESS: Fixed Stars populated.")
    else:
        print("FAIL: Aldebaran not found in table.")
        
    if conjunction_found:
        print("SUCCESS: Conjunction detected with glyphs.")
    else:
        print("FAIL: Conjunction logic failed or glyphs missing.")

if __name__ == "__main__":
    verify_logic()
