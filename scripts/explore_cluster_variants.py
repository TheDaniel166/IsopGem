import sys
import os
import math

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pillars.adyton.services.kamea_loader_service import KameaLoaderService

def explore_variants():
    loader = KameaLoaderService(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    grid = loader.load_grid()
    cells = list(grid.values())
    oct1 = [c for c in cells if c.octant_id == 1]
    
    print(f"Octant 1: {len(oct1)} cells")
    
    # helper to print
    def print_grid(groups, name):
        print(f"\n--- {name} ---")
        max_y = 13
        max_x = 13
        for y in range(max_y, 0, -1):
            row = ""
            for x in range(1, max_x+1):
                c = next((cell for cell in oct1 if cell.x == x and cell.y == y), None)
                if c:
                    if c in groups[0]: char = "1"
                    elif c in groups[1]: char = "2"
                    elif c in groups[2]: char = "3"
                    else: char = "?"
                    row += f" {char} "
                else:
                    row += " . "
            print(f"{y:>2} |{row}")

    # METHOD 1: EUCLIDEAN CENTROIDS (The Three Towers)
    # Octant 1 vertices approx: (0,0), (13,0), (13,13).
    # Centroids for 3 groups?
    # C1 (Base): (10, 2)
    # C2 (Middle): (10, 6)
    # C3 (Top): (10, 10)
    # Actually let's just sort by distance to these arbitrary points and fill buckets.
    
    c1 = (9, 2)   # Inner/Lower
    c2 = (11, 6)  # Outer/Middle
    c3 = (13, 11) # Tip
    
    # Assign each cell to nearest centroid
    g1, g2, g3 = [], [], []
    for c in oct1:
        d1 = math.hypot(c.x - c1[0], c.y - c1[1])
        d2 = math.hypot(c.x - c2[0], c.y - c2[1])
        d3 = math.hypot(c.x - c3[0], c.y - c3[1])
        
        m = min(d1, d2, d3)
        if m == d1: g1.append(c)
        elif m == d2: g2.append(c)
        else: g3.append(c)
        
    print(f"Centroids: G1={len(g1)}, G2={len(g2)}, G3={len(g3)}")
    # Won't be equal unless we force balance.
    # Let's try scanline.
    
    # METHOD 2: SERPENTINE SCAN (Diagonal)
    # Sort by (x+y) then x.
    serpent = sorted(oct1, key=lambda c: (c.x + c.y, c.x))
    s1 = serpent[0:26]
    s2 = serpent[26:52]
    s3 = serpent[52:78]
    print_grid([s1, s2, s3], "SERPENTINE DIAGONAL SCANS")
    
    # METHOD 3: FRACTURED SHELLS (The Rings)
    # Shells 1-6 = 21. Needs 5 from Shell 7.
    # Shell 7 has 7 cells.
    # Shell 8 (8), 9(9). S7 rem (2) + S8 + S9 = 19. Needs 7 from S10.
    # Group 1 = S1..S6 + 5 specific cells of S7.
    # Group 2 = S7(rem) + S8 + S9 + 7 specific cells of S10.
    # Group 3 = Rest.
    
    r1, r2, r3 = [], [], []
    for c in oct1:
        s = max(abs(c.x), abs(c.y))
        
        if s <= 6:
            r1.append(c)
        elif s == 7:
            # We need 5 for G1, 2 for G2.
            # Which 5? Lowest y?
            if len([x for x in r1 if max(abs(x.x),abs(x.y))==7]) < 5:
                 r1.append(c) # Logic flawed loop order
            else:
                 r2.append(c)
        elif s == 8 or s == 9:
            r2.append(c)
        elif s == 10:
             # Need 7 for G2, 3 for G3.
             pass # Logic needs sorting first
        else:
             r3.append(c)

    # Do it properly with sorted shells
    shell_sorted = sorted(oct1, key=lambda c: (max(abs(c.x), abs(c.y)), c.y))
    f1 = shell_sorted[0:26]
    f2 = shell_sorted[26:52]
    f3 = shell_sorted[52:78]
    print_grid([f1, f2, f3], "FRACTURED SHELLS (By Shell, then Y)")

if __name__ == "__main__":
    explore_variants()
