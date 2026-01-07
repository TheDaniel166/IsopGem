
import csv
import ast

# 1. Load Data from walls_constellations_complete.csv
# Structure: Wall,Constellation_ID,Val1 (Seed Value), ...
constellation_seeds = {} # (Wall, Constellation_ID) -> SeedValue
with open('Docs/adyton_walls/walls_constellations_complete.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader) # skip header
    for row in reader:
        if row:
            wall = row[0]
            cid = int(row[1])
            seed_val = int(row[2]) # Constellation File says Val1 is the Seed Value
            constellation_seeds[(wall, cid)] = seed_val

# 2. Load Data from wall_seeds_dna.csv
# Structure: Wall,Group (CID), ..., Seed_Coord (string tuple)
dna_data = []
with open('Docs/adyton_walls/wall_seeds_dna.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader) # skip header
    for row in reader:
        if row and len(row) >= 11:
            wall = row[0]
            cid = int(row[1])
            coord_str = row[10] # e.g. "(1, 0)"
            try:
                coord = ast.literal_eval(coord_str)
                dna_data.append({'wall': wall, 'cid': cid, 'coord': coord})
            except:
                print(f"Error parsing coord: {coord_str}")

# 3. Load Wall Grids for Value Lookup
def load_wall_grid(filename):
    grid = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                grid.append([int(x) for x in row])
    return grid

wall_files = {
    "Sun": "sun_wall.csv",
    "Mercury": "mercury_wall.csv",
    "Venus": "venus_wall.csv",
    "Moon": "luna_wall.csv",
    "Mars": "mars_wall.csv",
    "Jupiter": "jupiter_wall.csv",
    "Saturn": "saturn_wall.csv"
}

grids = {k: load_wall_grid(f"Docs/adyton_walls/{v}") for k,v in wall_files.items()}

# 4. Verify
mismatches = 0
total_checked = 0

print("--- Verification Report ---")

for item in dna_data:
    wall = item['wall']
    cid = item['cid']
    coord = item['coord']
    r, c = coord
    
    # Get value from grid at coord
    try:
        grid_val = grids[wall][r][c]
    except IndexError:
        print(f"ERROR: Coord {coord} out of bounds for {wall}")
        continue
        
    # Get expected value from constellation file
    if (wall, cid) not in constellation_seeds:
        print(f"WARNING: No constellation entry for {wall} Group {cid}")
        continue
        
    expected_val = constellation_seeds[(wall, cid)]
    
    total_checked += 1
    
    if grid_val != expected_val:
        print(f"MISMATCH: {wall} Group {cid}")
        print(f"  DNA Coord: {coord} -> Grid Value: {grid_val}")
        print(f"  Constellation File Seed: {expected_val}")
        mismatches += 1

print(f"\nTotal Checked: {total_checked}")
if mismatches == 0:
    print("SUCCESS: 'wall_seeds_dna.csv' coordinates perfectly match 'walls_constellations_complete.csv' seed values.")
else:
    print(f"FAILURE: Found {mismatches} mismatches.")
