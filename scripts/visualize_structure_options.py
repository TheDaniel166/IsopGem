import sys
import os
import collections

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pillars.adyton.services.kamea_loader_service import KameaLoaderService

def visualize_structure():
    loader = KameaLoaderService(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    grid = loader.load_grid()
    
    # Air Tablet = Octants 1 and 5
    cells = list(grid.values())
    air_cells = [c for c in cells if c.octant_id in [1, 5]]
    
    # Sort shells
    up_cells = [c for c in air_cells if c.octant_id == 1] # Upward Triangle
    down_cells = [c for c in air_cells if c.octant_id == 5] # Downward Triangle
    
    # Sort by Y primarily for visual printing
    # Octant 1: x>0, y>0, x>y. (East-North).
    # Wait, my loader logic for Octant 1:
    # 1 if x > y (East sector pointing Right?)
    # Let's check coordinates.
    
    print(f"Total Air Cells: {len(air_cells)} (Expected 156)")
    
    # Visualize Octant 1 geometry to see how to split it
    print("\n--- OCTANT 1 GEOMETRY (78 Cells) ---")
    # Coordinates
    min_x = min(c.x for c in up_cells)
    max_x = max(c.x for c in up_cells)
    min_y = min(c.y for c in up_cells)
    max_y = max(c.y for c in up_cells)
    print(f"X bounds: {min_x}..{max_x}, Y bounds: {min_y}..{max_y}")
    
    # Create grid for visualization
    # We want to label them to show splits.
    # Option A: Split by diagonal? center line?
    # Octant 1 is bounded by y=0 and y=x.
    # The "median" would be y = x/2?
    
    # Let's print the grid marking the MEDIAN split (Left/Right half of the wedge)
    # The wedge opens to the Right (East).
    # Top boundary y=x. Bottom boundary y=0.
    # "Left" and "Right" in the wedge context means "Upper" and "Lower" part of the wedge?
    # Or Inner/Outer?
    
    # Let's try splitting by y > x/2
    
    for y in range(max_y, min_y - 1, -1):
        line = ""
        for x in range(min_x, max_x + 1):
            cell = next((c for c in up_cells if c.x == x and c.y == y), None)
            if cell:
                # Mark Split
                # Split A: Inner vs Outer (Shell < 7 vs Shell >= 7)
                # Split B: Upper vs Lower half of wedge (y > x/2)
                
                is_upper_half = cell.y > (cell.x / 2)
                char = "A" if is_upper_half else "B"
                line += f" {char} "
            else:
                line += " . "
        print(f"{y:2} | {line}")
        
    print("\nTotal A (Upper Half): ", len([c for c in up_cells if c.y > c.x/2]))
    print("Total B (Lower Half): ", len([c for c in up_cells if c.y <= c.x/2]))
    
    # Visualize Octant 5
    print("\n--- OCTANT 5 GEOMETRY (78 Cells) ---")
    # Octant 5: x<0, y<0.
    
    min_x = min(c.x for c in down_cells)
    max_x = max(c.x for c in down_cells)
    min_y = min(c.y for c in down_cells)
    max_y = max(c.y for c in down_cells)
    
    for y in range(max_y, min_y - 1, -1):
        line = ""
        for x in range(min_x, max_x + 1):
            cell = next((c for c in down_cells if c.x == x and c.y == y), None)
            if cell:
                # Split Logic
                is_upper_half = cell.y > (cell.x / 2) # Note x,y are negative
                char = "C" if is_upper_half else "D"
                line += f" {char} "
            else:
                line += " . "
        print(f"{y:3} | {line}")

if __name__ == "__main__":
    visualize_structure()
