import json
import csv
import os
import collections

def get_dead_zone_values():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    lattice_path = os.path.join(project_root, "src/pillars/mods/data/planetary_lattices.json")
    walls_dir = os.path.join(project_root, "Docs/adyton_walls")
    
    # 1. Identify Dead Zones
    with open(lattice_path, 'r') as f:
        lattices = json.load(f)

    seed_counts = collections.Counter()
    for wall, grid in lattices.items():
        groups = collections.defaultdict(list)
        for r in range(8):
            for c in range(13):
                gid = grid[r][c]
                if gid >= 0:
                    groups[gid].append((r,c))
        
        for gid, cells in groups.items():
            if not cells: continue
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
            
            seed = sorted(candidates)[0]
            seed_counts[seed] += 1

    dead_zones = []
    for r in range(8):
        for c in range(13):
            if (r,c) not in seed_counts:
                dead_zones.append((r,c))
    dead_zones.sort()
    
    # 2. Load Wall Values
    wall_files = {
        "Sun": "sun_wall.csv",
        "Mercury": "mercury_wall.csv",
        "Venus": "venus_wall.csv",
        "Moon": "luna_wall.csv",
        "Mars": "mars_wall.csv",
        "Jupiter": "jupiter_wall.csv",
        "Saturn": "saturn_wall.csv"
    }
    
    wall_data = {}
    for wall, fname in wall_files.items():
        path = os.path.join(walls_dir, fname)
        vals = []
        if os.path.exists(path):
            with open(path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    vals.append([int(x) for x in row if x.strip()])
        wall_data[wall] = vals

    # 3. Write Report
    out_path = os.path.join(walls_dir, "dead_zones_values.csv")
    print(f"Writing Dead Zone Values to {out_path}...")
    
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        header = ["Row", "Col", "Sun", "Mercury", "Venus", "Moon", "Mars", "Jupiter", "Saturn"]
        writer.writerow(header)
        
        for r, c in dead_zones:
            row_vals = [r, c]
            for w in ["Sun", "Mercury", "Venus", "Moon", "Mars", "Jupiter", "Saturn"]:
                if w in wall_data and r < len(wall_data[w]) and c < len(wall_data[w][r]):
                    row_vals.append(wall_data[w][r][c])
                else:
                    row_vals.append("")
            writer.writerow(row_vals)
            
    print("Done.")

if __name__ == "__main__":
    get_dead_zone_values()
