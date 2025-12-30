import sys
import os
import collections

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pillars.adyton.services.kamea_loader_service import KameaLoaderService

def visualize_hexameric_split():
    loader = KameaLoaderService(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    grid = loader.load_grid()
    
    # Air Tablet = Octants 1 and 5 (78 cells each)
    cells = list(grid.values())
    oct1_cells = [c for c in cells if c.octant_id == 1]
    
    print(f"Octant 1 Cells: {len(oct1_cells)} (Target: 3 groups of 26)")
    
    # Method 1: Modulo 3 on Shell (Radial Rings)
    # Shell = max(x, y). Shells 1..12.
    print("\n--- METHOD 1: MODULO 3 ON SHELL (Ring Interlace) ---")
    g0, g1, g2 = [], [], []
    for c in oct1_cells:
        shell = max(abs(c.x), abs(c.y))
        mod = shell % 3
        if mod == 0: g0.append(c) # Shells 3, 6, 9, 12
        elif mod == 1: g1.append(c) # Shells 1, 4, 7, 10
        elif mod == 2: g2.append(c) # Shells 2, 5, 8, 11
        
    print(f"Group 0 (Shell%3==0): {len(g0)}")
    print(f"Group 1 (Shell%3==1): {len(g1)}")
    print(f"Group 2 (Shell%3==2): {len(g2)}")
    
    # Method 2: Rectilinear Modulo (Checkerboard)
    # (x + y) % 3
    print("\n--- METHOD 2: LATTICE MODULO (x+y)%3 ---")
    g0, g1, g2 = [], [], []
    for c in oct1_cells:
        mod = (c.x + c.y) % 3
        if mod == 0: g0.append(c)
        elif mod == 1: g1.append(c)
        elif mod == 2: g2.append(c)
        
    print(f"Group 0 (Sum%3==0): {len(g0)}")
    print(f"Group 1 (Sum%3==1): {len(g1)}")
    print(f"Group 2 (Sum%3==2): {len(g2)}")
    
    # Method 3: Geometric Wedges (Angle Based)
    # Octant 1 spans 45 degrees (slope 0 to 1).
    # Wedge A: slope 0 to 1/3
    # Wedge B: slope 1/3 to 2/3
    # Wedge C: slope 2/3 to 1
    
    print("\n--- METHOD 3: ANGULAR WEDGES ---")
    wA, wB, wC = [], [], []
    for c in oct1_cells:
        # Avoid division by zero, but x > 0 in Octant 1
        slope = c.y / c.x # 0 < slope <= 1
        
        # Angles: 0 to 45 deg.
        # Split 0-15, 15-30, 30-45?
        # Tangent values: tan(15)=0.268, tan(30)=0.577, tan(45)=1.0
        
        if slope <= 0.268:
            wA.append(c)
        elif slope <= 0.577:
            wB.append(c)
        else:
            wC.append(c)
            
    print(f"Wedge A (0-15 deg): {len(wA)}")
    print(f"Wedge B (15-30 deg): {len(wB)}")
    print(f"Wedge C (30-45 deg): {len(wC)}")
    
    # Method 4: Shell Grouping (Contiguous)
    # Find cutoff shells S1, S2 such that Group 1 = 26, Group 2 = 26, Group 3 = 26.
    print("\n--- METHOD 4: CONTIGUOUS SHELLS ---")
    # Shell counts:
    # Shell 1: 1
    # Shell 2: 2
    # ...
    # Shell k: k
    # Cumulative Sums: 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78
    
    # We need sum to equal 26.
    # Shells 1..6 = 21. Need 5 more from Shell 7.
    # Shell 7 has 7 cells.
    # So Split 1: Shells 1-6 + 5 cells of Shell 7.
    # Remainder of Shell 7 (2 cells) + Shell 8 (8) + Shell 9 (9) = 19. Need 7 more from Shell 10.
    # Group 2: Remainder Shell 7 + Shell 8 + Shell 9 + 7 cells of Shell 10.
    # Group 3: Remainder Shell 10 (3) + Shell 11 (11) + Shell 12 (12) = 26.
    
    print("Exact 26-26-26 partitioning is possible but requires splitting Shells 7 and 10.")
    print("Shells 1-6 sum: 21. Shell 7: 7 -> Total 28 (Close to 26).")
    print("Shells 11-12 sum: 23. Shell 10: 10 -> Total 33.")
    
    # Is there ANY shell arithmetic that works perfectly with modulo?
    # No, triangular numbers don't mod 26 easily.

if __name__ == "__main__":
    visualize_hexameric_split()
