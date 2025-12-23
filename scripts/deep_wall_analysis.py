import sys
import os
import collections

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pillars.adyton.services.kamea_loader_service import KameaLoaderService
from pillars.adyton.models.kamea_cell import KameaCell

def analyze_deep():
    loader = KameaLoaderService(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    grid = loader.load_grid()
    wall_map = loader.load_wall_map()
    
    def get_wall(val):
        # 0 and 364 are Axis/Void
        if val not in wall_map: return 99
        return wall_map[val]
    
    cells = list(grid.values())
    
    # 1. OCTANT-WALL CORRELATION
    print("\n=== 1. OCTANT-WALL CORRELATION ===")
    
    # Map Octant -> {Wall: Count}
    oct_wall_map = collections.defaultdict(lambda: collections.defaultdict(int))
    
    for c in cells:
        w = get_wall(c.decimal_value)
        oct_wall_map[c.octant_id][w] += 1
        
    for oct_id in sorted(oct_wall_map.keys()):
        counts = oct_wall_map[oct_id]
        total = sum(counts.values())
        print(f"\nOctant {oct_id} (Total {total} cells):")
        
        # Sort walls by frequency
        sorted_walls = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        # Print top 3 dominant walls
        top_str = ", ".join([f"Wall {w}: {cnt} ({cnt/total*100:.1f}%)" for w, cnt in sorted_walls[:3]])
        print(f"  Dominant: {top_str}")
        
        # Calculate Average Wall Index for this Octant
        weighted_sum = sum(w * cnt for w, cnt in counts.items() if w != 99)
        avg_wall = weighted_sum / total if total > 0 else 0
        print(f"  Avg Wall Index: {avg_wall:.2f}")

    # 2. RADIAL GRADIENT ANALYSIS
    print("\n=== 2. RADIAL GRADIENT (Shell Analysis) ===")
    # Shell = max(abs(x), abs(y))
    # Range 0 to 13?
    
    shell_wall_map = collections.defaultdict(list)
    for c in cells:
        shell = max(abs(c.x), abs(c.y))
        w = get_wall(c.decimal_value)
        if w != 99:
            shell_wall_map[shell].append(w)
            
    print("Shell | Avg Wall | Min Wall | Max Wall")
    for s in sorted(shell_wall_map.keys()):
        walls = shell_wall_map[s]
        avg = sum(walls)/len(walls)
        print(f"{s:5} | {avg:8.2f} | {min(walls):8} | {max(walls):8}")

    # 3. GLOBAL WALL DISTRIBUTION
    print("\n=== 3. GLOBAL WALL DISTRIBUTION ===")
    total_cells = len(cells)
    global_counts = collections.defaultdict(int)
    for c in cells:
        w = get_wall(c.decimal_value)
        global_counts[w] += 1
        
    for w in sorted(global_counts.keys()):
        print(f"Wall {w}: {global_counts[w]} cells ({global_counts[w]/total_cells*100:.1f}%)")

if __name__ == "__main__":
    analyze_deep()
