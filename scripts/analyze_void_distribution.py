"""
Analyze the actual Void Star distribution from the planetary lattices.
Void Stars = cells that NEVER host a seed across all 7 walls.
"""

import json
from collections import defaultdict

# Load lattices
lattices_path = "/home/burkettdaniel927/projects/isopgem/src/pillars/mods/data/planetary_lattices.json"
with open(lattices_path, 'r') as f:
    lattices = json.load(f)

def calculate_seeds_for_planet(lattice):
    """Calculate seed coordinates for a planetary lattice."""
    groups = defaultdict(list)
    for r in range(8):
        for c in range(13):
            gid = lattice[r][c]
            groups[gid].append((r, c))
    
    seeds = {}
    for gid in range(13):
        cells = groups.get(gid, [])
        if not cells:
            continue
        avg_r = sum(r for r, c in cells) / len(cells)
        avg_c = sum(c for r, c in cells) / len(cells)
        min_dist = float('inf')
        seed = cells[0]
        for r, c in cells:
            dist = (r - avg_r) ** 2 + (c - avg_c) ** 2
            if dist < min_dist:
                min_dist = dist
                seed = (r, c)
        seeds[gid] = seed
    return seeds

# Calculate all seed positions across all planets
all_seeds = set()
planets = ["Sun", "Mercury", "Venus", "Moon", "Mars", "Jupiter", "Saturn"]

print("=== SEED POSITIONS BY PLANET ===")
for planet in planets:
    seeds = calculate_seeds_for_planet(lattices[planet])
    print(f"\n{planet}:")
    for gid, (r, c) in sorted(seeds.items()):
        all_seeds.add((r, c))
        print(f"  #{gid}: ({r},{c})")

print(f"\n=== TOTAL UNIQUE SEED POSITIONS ===")
print(f"Total: {len(all_seeds)} unique cells ever used as seeds")

# Find cells that are NEVER seeds
all_cells = set((r, c) for r in range(8) for c in range(13))
void_cells = all_cells - all_seeds

print(f"\n=== VOID STARS (NEVER SEEDS) ===")
print(f"Total: {len(void_cells)} cells never host a seed")

# Show distribution by row
print("\nDistribution by row:")
for r in range(8):
    row_voids = [(r2, c) for r2, c in void_cells if r2 == r]
    print(f"  Row {r}: {len(row_voids)} voids - {sorted(row_voids)}")

# Show the void pattern as map
print("\n=== VOID MAP ===")
for r in range(8):
    row_str = ""
    for c in range(13):
        if (r, c) in void_cells:
            row_str += " ■ "
        else:
            row_str += " . "
    print(row_str)
