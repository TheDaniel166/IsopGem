import random
import sys

def generate_constellations():
    # Grid 8 rows x 13 cols. Total 104.
    rows = 8
    cols = 13
    total_cells = 104
    target_constellations = 13
    cells_per_constellation = 8
    
    grid = [[-1 for _ in range(cols)] for _ in range(rows)]
    
    # Track cells belonging to each group 0..12
    groups = {i: [] for i in range(target_constellations)}
    
    # 1. SEEDING (Harmonic Spacing)
    # We need 13 seeds. 104 / 13 = 8.
    # Let's space them exactly 8 apart linearly, then map to grid.
    # This ensures perfect distribution of "Centers".
    
    print("--- SEEDING ---")
    seeds = []
    # Shift probability: Start range 0-7, 8-15...
    # Pick a random spot in each "Sector" of 8 cells?
    for i in range(target_constellations):
        sector_start = i * 8
        # Pick centroid of sector? Or random within sector?
        # User wants "Harmonic". Let's pick Centroid + slight jitter.
        # Sector centroids: 3, 11, 19...
        center = sector_start + 4
        
        # Jitter -1 to +1
        # pos = center # Strict
        # Let's try Strict Harmonic Distribution first.
        # Actually randomizing start point shifts the whole lattice.
        
        # Let's use a "Knight's Tour" style distribution?
        # No, let's stick to the request: "Clusters... appear random... mathematical harmony".
        
        # Let's try placing seeds at prime intervals?
        # No, just linear for now to guarantee they fit.
        pos = sector_start + (i % 3) # Mild zigzag offset
        
        r, c = divmod(pos, cols)
        grid[r][c] = i
        groups[i].append((r,c))
        seeds.append((r,c))
        
    print(f"Placed {len(seeds)} seeds.")
    
    # 2. GROWTH (Crystal Accretion)
    # Iterate until all groups have 8 cells.
    # To make them "Unique shapes", we can vary the "Growth Vector" for each group.
    # Group 0 prefers growing UP. Group 1 prefers RIGHT. Group 2 prefers DOWN...
    
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1), # Orthogonal
        (-1, 1), (1, 1), (1, -1), (-1, -1) # Diagonal
    ]
    
    # Assign a "Personality" to each group
    personalities = []
    for i in range(target_constellations):
        # Prefer specific directions based on ID
        # e.g. ID 0 prefers (0,1)
        p_dir = directions[i % 8] 
        personalities.append(p_dir)

    completed = 0
    iteration = 0
    
    while completed < target_constellations and iteration < 1000:
        iteration += 1
        progress = False
        
        # Round Robin growth
        for i in range(target_constellations):
            if len(groups[i]) >= 8:
                continue
                
            # Try to grow
            # Find a free neighbor of existing cells
            potential = []
            preferred = []
            
            p_vec = personalities[i]
            
            for (cr, cc) in groups[i]:
                # Check neighbors
                for dr, dc in directions:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if grid[nr][nc] == -1:
                            potential.append((nr, nc))
                            if (dr, dc) == p_vec:
                                preferred.append((nr, nc))
            
            if not potential:
                # Stuck! This happens in naive growth.
                continue
                
            # Pick
            # Prefer "Personality" direction if possible to create unique shapes
            if preferred:
                choice = preferred[0] # Deterministic
            else:
                choice = potential[0] # Fallback
                
            # Occupy
            grid[choice[0]][choice[1]] = i
            groups[i].append(choice)
            progress = True
            
        # Check completion
        completed = sum(1 for i in range(target_constellations) if len(groups[i]) == 8)
        
        if not progress and completed < target_constellations:
             print("Deadlock reached.")
             break

    # 3. VISUALIZE
    print("\n--- ADYTON CONSTELLATIONS (13 x 8) ---")
    print(f"Completed Groups: {completed}/13")
    
    # Symbols map 0..12 -> Digits/Letters
    symbols = "0123456789ABC"
    
    for r in range(rows):
        line = ""
        for c in range(cols):
            val = grid[r][c]
            if val == -1: char = "."
            else: char = symbols[val]
            line += f" {char} "
        print(line)
        
    # Analyze Shapes
    print("\n--- SHAPE ANALYSIS ---")
    for i in range(target_constellations):
        cells = groups[i]
        # Bounding box
        min_r = min(c[0] for c in cells)
        max_r = max(c[0] for c in cells)
        min_c = min(c[1] for c in cells)
        max_c = max(c[1] for c in cells)
        w = max_c - min_c + 1
        h = max_r - min_r + 1
        print(f"Constellation {symbols[i]}: {len(cells)} cells. Box {w}x{h}. Personality {personalities[i]}")

if __name__ == "__main__":
    generate_constellations()
