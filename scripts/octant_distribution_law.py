import sys
import os
import collections


# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pillars.adyton.services.kamea_loader_service import KameaLoaderService

def analyze_octant_law():
    loader = KameaLoaderService(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    grid = loader.load_grid()
    wall_map = loader.load_wall_map()
    
    def get_wall(val):
        if val not in wall_map: return 99
        return wall_map[val]
    
    # matrix[octant][wall] = count
    matrix = collections.defaultdict(lambda: collections.defaultdict(int))
    
    cells = list(grid.values())
    
    for c in cells:
        w = get_wall(c.decimal_value)
        matrix[c.octant_id][w] += 1
        
    # 1. Confirm Symmetry law
    print("=== SYMMETRY CONFIRMATION ===")
    pairs = [(1,5), (2,6), (3,7), (4,8)]
    for o1, o2 in pairs:
        match = True
        for w in range(7):
            if matrix[o1][w] != matrix[o2][w]:
                match = False
                break
        status = "EXACT MATCH" if match else "DIFF"
        print(f"Octant {o1} vs {o2}: {status}")

    # 2. Analyze Unique Octants (1, 2, 3, 4)
    # Print the Matrix
    print("\n=== OCTANT DISTRIBUTION MATRIX (1-4) ===")
    header = f"{'Oct':<4} | {'W0 (Sun)':<8} | {'W1 (Mer)':<8} | {'W2 (Mon)':<8} | {'W3 (Ven)':<8} | {'W4 (Jup)':<8} | {'W5 (Mar)':<8} | {'W6 (Sat)':<8} | {'Total':<6}"
    print(header)
    print("-" * len(header))
    
    octants = [1, 2, 3, 4]
    col_sums = {w:0 for w in range(7)}
    
    for o in octants:
        row = matrix[o]
        row_str = f"{o:<4} |"
        total = 0
        for w in range(7):
            count = row[w]
            col_sums[w] += count
            total += count
            row_str += f" {count:<8} |"
        row_str += f" {total:<6}"
        print(row_str)
        
    print("-" * len(header))
    sum_str = f"{'SUM':<4} |"
    for w in range(7):
        sum_str += f" {col_sums[w]:<8} |"
    print(sum_str)
    
    # 3. Analyze Octant 0 (Center)
    print("\n=== CENTER (OCTANT 0) ===")
    row0 = matrix[0]
    print(f"W0:{row0[0]} W1:{row0[1]} W2:{row0[2]} W3:{row0[3]} W4:{row0[4]} W5:{row0[5]} W6:{row0[6]}")

if __name__ == "__main__":
    analyze_octant_law()
