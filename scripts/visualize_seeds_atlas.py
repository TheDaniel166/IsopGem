
import json
import collections
import os
import sys

def generate_vis():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    lattice_path = os.path.join(project_root, "src/pillars/mods/data/planetary_lattices.json")
    out_path = os.path.join(project_root, "Docs/adyton_walls/The_Atlas_of_Seeds.md")
    
    with open(lattice_path, 'r') as f:
        lattices = json.load(f)

    # 1. Calculate Seeds for All Walls
    # Map: wall -> set of seed coords
    wall_seeds = {}
    all_seeds = set()
    
    planets = ["Sun", "Mercury", "Venus", "Moon", "Mars", "Jupiter", "Saturn"]
    
    for wall in planets:
        # Handle key mismatch logic if any
        # The JSON uses "Sun", "Mercury", etc. Moon might be "Luna".
        # Based on previous file reads, "Sun" is there. Let's assume standard keys first.
        # But previous script iterated `for wall, grid in lattices.items():`.
        # Let's do that to match keys exactly.
        pass
        
    # Re-iterate correctly
    for p_key, grid in lattices.items():
        # Standardize name for display if needed
        # We only care about the 7 planets.
        if p_key not in ["Sun", "Mercury", "Venus", "Moon", "Luna", "Earth", "Mars", "Jupiter", "Saturn"]:
            continue
            
        display_name = p_key
        if p_key == "Luna": display_name = "Moon"
        if p_key == "Earth": display_name = "Moon" # Sometimes Earth is used for Moon wall in this codebase
        
        seeds = set()
        
        groups = collections.defaultdict(list)
        for r in range(8):
            for c in range(13):
                gid = grid[r][c]
                if gid >= 0:
                    groups[gid].append((r,c))
                    
        for gid, cells in groups.items():
            if not cells: continue
            # Calc Seed
            adj = {cell: [] for cell in cells}
            cell_set = set(cells)
            for r, c in cells:
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r+dr, c+dc
                    if (nr, nc) in cell_set:
                        adj[(r,c)].append((nr,nc))
            
            min_ecc = 999
            candidates = []
            for start_node in cells:
                q = collections.deque([(start_node, 0)])
                visited = {start_node}
                max_dist = 0
                while q:
                    curr, dist = q.popleft()
                    max_dist = max(max_dist, dist)
                    for nxt in adj[curr]:
                        if nxt not in visited:
                            visited.add(nxt)
                            q.append((nxt, dist+1))
                if max_dist < min_ecc:
                    min_ecc = max_dist
                    candidates = [start_node]
                elif max_dist == min_ecc:
                    candidates.append(start_node)
            
            chosen_seed = sorted(candidates)[0]
            seeds.add(chosen_seed)
            all_seeds.add(chosen_seed)
            
        wall_seeds[display_name] = seeds

    # 2. Identify Dead Zones
    dead_zones = set()
    for r in range(8):
        for c in range(13):
            if (r,c) not in all_seeds:
                dead_zones.add((r,c))

    # 3. Generate Markdown
    lines = []
    lines.append("# The Atlas of Seeds")
    lines.append("> *\"Map of the Invisible Structure of the Adyton\"*")
    lines.append("")
    lines.append("This document visualizes the **Geometric Seeds** of the 7 Planetary Walls and the **Empty Net** (The Altar).")
    lines.append("")
    
    # 4. The Altar (Dead Zones)
    lines.append("## 1. The Altar of the Universe (The Empty Net)")
    lines.append("The cells marked with `■` represent the **287** values (41 cells x 7 walls) that *never* spawn a constellation.")
    lines.append("They are the static foundation.")
    lines.append("")
    lines.append("```")
    for r in range(8):
        row_str = ""
        for c in range(13):
            if (r,c) in dead_zones:
                row_str += " ■ "
            else:
                row_str += " . "
        lines.append(row_str)
    lines.append("```")
    lines.append("")
    lines.append(f"**Total Dead Zones:** {len(dead_zones)} Coords / 104")
    lines.append("")
    
    # 5. Planetary Maps
    # Sort specifically
    order = ["Sun", "Mercury", "Venus", "Moon", "Mars", "Jupiter", "Saturn"]
    
    for p in order:
        if p not in wall_seeds: continue # Might happen if Lattice key is diff
        
        seeds = wall_seeds[p]
        lines.append(f"## {p.upper()}")
        lines.append(f"**Seed Pattern** (`*` = Seed, `.` = Void)")
        lines.append("```")
        for r in range(8):
            row_str = ""
            for c in range(13):
                if (r,c) in seeds:
                    row_str += " * "
                else:
                    row_str += " . "
            lines.append(row_str)
        lines.append("```")
        lines.append("")
        
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
        
    print(f"Atlas generated at {out_path}")

if __name__ == "__main__":
    generate_vis()
