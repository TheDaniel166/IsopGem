
import csv
import ast

# 1. Load Coordinates from wall_seeds_dna.csv
dna_coords = []
with open('Docs/adyton_walls/wall_seeds_dna.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader) # skip header
    for row in reader:
        if row and len(row) >= 11:
            # coord is in the last column
            coord_str = row[10]
            try:
                coord = ast.literal_eval(coord_str)
                dna_coords.append(coord)
            except:
                print(f"Error parsing coord: {coord_str}")

# 2. Analyze Topology
distribution = {} # (r, c) -> count
total_seeds = len(dna_coords)

for coord in dna_coords:
    if coord in distribution:
        distribution[coord] += 1
    else:
        distribution[coord] = 1

active_columns = len(distribution)
total_columns = 8 * 13
empty_columns = total_columns - active_columns
active_coords = list(distribution.keys())
common_coords = [c for c in active_coords if distribution[c] > 1]
unique_coords = [c for c in active_coords if distribution[c] == 1]

print(f"Total Grid Size: {total_columns}")
print(f"Total Seeds from DNA File: {total_seeds}")
print(f"Active Columns: {active_columns}")
print(f"Empty Columns (Void): {empty_columns}")
print(f"Common Active Columns: {len(common_coords)}")
print(f"Unique Active Columns: {len(unique_coords)}")

print("\n--- Distribution Verification ---")
print(f"41 Empty: {empty_columns == 41}")
print(f"41 Common: {len(common_coords) == 41}")
print(f"22 Unique: {len(unique_coords) == 22}")

if empty_columns == 41 and len(unique_coords) == 22:
    print("\nGOLDEN RATIO FOUND: The DNA File coordinates produce the Perfect 41-41-22 Cosmology.")
elif empty_columns == 50:
    print("\nResult Matches Constellation File (50 Empty).")
else:
    print(f"\nResult is a new topology: {empty_columns} Empty / {len(unique_coords)} Unique.")
