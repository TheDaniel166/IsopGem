import sys

# Since 8x13 is not a power of 2, standard Hilbert is tricky.
# But we can use a "Pseudo-Hilbert" or simply a "Serpentine with localized winding".
# Or better: Recursive Subdivision?
# 104 cells. Split in half (52/52). Split again (26/26). Split again (13/13).
# Wait, 13 is prime. We can't split 13 evenly.
# But we want 13 groups of 8.
# 104 / 8 = 13.

# Let's use a "Space Filling Worm".
# Just wander randomly but self-avoiding until length 8, then start next worm?
# That leaves holes.

# Correct approach: K-Means Clustering on Grid.
# 1. Place 13 centroids.
# 2. Assign every cell to nearest centroid.
# 3. Balance sizes: If a group > 8, give furthest cell to neighbor. If < 8, take from neighbor.
# 4. Repeat until all = 8.

# This creates organic, compact, unique shapes.

def generate_kmeans_constellations():
    import random
    import math

    rows = 8
    cols = 13
    target = 13
    size = 8
    
    # 13 Centroids init
    centroids = []
    # Grid spacing 8x13. 104 cells.
    # roughly sqrt(104/13) = sqrt(8) = 2.8 spacing.
    # Let's place them on a hexagonal-ish lattice.
    
    # Simple valid approach: 
    # Just take 13 points from a shuffled deck of grid coords?
    # No, make them somewhat spread.
    coords = [(r,c) for r in range(rows) for c in range(cols)]
    
    # spread seeds
    seeds = []
    step = 104 // 13
    for i in range(13):
        idx = (i * step + 4) % 104
        seeds.append(coords[idx])
        
    # Assignment loop
    assignment = {} # (r,c) -> group_id
    
    # Iterate to balance
    for _ in range(50): # Max iterations
        # Reset assignment
        groups = {i: [] for i in range(13)}
        
        # 1. Assign to nearest seed
        # But we need exactly 8.
        # So we can't just doing "nearest".
        # We must solve the "Assignment Problem" (Transportation Problem)
        # Cost matrix: Distance from cell X to Seed Y.
        # Constraints: Each Seed gets 8 cells.
        
        # Greedy approximations work well for visual clustering.
        # Sort all (cell, seed) pairs by distance?
        # Too expensive.
        
        # Swap approach.
        # Assign initially by chunks.
        # Then swap cells at boundaries to minimize total variance (compactness).
        
        # INITIAL TILING: Centroid-based to ensure compactness start
        # Place 13 centroids in a roughly 4x3 grid pattern (13 points)
        # Grid 13 cols x 8 rows.
        # 4 cols x 3 rows = 12 points. +1 extra.
        # Spacing:
        cx = [2, 5, 8, 11] # 4 cols
        cy = [1, 4, 6]     # 3 rows
        centers = []
        for y in cy:
            for x in cx:
                centers.append((y, x))
        # Add 13th point
        centers.append((4, 6)) # Center-ish? 
        
        # Ensure distinct seeds
        current_map = [[-1]*cols for _ in range(rows)]
        
        # Naive nearest neighbor assignment
        counts = [0]*13
        cells_flat = [(r,c) for r in range(rows) for c in range(cols)]
        
        # Sort cells by distance to THEIR nearest centroid to prefer core cells first?
        # Actually, let's just spiral fill or something simple.
        # Simple: Assign to nearest, then balance.
        
        # list of (dist, group, r, c)
        assignments = []
        for r, c in cells_flat:
            # Find nearest seed
            dists = []
            for i in range(13):
                sr, sc = centers[i]
                d = (r-sr)**2 + (c-sc)**2
                dists.append((d, i))
            dists.sort()
            assignments.append((dists[0][0], dists[0][1], r, c))
            
        # This doesn't guarantee count=8.
        # Forced Assignment:
        # Just snake fill? No.
        # Let's simple tile:
        # 0 0 1 1 2 2 3 3 
        # 0 0 1 1 2 2 3 3
        # ...
        # This is a pre-baked 4x2 grid tiling.
        # 13 groups. 13 cols.
        # Simple Box Init:
        # G0: (0,0)..(1,3) -> 4x2=8 cells.
        # We can map this manually.
        
        box_defs = [
          (0,0), (0,2), (0,4), (0,6), (0,8), (0,10), # Row 0-3 (Top half)
          (4,0), (4,2), (4,4), (4,6), (4,8), (4,10), # Row 4-7 (Bot half)
          (2, 6) # Middle 13th?
        ]
        # This is getting complicated to code manually. 
        # Let's stick to Centroid "Trading".
        
        # Just assign sequentially 0..12 to cells (r,c) to keep them close?
        # Hilbert curve fill would be ideal.
        # Let's emulate Hilbert Scan (Local Block fill)
        
        # 0 0 1 1 2 2 ...
        # 0 0 1 1 2 2 ... (2 rows per block)
        # Groups 0..5 in Top 4 rows. (6 groups * 8 = 48 cells. Top half 4*13=52. Close)
        # Groups 6..12 in Bot 4 rows.
        
        i = 0
        for r in range(rows):
            for c in range(cols):
                # Custom block mapping
                # Top half (r < 4)
                if r < 4:
                    # 52 cells. Need roughly 6.5 groups.
                    # Let's say Groups 0,1,2,3,4,5
                    # 6 groups * 8 = 48. 4 leftovers.
                    # Just filling linearly typically makes lines.
                    # Let's fill 2x2 blocks?
                    pass
                pass
        
        # Fallback to simple modulo but with "folded" coords to cluster spatial locality
        # r, c -> id. 
        # (r // 2) * 6 + (c // 2) ?
        
        current_map = [[0]*cols for _ in range(rows)]
        
        # Simple Block Filler
        # We need 13 blocks of 8.
        # Let's hardcode a "Good Start"
        # 13 columns.
        # Maybe 8 cells = 2 cols x 4 rows?
        # 6 of those fit in width?
        
        # Let's just use the previous linear fill but TRANPOSED?
        # Fill Columns first?
        # Cols 0-7 -> Group 0? (Straight vertical line 1x8) -> Valid shape!
        # Width 1, Height 8. Warning: Height 8 fails "h>5" check?
        # User hated straight lines.
        
        # Okay, random seed growth with enforced counts.
        seeds = random.sample(cells_flat, 13)
        # BFS separate regions until collision
        
        # Initialize groups as empty lists
        grps = {i: [] for i in range(13)}
        # Assign seeds
        for i, s in enumerate(seeds):
            current_map[s[0]][s[1]] = i
            grps[i].append(s)
            
        unassigned = set(cells_flat) - set(seeds)
        
        # Grow until all 8
        while unassigned:
            # Pick a group that needs cells
            needy = [g for g in range(13) if len(grps[g]) < 8]
            if not needy: break # Should not happen if total=104
            
            # Pick one
            g = random.choice(needy)
            
            # Find neighbors of G
            neighbors = []
            for (r,c) in grps[g]:
                 for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r+dr, c+dc
                    if (nr,nc) in unassigned:
                        neighbors.append((nr,nc))
            
            if neighbors:
                nxt = random.choice(neighbors)
                current_map[nxt[0]][nxt[1]] = g
                grps[g].append(nxt)
                unassigned.remove(nxt)
            else:
                # No neighbors? Pick random unassigned (teleport)
                # Annealing will fix connectivity later.
                if unassigned:
                     nxt = random.choice(list(unassigned)) # Slow but functional
                     current_map[nxt[0]][nxt[1]] = g
                     grps[g].append(nxt)
                     unassigned.remove(nxt)
        
        # Now ANNEALING (Swapping)
        # Randomly pick two touching cells of different groups.
        # If swapping them improves "Compactness" of both groups, do it.
        
        # Helper: Check connectivity of a set of cells
        def is_connected(cells):
            if not cells: return True
            cells_list = list(cells)
            start = cells_list[0]
            queue = [start]
            seen = {start}
            while queue:
                r, c = queue.pop(0)
                # Check neighbors
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r+dr, c+dc
                    if (nr, nc) in cells and (nr, nc) not in seen:
                        seen.add((nr, nc))
                        queue.append((nr, nc))
            return len(seen) == len(cells)

        # Helper: Check shape constraints (prevent straight lines)
        def is_valid_shape(cells):
            if not cells: return True
            rs = [c[0] for c in cells]
            cs = [c[1] for c in cells]
            h = max(rs) - min(rs) + 1
            w = max(cs) - min(cs) + 1
            # Prevent 1x8 or 8x1 lines. Max dim should be, say, 5?
            # 8 cells. Compact is 3x3 approx.
            if h > 5 or w > 5: return False
            return True

        def calculate_compactness(grid_map):
            score = 0
            for g in range(13):
                cells = [(r, c) for r in range(rows) for c in range(cols) if grid_map[r][c] == g]
                if not cells: continue
                
                # Connectivity Penalty (Huge)
                if not is_connected(set(cells)):
                    score += 100000 
                
                # Shape Penalty
                if not is_valid_shape(cells):
                    score += 5000
                
                # Compactness (Variance)
                avg_r = sum(x[0] for x in cells) / len(cells)
                avg_c = sum(x[1] for x in cells) / len(cells)
                var = sum((x[0]-avg_r)**2 + (x[1]-avg_c)**2 for x in cells)
                score += var
            return score

        current_score = calculate_compactness(current_map)
        
        # Mutate
        improved = False
        # Increase attempts to find valid config
        for k in range(5000): 
            r1, c1 = random.randint(0, rows-1), random.randint(0, cols-1)
            # Pick neighbor
            n_opts = []
            if r1>0: n_opts.append((r1-1, c1))
            if r1<rows-1: n_opts.append((r1+1, c1))
            if c1>0: n_opts.append((r1, c1-1))
            if c1<cols-1: n_opts.append((r1, c1+1))
            
            r2, c2 = random.choice(n_opts)
            
            g1 = current_map[r1][c1]
            g2 = current_map[r2][c2]
            
            if g1 == g2: continue
            
            # SWAP
            current_map[r1][c1] = g2
            current_map[r2][c2] = g1
            
            # Only accept if it improves score (reduces penalties)
            new_score = calculate_compactness(current_map)
            
            if new_score <= current_score:
                current_score = new_score
                improved = True
            else:
                # Revert
                current_map[r1][c1] = g1
                current_map[r2][c2] = g2
                
        if not improved:
            # If we are stuck with high score (invalid shapes), restart?
            if current_score > 1000:
                continue # Restart loop
            else:
                break
            
    # VISUALIZE
    symbols = "0123456789ABC"
    print("--- ANNEALED CONSTELLATIONS (Connected & Organic) ---")
    
    # Verify final
    valid = True
    for g in range(13):
         cells = [(r, c) for r in range(rows) for c in range(cols) if current_map[r][c] == g]
         connected = is_connected(set(cells))
         shape = is_valid_shape(cells)
         print(f"Group {symbols[g]}: Connected={connected}, Valid={shape}")
         if not connected or not shape:
             valid = False

    for r in range(rows):
        line = ""
        for c in range(cols):
            val = current_map[r][c]
            line += f" {symbols[val]} "
        print(line)

    if not valid:
        print("WARNING: Some shapes are invalid. Rerunning might help.")

if __name__ == "__main__":
    generate_kmeans_constellations()
