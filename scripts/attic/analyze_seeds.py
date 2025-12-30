import json
import os

def analyze_seeds():
    path = "src/pillars/mods/data/planetary_lattices.json"
    with open(path, 'r') as f:
        lattices = json.load(f)
        
    walls = lattices.keys()
    print(f"Analyzing {len(walls)} walls: {list(walls)}")
    
    # Storage for potential seeds: GroupID -> Set of (r,c)
    # Initialize with all cells
    candidates = {}
    for gid in range(13):
        candidates[gid] = set()
        for r in range(8):
            for c in range(13):
                candidates[gid].add((r,c))
                
    # Intersect
    for name, grid in lattices.items():
        print(f"Processing {name}...")
        current_groups_cells = {gid: set() for gid in range(13)}
        
        for r in range(8):
            for c in range(13):
                gid = grid[r][c]
                if gid >= 0:
                     current_groups_cells[gid].add((r,c))
                     
        # Intersect with global candidates
        for gid in range(13):
            candidates[gid] = candidates[gid].intersection(current_groups_cells[gid])
            
    print("\n--- RESULTS ---")
    seeds_found = 0
    final_seeds = {}
    for gid in range(13):
        cands = sorted(list(candidates[gid]))
        print(f"Group {gid}: {cands}")
        if len(cands) == 1:
            seeds_found += 1
            final_seeds[gid] = cands[0]
        elif len(cands) > 1:
            print(f"  Ambiguous! Multiple common cells.")
        else:
            print(f"  No common seed found!")
            
    if seeds_found == 13:
        print("\nSUCCESS! Found unique constant seeds for all groups:")
        for gid in sorted(final_seeds.keys()):
            r, c = final_seeds[gid]
            print(f"Group {gid}: ({r}, {c})")
    else:
        print(f"\nOnly found {seeds_found}/13 seeds.")

if __name__ == "__main__":
    analyze_seeds()
