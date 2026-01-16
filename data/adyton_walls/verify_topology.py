
# Corrected Seed Coordinates derived from walls_constellations_complete.csv
# Format: (List of tuples (row, col))

# Note: I need to extract ALL planetary seeds from the constellation file to be 100% sure.
# The previous script parsed ASCII which was wrong.
# This script will take the Seed Values from the constellation file and map them to the Wall CSVs.

import csv

def load_wall_grid(filename):
    grid = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                grid.append([int(x) for x in row])
    return grid

walls = {
    "Sun": "sun_wall.csv",
    "Mercury": "mercury_wall.csv",
    "Venus": "venus_wall.csv",
    "Moon": "luna_wall.csv",
    "Mars": "mars_wall.csv",
    "Jupiter": "jupiter_wall.csv",
    "Saturn": "saturn_wall.csv"
}

# The seed value is the first value (Val1) in walls_constellations_complete.csv
# We need to map which rows belong to which wall.
# Based on file inspection:
# Sun: Rows 2-14 (13 seeds)
# Mercury: Rows 15-27 (13 seeds)
# Venus: Rows 28-40 (13 seeds)
# Moon: Rows 41-53 (13 seeds)
# Mars: Rows 54-66 (13 seeds)
# Jupiter: Rows 67-79 (13 seeds)
# Saturn: Rows 80-92 (13 seeds)

planet_ranges = {
    "Sun": (2, 14),
    "Mercury": (15, 27),
    "Venus": (28, 40),
    "Moon": (41, 53),
    "Mars": (54, 66),
    "Jupiter": (67, 79),
    "Saturn": (80, 92)
}

# Load seed VALUES from constellation file
seed_values = {p: [] for p in walls.keys()}
with open('Docs/adyton_walls/walls_constellations_complete.csv', 'r') as f:
    # Skip header
    lines = f.readlines()
    for i, line in enumerate(lines):
        if i == 0: continue
        parts = line.split(',')
        if not parts: continue
        wall_name = parts[0]
        seed_val = int(parts[2]) # Val1 is at index 2
        
        # Verify wall name matches range
        if wall_name in seed_values:
            seed_values[wall_name].append(seed_val)

# Locate coordinates
distribution = {} # (r, c) -> count
total_seeds = 0

for name, filename in walls.items():
    grid = load_wall_grid(f"Docs/adyton_walls/{filename}")
    values = seed_values[name]
    
    # print(f"Processing {name}: {len(values)} seeds")
    total_seeds += len(values)
    
    for val in values:
        found = False
        for r in range(8):
            for c in range(13):
                if grid[r][c] == val:
                    coord = (r, c)
                    if coord in distribution:
                        distribution[coord] += 1
                    else:
                        distribution[coord] = 1
                    found = True
                    break
            if found: break
        if not found:
            print(f"ERROR: Seed {val} for {name} not found in wall grid!")

active_columns = len(distribution)
total_columns = 8 * 13
empty_columns = total_columns - active_columns

active_coords = list(distribution.keys())
common_coords = [c for c in active_coords if distribution[c] > 1]
unique_coords = [c for c in active_coords if distribution[c] == 1]

print(f"Total Grid Size: {total_columns}")
print(f"Total Seeds Found: {total_seeds}")
print(f"Active Columns: {active_columns}")
print(f"Empty Columns (Void): {empty_columns}")
print(f"Common Active Columns: {len(common_coords)}")
print(f"Unique Active Columns: {len(unique_coords)}")

print("\n--- Distribution Verification ---")
print(f"41 Empty: {empty_columns == 41}")
print(f"41 Common: {len(common_coords) == 41}")
print(f"22 Unique: {len(unique_coords) == 22}")

if len(unique_coords) == 22:
    print("\nSUCCESS: The 41-41-22 Topology is CONFIRMED using the data files.")
else:
    print(f"\nDiscrepancy: Expected 22 Unique, found {len(unique_coords)}")
