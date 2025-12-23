import sys
import os
import math

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pillars.adyton.services.kamea_loader_service import KameaLoaderService

def find_cluster_split():
    loader = KameaLoaderService(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    grid = loader.load_grid()
    
    # Octant 1: x>0, y>0, x>y (East-North)
    # Slope = y/x. Range 0 to 1.
    
    cells = list(grid.values())
    oct1 = [c for c in cells if c.octant_id == 1]
    
    print(f"Octant 1 Total: {len(oct1)} cells.")
    
    # Sort by Slope (Angle) from 0 (East axis) to 1 (Diagonal)
    # Actually Octant 1 is defined as x > y. So slope is < 1.
    # Note: cell (x=13, y=1) -> slope 1/13.
    # cell (x=2, y=1) -> slope 0.5.
    
    sorted_cells = sorted(oct1, key=lambda c: c.y / c.x)
    
    # Split into 3 groups of 26
    g1 = sorted_cells[0:26]
    g2 = sorted_cells[26:52]
    g3 = sorted_cells[52:78]
    
    print(f"Group 1 (0-26): Slope Range {g1[0].y/g1[0].x:.3f} to {g1[-1].y/g1[-1].x:.3f}")
    print(f"Group 2 (26-52): Slope Range {g2[0].y/g2[0].x:.3f} to {g2[-1].y/g2[-1].x:.3f}")
    print(f"Group 3 (52-78): Slope Range {g3[0].y/g3[0].x:.3f} to {g3[-1].y/g3[-1].x:.3f}")
    
    # Visualize
    # Let's print a ASCII map
    max_y = 13
    max_x = 13
    
    print("\n--- VISUAL CLUSTERS ---")
    for y in range(max_y, 0, -1):
        row_str = ""
        for x in range(1, max_x+1):
            # Check which group
            c = next((cell for cell in oct1 if cell.x == x and cell.y == y), None)
            if c:
                if c in g1: char = "1"
                elif c in g2: char = "2"
                elif c in g3: char = "3"
                else: char = "?"
                row_str += f" {char} "
            else:
                row_str += " . "
        print(f"{y:2} |{row_str}")

if __name__ == "__main__":
    find_cluster_split()
