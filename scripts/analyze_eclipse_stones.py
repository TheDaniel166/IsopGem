
import sys
import os
from datetime import datetime, timedelta, timezone
import math

# Direct dependency on openastro2, avoiding app architecture
try:
    from openastro2.openastro2 import openAstro
except ImportError:
    print("Error: openastro2 not installed. Cannot run.")
    sys.exit(1)

# Constants
SAROS_HOLES = 223
AUBREY_HOLES = 56
SYNODIC_MONTH = 29.53059
J2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

def to_zodiacal_string(lon):
    signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqr", "Pis"]
    idx = int(lon / 30)
    deg = lon % 30
    d_int = int(deg)
    m_int = int((deg - d_int) * 60)
    return f"{d_int}° {signs[idx]} {m_int:02d}'"

def get_stone_idx(lon):
    return int((lon / 360.0) * AUBREY_HOLES) + 1

def analyze():
    start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2124, 1, 1, tzinfo=timezone.utc) # 100 years
    
    current = start_date
    events = []
    
    print(f"Scanning from {start_date.date()} to {end_date.date()}...", flush=True)
    
    step = timedelta(days=1)
    last_event_date = None
    
    while current < end_date:
        if current.day == 1 and current.month == 1:
            print(f"Scanning {current.year}...", flush=True)
            
        try:
            # Create minimal event
            # Must manually decompose datetime as per AstrologyEvent.to_openastro_kwargs
            oa_event = openAstro.event(
                year=current.year,
                month=current.month,
                day=current.day,
                hour=current.hour,
                minute=current.minute,
                second=current.second,
                timezone=0.0,
                location="Greenwich",
                countrycode="",
                geolat=51.48,
                geolon=0.0,
                altitude=0,
                name="Scan"
            )
            
            # Generate Chart
            # Default settings
            chart = openAstro(oa_event, type="Radix", settings={
                "astrocfg": {
                    "language": "en",
                    "houses_system": "P",
                    "zodiactype": "tropical",
                    "postype": "geo",
                    "planet_in_one_house": 0
                }
            })
            chart.calcAstro()
            
            # Extract
            names = getattr(chart, "planets_name", [])
            degrees = getattr(chart, "planets_degree_ut", [])
            
            def get_deg(target):
                for i, name in enumerate(names):
                    if name.lower() == target.lower():
                        return float(degrees[i])
                return 0.0

            sun = get_deg("Sun")
            moon = get_deg("Moon")
            node = get_deg("North Node") 
            # Note: OA might name it differently?
            # Let's hope "North Node" works. If not, try "True Node"
            if node == 0.0: node = get_deg("True Node")
            if node == 0.0: node = get_deg("Mean Node")
            
            if current < start_date + timedelta(days=5):
                print(f"DEBUG: {current.date()} Sun={sun:.2f} Moon={moon:.2f} Node={node:.2f}")

            dist_sun_moon = min(abs(sun - moon), 360 - abs(sun - moon))
            is_new = dist_sun_moon < 10
            is_full = abs(dist_sun_moon - 180) < 10
            
            if not (is_new or is_full):
                current += step
                continue
                
            dist_sun_node = min(abs(sun - node), 360 - abs(sun - node))
            south_node = (node + 180) % 360
            dist_sun_snode = min(abs(sun - south_node), 360 - abs(sun - south_node))
            min_node_dist = min(dist_sun_node, dist_sun_snode)
            
            if min_node_dist < 18:
                evt_type = None
                if is_new and dist_sun_moon < 2:
                    evt_type = "SOLAR"
                elif is_full and abs(dist_sun_moon - 180) < 2:
                    evt_type = "LUNAR"
                    
                if evt_type:
                    date_str = current.strftime("%Y-%m-%d")
                    if last_event_date == date_str:
                         current += step
                         continue
                    
                    last_event_date = date_str
                    
                    sun_stone = get_stone_idx(sun)
                    node_stone = get_stone_idx(node if dist_sun_node < dist_sun_snode else south_node)
                    
                    delta = current - J2000
                    saros_days = delta.total_seconds() / 86400.0
                    saros_idx = int((saros_days / SYNODIC_MONTH) % SAROS_HOLES) + 1
                    
                    node_name = "North" if dist_sun_node < dist_sun_snode else "South"
                    
                    events.append({
                        "date": date_str,
                        "type": evt_type,
                        "sun_stone": sun_stone,
                        "node_stone": node_stone,
                        "node_name": node_name,
                        "saros_stone": saros_idx,
                        "zodiac": to_zodiacal_string(sun)
                    })
                    
        except Exception as e:
            print(f"Error: {e}")
            pass
            
        current += step

    output_path = "eclipse_patterns.md"
    with open(output_path, "w") as f:
        f.write("# Eclipse Stone Patterns (2024-2124)\n\n")
        f.write("| Date | Type | Sun Stone | Node Stone | Node | Saros Stone | Zodiac |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for e in events:
            f.write(f"| {e['date']} | {e['type']} | {e['sun_stone']} | {e['node_stone']} | {e['node_name']} | {e['saros_stone']} | {e['zodiac']} |\n")
            
    print(f"Done. Found {len(events)} events. Report written to {output_path}")

if __name__ == "__main__":
    analyze()
