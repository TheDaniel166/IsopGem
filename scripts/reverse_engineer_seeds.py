import json
import collections

def reverse_engineer():
    path = "src/pillars/mods/data/planetary_lattices.json"
    with open(path, 'r') as f:
        lattices = json.load(f)
        
    print("Reverse Engineering Seeds via Graph Center Analysis...")
    
    wall_seeds = {}
    
    for wall, grid in lattices.items():
        print(f"\n[{wall}]")
        
        # 1. Group Cells
        groups = collections.defaultdict(list)
        for r in range(8):
            for c in range(13):
                gid = grid[r][c]
                if gid >= 0:
                    groups[gid].append((r,c))
                    
        current_wall_seeds = {}
        
        for gid in sorted(groups.keys()):
            cells = groups[gid]
            if not cells:
                continue
                
            # Build Adjacency
            adj = {cell: [] for cell in cells}
            cell_set = set(cells)
            for r, c in cells:
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r+dr, c+dc
                    if (nr, nc) in cell_set:
                        adj[(r,c)].append((nr,nc))
            
            # Calculate Eccentricity for each cell
            # Eccentricity = max distance to any other cell
            min_ecc = 999
            candidates = []
            
            for start_node in cells:
                # BFS for max dist
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
            
            # Tie breakers?
            # Prefer top-left? Or just list first.
            # Usually seeds are picked somewhat orderly.
            seed = sorted(candidates)[0] # Deterministic tie-break
            current_wall_seeds[gid] = seed
            print(f"  Group {gid}: {seed} (Ecc: {min_ecc}) candidates: {candidates}")
            
        wall_seeds[wall] = current_wall_seeds
        
    # Check for consistency?
    # We already know they aren't fully consistent.
    
if __name__ == "__main__":
    reverse_engineer()
