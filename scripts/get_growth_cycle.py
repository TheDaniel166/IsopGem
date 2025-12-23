import json
import csv
import os
import collections

def get_growth_cycle():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    lattice_path = os.path.join(project_root, "src/pillars/mods/data/planetary_lattices.json")
    walls_dir = os.path.join(project_root, "Docs/adyton_walls")
    
    with open(lattice_path, 'r') as f:
        lattices = json.load(f)
        
    wall_files = {
        "Sun": "sun_wall.csv",
        "Mercury": "mercury_wall.csv",
        "Venus": "venus_wall.csv",
        "Moon": "luna_wall.csv",
        "Mars": "mars_wall.csv",
        "Jupiter": "jupiter_wall.csv",
        "Saturn": "saturn_wall.csv"
    }

    output_path = os.path.join(walls_dir, "wall_seeds_dna.csv")
    print(f"Generating Growth Cycle Report to {output_path}...")
    
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['Wall', 'Group', 
                      'Step1_Val', 'Step2_Val', 'Step3_Val', 'Step4_Val', 
                      'Step5_Val', 'Step6_Val', 'Step7_Val', 'Step8_Val',
                      'Seed_Coord']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for wall, grid in lattices.items():
            csv_name = wall_files.get(wall)
            if not csv_name: continue
            
            csv_path = os.path.join(walls_dir, csv_name)
            wall_values = []
            if os.path.exists(csv_path):
                with open(csv_path, 'r') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        wall_values.append([int(x) for x in row if x.strip()])
            else:
                continue

            # 1. Group Cells
            groups = collections.defaultdict(list)
            for r in range(8):
                for c in range(13):
                    gid = grid[r][c]
                    if gid >= 0:
                        groups[gid].append((r,c))
                        
            for gid in sorted(groups.keys()):
                cells = groups[gid]
                if not cells: continue
                
                # 2. Build Adjacency for this cluster
                adj = {cell: [] for cell in cells}
                cell_set = set(cells)
                for r, c in cells:
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nr, nc = r+dr, c+dc
                        if (nr, nc) in cell_set:
                            adj[(r,c)].append((nr,nc))
                
                # 3. Find Seed (Graph Center / Min Eccentricity)
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
                
                # Deterministic Seed Selection
                seed = sorted(candidates)[0]
                
                # 4. Determine Growth Order (BFS Distance Layers from Seed)
                # (distance, row, col)
                ordered_cells = []
                
                q = collections.deque([(seed, 0)])
                visited = {seed}
                
                while q:
                    curr, dist = q.popleft()
                    val = wall_values[curr[0]][curr[1]]
                    ordered_cells.append({
                        'coord': curr,
                        'dist': dist,
                        'val': val
                    })
                    
                    # Neighbors
                    # Sort neighbors by coord for deterministic BFS queue addition
                    neighbors = sorted(adj[curr])
                    for nxt in neighbors:
                        if nxt not in visited:
                            visited.add(nxt)
                            q.append((nxt, dist+1))
                            
                # Sort just safely, though BFS naturally yields distance order
                # Secondary sort logic: BFS order is good representation of growth front.
                
                # Prepare Row
                row_data = {
                    'Wall': wall,
                    'Group': gid,
                    'Seed_Coord': f"{seed}"
                }
                
                # Fill steps 1-8
                for i in range(8):
                    key = f'Step{i+1}_Val'
                    if i < len(ordered_cells):
                        row_data[key] = ordered_cells[i]['val']
                    else:
                        row_data[key] = ""
                        
                writer.writerow(row_data)
                
    print("Done.")

if __name__ == "__main__":
    get_growth_cycle()
