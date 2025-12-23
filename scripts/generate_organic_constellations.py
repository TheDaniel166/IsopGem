import random
import sys
import time

def generate_organic_constellations():
    rows = 8
    cols = 13
    target_groups = 13
    target_size = 8
    max_attempts = 10000
    
    symbols = "0123456789ABC"
    
    start_time = time.time()
    
    for attempt in range(max_attempts):
        grid = [[-1 for _ in range(cols)] for _ in range(rows)]
        groups = {i: [] for i in range(target_groups)}
        frontiers = {i: set() for i in range(target_groups)}
        
        # 1. SEEDING (Harmonic Fixed Points)
        # Use fixed seeds to ensure space for everyone
        # 4 cols x 2 rows logic roughly?
        # 13 points spreading across 8x13
        # Ideal centers:
        seeds = [
            (1, 1), (1, 3), (1, 5), (1, 7), (1, 9), (1, 11),  # Top Row approx
            (6, 1), (6, 3), (6, 5), (6, 7), (6, 9), (6, 11),  # Bot Row approx
            (3, 6) # Middle Core
        ]
        # Just 13 points well distributed.
        
        # Override with jitter? No, strict start.
        for i, (r,c) in enumerate(seeds):
            grid[r][c] = i
            groups[i].append((r,c))
            # Add neighbors to frontier
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    frontiers[i].add((nr,nc))
                    
        # 2. GROWTH LOOP
        # Round robin growth
        active_groups = list(range(target_groups))
        random.shuffle(active_groups)
        
        success = True
        while active_groups:
            # Sort by "Most Desperate" (fewest neighbor options)? Or just random?
            # Random is fine.
            # Or iterate all active.
            
            stuck_groups = []
            
            for g in list(active_groups): # copy list to modify
                if len(groups[g]) >= target_size:
                    active_groups.remove(g)
                    continue
                
                # Try to grow
                # Filter frontier for valid unassigned cells
                valid_frontier = [c for c in frontiers[g] if grid[c[0]][c[1]] == -1]
                
                if not valid_frontier:
                    # Stuck!
                    success = False
                    break
                
                # Pick one
                # Heuristic: Pick neighbor that has fewer free neighbors? (To hug edges)
                # Or just random organic.
                nxt = random.choice(valid_frontier)
                
                # Commit
                grid[nxt[0]][nxt[1]] = g
                groups[g].append(nxt)
                
                # Update Frontier
                nr, nc = nxt
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nnr, nnc = nr+dr, nc+dc
                    if 0 <= nnr < rows and 0 <= nnc < cols:
                        if grid[nnr][nnc] == -1:
                            frontiers[g].add((nnr, nnc))
                
                if len(groups[g]) >= target_size:
                    active_groups.remove(g)
            
            if not success:
               break
               
        if success:
             # Check if all filled? 
             # Should be. Target 13 * 8 = 104.
             # Double check
             filled = sum(len(g) for g in groups.values())
             if filled == 104:
                 print(f"--- SUCCESS (Attempt {attempt+1}) ---")
                 print_grid(grid, rows, cols, symbols)
                 return
             
    print("Failed to find solution in max attempts.")

def print_grid(grid, rows, cols, symbols):
    print("\n--- ORGANIC CONSTELLATIONS ---")
    for r in range(rows):
        line = ""
        for c in range(cols):
            val = grid[r][c]
            line += f" {symbols[val]} "
        print(line)
        
if __name__ == "__main__":
    generate_organic_constellations()
