
import os
import json
import csv
import collections

def get_constellation_metrics():
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__)) # scripts/
    project_root = os.path.dirname(base_dir) # projects/isopgem/
    
    lattice_path = os.path.join(project_root, "src", "pillars", "mods", "data", "planetary_lattices.json")
    docs_dir = os.path.join(project_root, "Docs", "adyton_walls")
    
    # Load Lattices
    with open(lattice_path, 'r') as f:
        lattices = json.load(f)
        
    # Planets mapping
    # Maps Key in JSON/CSV logic to Filename
    # JSON Keys: Sun, Mercury, Venus, Earth(Maybe?), Mars, Jupiter, Saturn
    # Let's assume the JSON keys match standard names.
    # Note: JSON start with "Sun".
    
    # Order for Output
    planets = ["Sun", "Mercury", "Moon", "Venus", "Jupiter", "Mars", "Saturn"]
    
    # File Map (based on wall_designer.py)
    # Note: wall_designer uses "Moon": "luna_wall.csv"
    fname_map = {
        "Sun": "sun_wall.csv",
        "Mercury": "mercury_wall.csv",
        "Moon": "luna_wall.csv",
        "Venus": "venus_wall.csv",
        "Jupiter": "jupiter_wall.csv",
        "Mars": "mars_wall.csv",
        "Saturn": "saturn_wall.csv"
    }

    # Lattice Keys might differ. "Moon" might be "Luna" or "Earth"?
    # Let's check keys in lattices variable.
    # We saw "Sun" in the file.
    # If "Moon" key is missing, we might need to check "Earth" or "Luna".
    # I'll add a check.

    results = []
    
    for p_name in planets:
        # Resolve Lattice Key
        l_key = p_name
        if p_name == "Moon" and "Moon" not in lattices:
            if "Luna" in lattices: l_key = "Luna"
            elif "Earth" in lattices: l_key = "Earth" # Often Moon/Earth are swapped in this system
            
        print(f"Processing {p_name} (Lattice: {l_key})...")
        
        # Load Values
        csv_file = fname_map[p_name]
        csv_path = os.path.join(docs_dir, csv_file)
        
        values = []
        if os.path.exists(csv_path):
             with open(csv_path, 'r') as f:
                 reader = csv.reader(f)
                 for row in reader:
                     values.append([int(x) for x in row if x.strip()])
        else:
            print(f"  ERROR: Missing csv {csv_path}")
            continue

        # Load Grid
        grid = lattices.get(l_key)
        if not grid:
            print(f"  ERROR: Missing lattice for {l_key}")
            continue
            
        # Group Data
        groups = collections.defaultdict(list)
        
        rows = len(grid)
        cols = len(grid[0])
        
        for r in range(rows):
            for c in range(cols):
                if r < len(values) and c < len(values[r]):
                    gid = grid[r][c]
                    val = values[r][c]
                    if gid >= 0: # -1 is dead zone
                        groups[gid].append(val)
                        
        # Calc Metrics
        # Ensure we have 0-12
        for gid in range(13):
            if gid in groups:
                vals = groups[gid]
                total = sum(vals)
                count = len(vals)
                
                results.append({
                    "Wall": p_name,
                    "GroupID": gid,
                    "Sum": total,
                    "Count": count
                })
                
    # Output
    out_path = os.path.join(docs_dir, "constellation_metrics.csv")
    with open(out_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Wall", "GroupID", "Sum", "Count"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Saved to {out_path}")

if __name__ == "__main__":
    get_constellation_metrics()
