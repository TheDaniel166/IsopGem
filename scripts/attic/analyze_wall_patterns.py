import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pillars.adyton.services.kamea_loader_service import KameaLoaderService
from pillars.adyton.models.kamea_cell import KameaCell

def get_wall_index(decimal_value: int) -> int:
    if decimal_value == 364:
        return 99 # Axis
    norm_val = decimal_value if decimal_value < 364 else decimal_value - 1
    return norm_val // 104

def analyze_air_tablet():
    loader = KameaLoaderService(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    grid = loader.load_grid()
    
    # Air Tablet: Octants 1 and 5
    # Octant 1: Upward Triangle
    # Octant 5: Downward Triangle
    
    cells = list(grid.values())
    air_cells = [c for c in cells if c.octant_id in [1, 5]]
    
    up_cells = [c for c in air_cells if c.octant_id == 1]
    down_cells = [c for c in air_cells if c.octant_id == 5]
    
    # Sort for display (Shells)
    # Shell logic from WatchtowerView
    up_cells.sort(key=lambda c: (max(abs(c.x), abs(c.y)), c.y))
    down_cells.sort(key=lambda c: (max(abs(c.x), abs(c.y)), c.y))
    
    print("--- AIR COMPLETED TABLET WALL DISTRIBUTION ---")
    print("Wall Legend: 0=Sun, 1=Merc, 2=Moon, 3=Ven, 4=Jup, 5=Mars, 6=Sat, X=Axis\n")
    
    # Visualize Up Triangle (Tip at Top)
    # Row 0 has 1 cell, Row 11 has 12 cells
    print("   UPWARD TRIANGLE (Octant 1)")
    current_idx = 0
    for row in range(12):
        count = row + 1
        row_cells = up_cells[current_idx : current_idx + count]
        current_idx += count
        
        row_walls = []
        for c in row_cells:
            w = get_wall_index(c.decimal_value)
            symbol = str(w) if w != 99 else "X"
            row_walls.append(symbol)
        
        # Center align
        padding = " " * (12 - row)
        print(f"{padding}{' '.join(row_walls)}")

    print("\n   DOWNWARD TRIANGLE (Octant 5)")
    # Visualize Down Triangle (Tip at Bottom)
    # Actually logic in View puts Base at Top (Row 11) and Tip at Bottom (Row 0)
    # But usually we print top-down. 
    # Row 11 (Base) is at top visually in the diamond's bottom half?
    # No, in view: 
    # Up Triangle: Tip(0) -> Base(11)
    # Down Triangle: Base(11) -> Tip(0) 
    # So we print Down Triangle in REVERSE row order to match visual diamond geometry
    
    current_idx = 0
    rows_data = []
    for row in range(12):
        count = row + 1
        row_cells = down_cells[current_idx : current_idx + count]
        current_idx += count
        
        row_walls = []
        for c in row_cells:
            w = get_wall_index(c.decimal_value)
            symbol = str(w) if w != 99 else "X"
            row_walls.append(symbol)
        rows_data.append(row_walls)
        
    # Print reversed (Row 11 first, down to Row 0)
    for i, r_walls in enumerate(reversed(rows_data)):
        # Row 11 has 0 padding (widest)
        # Row 0 has 11 padding
        padding = " " * (i + 1)  # +1 to align with base of top triangle roughly
        print(f"{padding}{' '.join(r_walls)}")

    # Analysis
    print("\n--- STATISTICAL ANALYSIS ---")
    wall_counts = {i:0 for i in range(7)}
    wall_counts[99] = 0
    
    for c in air_cells:
        w = get_wall_index(c.decimal_value)
        wall_counts[w] += 1
        
    for w in range(7):
        print(f"Wall {w}: {wall_counts[w]} cells")
    print(f"Axis : {wall_counts[99]} cells")

if __name__ == "__main__":
    analyze_air_tablet()
