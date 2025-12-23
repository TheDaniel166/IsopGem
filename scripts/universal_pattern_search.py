import sys
import os
import collections

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pillars.adyton.services.kamea_loader_service import KameaLoaderService
from pillars.adyton.models.kamea_cell import KameaCell

from pillars.tq.services.ternary_service import TernaryService

def get_wall_index(decimal_value, wall_map):
    if decimal_value not in wall_map: return 99
    return wall_map[decimal_value]

def analyze_conrune_invariance(grid, wall_map):
    print("\n=== CONRUNE INVARIANCE CHECK ===")
    # Formula: Wall(x) == Wall(Conrune(x))
    
    matches = 0
    total = 0
    
    for c in grid.values():
         # Calculate Conrune
         # 1. To Ternary
         tern = TernaryService.decimal_to_ternary(c.decimal_value).zfill(6)
         # 2. Swap 1<->2
         conrune_tern = tern.replace('1', 'x').replace('2', '1').replace('x', '2')
         conrune_val = TernaryService.ternary_to_decimal(conrune_tern)
         
         w1 = get_wall_index(c.decimal_value, wall_map)
         w2 = get_wall_index(conrune_val, wall_map)
         
         if w1 == w2:
             matches += 1
         else:
             pass # mismatch
             
         total += 1
         
    print(f"Wall(x) == Wall(Conrune(x)): {matches}/{total} ({matches/total*100:.1f}%)")

if __name__ == "__main__":
    loader = KameaLoaderService(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    grid = loader.load_grid()
    wall_map = loader.load_wall_map()
    
    # check_symmetry(grid) # Need to update check_symmetry signature to take wall_map too if used
    analyze_conrune_invariance(grid, wall_map)
