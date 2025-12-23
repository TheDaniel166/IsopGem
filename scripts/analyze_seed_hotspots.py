import json
import collections
import os

def analyze_hotspots():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    lattice_path = os.path.join(project_root, "src/pillars/mods/data/planetary_lattices.json")
    
    with open(lattice_path, 'r') as f:
        lattices = json.load(f)

    # Count occurrences of each coord being a seed
    seed_counts = collections.Counter()
    wall_details = collections.defaultdict(list) # coord -> list of walls

    print("Analyzing Seed Locations across 7 Walls...\n")

    for wall, grid in lattices.items():
        # Identify Seeds for this wall
        groups = collections.defaultdict(list)
        for r in range(8):
            for c in range(13):
                gid = grid[r][c]
                if gid >= 0:
                    groups[gid].append((r,c))
        
        for gid, cells in groups.items():
            if not cells: continue
            # Calc Seed (Graph Center)
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
            wall_details[seed].append(wall)

    # Report
    print(f"Total Unique Seed Locations: {len(seed_counts)}\n")
    
    print("--- TOP SEED HOTSPOTS ---")
    sorted_seeds = seed_counts.most_common()
    
    for coord, count in sorted_seeds:
        walls = ", ".join(wall_details[coord])
        bar = "█" * count
        print(f"{coord} : {count} {bar}  [{walls}]")

    # Check for "Ghost" cells (Never seeds)
    print("\n--- DEAD ZONES (Never Seeds) ---")
    never_seeds = []
    for r in range(8):
        for c in range(13):
            if (r,c) not in seed_counts:
                never_seeds.append((r,c))
    print(f"Count: {len(never_seeds)}")
    
    print("\n--- LIST OF 41 'MA' DEAD ZONES ---")
    # Sort by Row, then Col
    never_seeds.sort()
    for r, c in never_seeds:
        print(f"({r}, {c})")

if __name__ == "__main__":
    analyze_hotspots()
