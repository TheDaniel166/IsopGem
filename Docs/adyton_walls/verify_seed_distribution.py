
def parse_grid(grid_str):
    """Parses an 8x13 ASCII grid into a list of (row, col) tuples."""
    seeds = []
    rows = grid_str.strip().split('\n')
    for r, row_text in enumerate(rows):
        # Remove brackets or pipe characters if present, just look for *
        # The maps in the Atlas use . and * separated by spaces
        # e.g. " .  .  *  . "
        # We need to maintain column index.
        # Removing spaces and finding index might be tricky if spacing varies.
        # Assuming fixed width or simply stripping spaces and checking chars?
        # The Atlas format is ".  .  *" etc. let's split by regex or fixed width.
        # Actually, split by whitespace seems safest if they act as tokens.
        tokens = row_text.split()
        for c, token in enumerate(tokens):
            if token == '*':
                seeds.append((r, c))
    return seeds

# ASCII Maps from The_Atlas_of_Seeds.md
sun_map = """
 .  .  .  .  .  .  .  *  .  .  *  .  . 
 *  .  *  .  *  .  .  .  .  .  .  .  . 
 .  .  .  .  .  .  .  .  .  .  *  .  . 
 .  .  .  .  .  .  *  .  .  .  .  .  . 
 .  .  .  .  .  .  .  .  .  .  .  .  . 
 *  .  *  .  .  .  .  .  .  *  .  *  . 
 .  .  .  .  .  *  .  .  *  .  .  .  . 
 .  .  .  .  .  .  .  .  .  .  .  .  . 
"""

mercury_map = """
 .  .  .  .  .  *  .  .  .  .  .  .  * 
 .  *  .  .  .  .  .  .  .  .  *  .  . 
 .  .  .  .  .  .  .  .  .  .  .  .  . 
 .  .  .  *  .  .  *  .  *  .  .  .  . 
 .  .  .  .  .  .  .  .  .  .  .  .  . 
 *  .  *  .  *  .  .  *  .  .  .  .  . 
 .  .  .  .  .  .  .  .  .  *  .  .  * 
 .  .  .  .  .  .  .  .  .  .  .  .  . 
"""

venus_map = """
 .  .  .  .  .  .  *  .  .  .  .  .  . 
 .  .  *  .  .  .  .  .  .  .  *  .  . 
 .  *  .  .  .  .  *  .  .  *  .  .  . 
 .  .  .  .  .  .  .  .  .  .  .  .  . 
 .  .  .  .  .  *  .  .  .  .  .  .  . 
 .  .  *  .  .  .  .  .  .  .  *  .  * 
 *  .  .  .  .  *  .  .  *  .  .  .  . 
 .  .  .  .  .  .  .  .  .  .  .  .  . 
"""

moon_map = """
 .  .  .  .  .  .  .  .  .  .  .  *  . 
 .  *  .  .  .  .  .  *  .  .  .  .  . 
 .  .  .  *  *  .  .  .  .  .  .  *  . 
 .  *  .  .  .  .  .  *  .  .  .  .  . 
 .  .  .  .  .  .  .  .  .  .  .  .  . 
 .  .  .  .  *  .  .  *  .  .  .  .  . 
 .  .  .  .  .  .  .  .  .  *  .  *  . 
 .  *  .  .  .  .  .  .  .  .  .  .  . 
"""

mars_map = """
 *  .  .  .  .  .  .  .  .  *  .  .  . 
 .  .  .  .  .  *  .  .  .  .  .  .  * 
 .  .  *  .  .  .  .  .  .  .  .  .  . 
 .  .  .  .  .  *  .  .  *  .  .  .  . 
 .  .  .  *  .  .  .  .  .  .  .  .  * 
 .  *  .  .  .  .  .  .  .  .  .  .  . 
 .  .  .  .  .  *  .  *  .  *  .  .  . 
 .  .  .  .  .  .  .  .  .  .  .  .  . 
"""

jupiter_map = """
 .  .  .  *  .  .  .  .  .  .  *  .  . 
 *  .  .  .  .  .  .  *  .  .  *  .  . 
 .  .  .  .  .  *  .  .  .  .  .  .  . 
 .  .  *  .  .  .  .  .  .  .  .  .  . 
 .  .  .  .  .  .  .  *  .  .  .  .  . 
 .  .  .  *  .  .  .  .  .  .  .  *  . 
 .  *  .  .  .  *  .  .  .  .  .  .  . 
 .  .  .  .  .  .  .  .  .  *  .  .  . 
"""

saturn_map = """
 .  .  .  .  .  .  .  .  .  *  .  .  . 
 *  .  .  .  *  .  *  .  .  .  .  .  . 
 .  .  *  .  .  .  .  .  .  .  .  .  * 
 .  .  .  .  .  .  .  .  .  *  .  .  . 
 .  .  .  .  .  .  .  *  .  .  .  .  . 
 .  .  .  *  .  .  .  .  .  *  .  .  . 
 .  .  .  .  *  .  .  .  .  .  .  *  . 
 .  .  .  .  .  .  .  .  .  .  .  .  . 
"""

planets = {
    "Sun": sun_map,
    "Mercury": mercury_map,
    "Venus": venus_map,
    "Moon": moon_map,
    "Mars": mars_map,
    "Jupiter": jupiter_map,
    "Saturn": saturn_map
}

distribution = {} # (r, c) -> count
total_seeds = 0

for name, grid in planets.items():
    seeds = parse_grid(grid)
    # print(f"{name}: {len(seeds)} seeds")
    if len(seeds) != 13:
        print(f"WARNING: {name} has {len(seeds)} seeds, expected 13")
    
    total_seeds += len(seeds)
    for coord in seeds:
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
print(f"Total Seeds: {total_seeds}")
print(f"Active Columns (Occupied by at least one planet): {active_columns}")
print(f"Empty Columns (Dead Zones): {empty_columns}")
print(f"Common Active Columns (Occupied by >1 planet): {len(common_coords)}")
print(f"Unique Active Columns (Occupied by exactly 1 planet): {len(unique_coords)}")

print("\n--- Distribution ---")
print(f"41 Empty: {empty_columns == 41}")
print(f"41 Common: {len(common_coords) == 41}")
print(f"22 Unique: {len(unique_coords) == 22}")

if len(unique_coords) != 22:
    print(f"DISCREPANCY DETECTED. Unique count is {len(unique_coords)}")
    print("Unique Points:")
    for c in unique_coords:
        print(c)
else:
    print("VERIFICATION SUCCESSFUL: 41 - 41 - 22 Topology Confirmed.")
