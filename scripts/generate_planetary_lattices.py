import random
import sys
import time
import json
import os

def generate_planetary_lattices():
    rows = 8
    cols = 13
    target_groups = 13
    target_size = 8
    max_attempts = 100000
    
    walls = ["Sun", "Mercury", "Moon", "Venus", "Jupiter", "Mars", "Saturn"]
    results = {}
    
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "pillars", "mods", "data"))
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "planetary_lattices.json")
    
    print(f"Generating 7 Unique Lattices...")
    
    for wall_name in walls:
        print(f"--- Generating {wall_name} ---")
        found = False
        
        for attempt in range(max_attempts):
            grid = [[-1 for _ in range(cols)] for _ in range(rows)]
            groups = {i: [] for i in range(target_groups)}
            frontiers = {i: set() for i in range(target_groups)}
            
            # 1. SEEDING (Harmonic Fixed Points)
            # Use fixed seeds layout but JITTER them slightly to ensure variety across walls
            # Centers roughly:
            # Top: (1,1), (1,3)...
            
            # Base seeds
            base_seeds = [
                (1, 1), (1, 3), (1, 5), (1, 7), (1, 9), (1, 11),
                (6, 1), (6, 3), (6, 5), (6, 7), (6, 9), (6, 11),
                (3, 6)
            ]
            
            seeds = []
            used_seeds = set()
            
            # Jitter seeds for uniqueness per wall
            for br, bc in base_seeds:
                # Try to jitter by 1 step
                options = [(br, bc)]
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = br+dr, bc+dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        options.append((nr, nc))
                
                # Pick one that isn't used
                random.shuffle(options)
                picked = options[0]
                for opt in options:
                    if opt not in used_seeds:
                        picked = opt
                        break
                seeds.append(picked)
                used_seeds.add(picked)
            
            # Initialize with seeds
            for i, (r,c) in enumerate(seeds):
                grid[r][c] = i
                groups[i].append((r,c))
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        frontiers[i].add((nr,nc))
                        
            # 2. GROWTH LOOP
            active_groups = list(range(target_groups))
            random.shuffle(active_groups)
            
            success = True
            while active_groups:
                stuck_groups = []
                
                # Shuffle active groups each step for organic randomness
                random.shuffle(active_groups)
                
                for g in list(active_groups): 
                    if len(groups[g]) >= target_size:
                        active_groups.remove(g)
                        continue
                    
                    valid_frontier = [c for c in frontiers[g] if grid[c[0]][c[1]] == -1]
                    
                    if not valid_frontier:
                        success = False
                        break
                    
                    nxt = random.choice(valid_frontier)
                    
                    grid[nxt[0]][nxt[1]] = g
                    groups[g].append(nxt)
                    
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
                 # Double check count
                 filled = sum(len(g) for g in groups.values())
                 if filled == 104:
                     print(f"  > Success on attempt {attempt+1}")
                     found = True
                     results[wall_name] = grid
                     break
        
        if not found:
            print(f"  ! FAILED to generate {wall_name}")
            return

    # Save to JSON
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved 7 Lattices to {output_file}")

if __name__ == "__main__":
    generate_planetary_lattices()
