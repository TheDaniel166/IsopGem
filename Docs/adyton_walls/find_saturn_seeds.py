
import csv

# Saturn Wall Data from saturn_wall.csv
saturn_wall_grid = [
    [725,721,720,722,727,726,364,337,336,338,334,333,335],
    [717,719,706,705,707,703,377,324,326,331,330,332,346],
    [718,713,711,712,716,714,325,349,344,342,343,347,345],
    [723,724,710,708,709,704,351,329,327,328,341,339,340],
    [671,669,670,656,654,655,702,352,356,354,355,368,366],
    [663,664,659,657,658,662,650,375,376,371,369,370,374],
    [665,652,651,653,649,648,715,353,358,357,359,373,372],
    [667,666,668,673,672,674,728,363,365,361,360,362,367]
]

# Seeds from walls_constellations_complete.csv (lines 80-92)
# Since the 'Val1' column in walls_constellations_complete.csv represents the SEED value for that constellation
# We can just extract Val1 for each of the 13 Saturn constellations.

saturn_seeds_values = [
    725, # Constellation 0
    720, # Constellation 1
    722, # Constellation 2
    726, # Constellation 3
    337, # Constellation 4
    335, # Constellation 5
    724, # Constellation 6
    656, # Constellation 7
    649, # Constellation 8
    655, # Constellation 9
    355, # Constellation 10
    368, # Constellation 11
    344  # Constellation 12
]

print(f"Saturn Seeds (Values): {saturn_seeds_values}")
print(f"Count: {len(saturn_seeds_values)}")

print("\n--- Coordinates (Row, Col) ---")
found_count = 0
for seed_val in saturn_seeds_values:
    found = False
    for r in range(8):
        for c in range(13):
            if saturn_wall_grid[r][c] == seed_val:
                print(f"Seed {seed_val}: ({r}, {c})")
                found = True
                found_count += 1
                break
        if found: break
    if not found:
        print(f"WARNING: Seed {seed_val} not found in grid!")

print(f"\nTotal Found: {found_count}")
