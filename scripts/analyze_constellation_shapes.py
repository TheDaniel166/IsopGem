
import os
import sys
import json
import collections

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def analyze_constellation_shapes():
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    lattice_path = os.path.join(project_root, "src", "pillars", "mods", "data", "planetary_lattices.json")
    
    with open(lattice_path, 'r') as f:
        lattices = json.load(f)

    # Planets
    planets = ["Sun", "Mercury", "Moon", "Venus", "Jupiter", "Mars", "Saturn"]
    
    # Map
    shape_map = {} # (Wall, GroupID) -> ShapeString
    
    for p_name in planets:
        l_key = p_name
        if p_name == "Moon" and "Moon" not in lattices:
            if "Luna" in lattices: l_key = "Luna"
            elif "Earth" in lattices: l_key = "Earth"

        if l_key not in lattices:
            print(f"Skipping {p_name}, no lattice found.")
            continue
            
        grid = lattices[l_key]
        
        # 1. Group Cells
        groups = collections.defaultdict(list)
        for r in range(8):
            for c in range(13):
                gid = grid[r][c]
                if gid >= 0:
                    groups[gid].append((r,c))
                    
        # 2. Normalize Shapes for each group
        for gid, cells in groups.items():
            if not cells: continue
            
            # Normalize to 0,0
            min_r = min(r for r, c in cells)
            min_c = min(c for r, c in cells)
            
            normalized = [(r-min_r, c-min_c) for r, c in cells]
            
            # Create ASCII Grid
            max_r_norm = max(r for r, c in normalized)
            max_c_norm = max(c for r, c in normalized)
            
            # Build string
            lines = []
            for r in range(max_r_norm + 1):
                line = ""
                for c in range(max_c_norm + 1):
                    if (r, c) in normalized:
                        line += "■" # Use block char
                    else:
                        line += "·" # Use mid dot or space? mid dot is nice for alignment
                lines.append(line)
            
            shape_str = "\n".join(lines)
            shape_map[f"{p_name}_{gid}"] = shape_str

    # Export
    out_path = os.path.join(project_root, "Docs", "adyton_walls", "constellation_shapes.json")
    with open(out_path, 'w') as f:
        json.dump(shape_map, f, indent=4)
        
    print(f"Exported {len(shape_map)} shapes to {out_path}.")

if __name__ == "__main__":
    analyze_constellation_shapes()
