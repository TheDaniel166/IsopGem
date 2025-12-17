
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.abspath("src"))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSize
from pillars.astrology.ui.chart_canvas import ChartCanvas
from pillars.astrology.models.chart_models import PlanetPosition, HousePosition

def render_preview():
    app = QApplication(sys.argv)
    
    canvas = ChartCanvas()
    canvas.resize(800, 800)
    
    # Dummy Data
    planets = [
        PlanetPosition(name="Sun", degree=15.5),     # Aries 15
        PlanetPosition(name="Moon", degree=140.2),  # Leo 20
        PlanetPosition(name="Venus", degree=45.0),   # Taurus 15
        PlanetPosition(name="Mars", degree=200.0),   # Libra 20
        PlanetPosition(name="Jupiter", degree=300.0), # Aquarius 0
        PlanetPosition(name="Saturn", degree=350.0), # Pisces 20
    ]
    
    houses = []
    start_deg = 0.0
    for i in range(1, 13):
        houses.append(HousePosition(number=i, degree=start_deg))
        start_deg += 30.0
        
    canvas.set_data(planets, houses)
    
    # Simulate Hover on Sun (Index 0)
    # We need to force layout/paint once to populate hitboxes? 
    # Actually, we can just set the internal state directly for testing the paint logic.
    if canvas.planets:
        canvas._hovered_planet = canvas.planets[0] # Sun
    
    # Grab pixmap
    pixmap = canvas.grab()
    
    output_path = os.path.abspath("chart_preview.png")
    pixmap.save(output_path)
    print(f"Saved preview to {output_path}")

if __name__ == "__main__":
    render_preview()
