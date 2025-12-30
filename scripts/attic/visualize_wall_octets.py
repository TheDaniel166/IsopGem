import sys
import os
import csv
from collections import defaultdict

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pillars.adyton.services.kamea_loader_service import KameaLoaderService

def visualize_octets():
    loader = KameaLoaderService(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    # We need the Wall Map AND the Source Sets.
    # The current load_wall_map returns {decimal: wall_id}.
    # We need to know WHICH SET (1-52) a decimal belongs to.
    
    # Let's re-parse zodiacal_heptagon.csv manually to get Set info.
    csv_path = os.path.join(loader.project_root, "Docs", "adyton_walls", "zodiacal_heptagon.csv")
    
    # Structure: set_id, then columns for planets A/B
    # But wait, looking at load_wall_map implementation...
    # It just iterated rows. Row 1 is Set 1?
    
    # Let's map decimal -> (Wall_ID, Set_ID, Is_A)
    # Wall IDs: 0=Sun, 1=Merc... 6=Saturn.
    
    cell_info = {} # decimal -> list of (wall_id, set_id)
    
    walls = ["Sun", "Mercury", "Moon", "Venus", "Jupiter", "Mars", "Saturn"]
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                set_id = int(row['set'])
            except:
                continue
                
            # Columns: 
            # Sun A, Sun B, Mercury A, Mercury B ...
            
            for w_idx, w_name in enumerate(walls):
                # Column names likely "Sun A", "Sun B" or "Sun_A" etc?
                # Let's check keys based on previous knowledge or just generic
                # Usually: "Sun A", "Sun B"
                
                # Check keys
                keys_a = [k for k in row.keys() if w_name in k and 'A' in k]
                keys_b = [k for k in row.keys() if w_name in k and 'B' in k]
                
                if keys_a and keys_b:
                    val_a = int(row[keys_a[0]])
                    val_b = int(row[keys_b[0]])
                    
                    if val_a not in cell_info: cell_info[val_a] = []
                    cell_info[val_a].append({'wall': w_idx, 'set': set_id, 'type': 'A'})
                    
                    if val_b not in cell_info: cell_info[val_b] = []
                    cell_info[val_b].append({'wall': w_idx, 'set': set_id, 'type': 'B'})

    # Now we have the Source Set for every cell in every wall.
    # Let's visualize Sun Wall (Wall 0).
    target_wall = 0
    print(f"--- Visualizing {walls[target_wall]} Wall Octets ---")
    
    # We need the X,Y coordinates of these cells on the 8x13 grid?
    # Wait, the Wall Designer grid is abstract 8x13? Or does it map to the Kamea?
    # The user said "present me with the Grid of 8 high and 13 long".
    # A Wall has 104 cells. 8 * 13 = 104.
    # How are the 104 cells mapped to the 8x13 grid?
    # Linear sequence? Or geometric?
    # Previous implementation of WallDesigner just made a grid.
    
    # Hypothsis: The 104 cells are ordered by Set ID (1..52) and Side (A/B).
    # Total 104 items.
    # Row 1: Sets 1-7 (approx)?
    # Let's assume a linear mapping for now: 
    # The "Wall Grid" is simply the sequence of cells as defined in the Heptagon CSV, laid out 13 wide.
    # Cell 0 = Set 1 A
    # Cell 1 = Set 1 B
    # ...
    # Cell 103 = Set 52 B.
    
    # If we do this, and we group sets 1-4... those are just lines. That's boring.
    
    # ALTERNATIVE: The "Wall Grid" is the Kamea Geometry filtered for that wall?
    # But the Kamea is scattered. The user wants a "Constellation".
    # User said: "Grid of 8 high and 13 long". This implies a RECTANGLE.
    # This rectangle is a constructed abstraction.
    
    # Let's try mapping the 104 cells onto 8x13.
    # Method 1: Ordered by Set ID.
    # Group 1 (Set 1-4) = First 8 cells.
    # If layout is row-major 13 cols:
    # 8 cells take up roughly half a row.
    # This will just look like blocks.
    
    # UNLESS: The "Randomness" comes from the VALUES of the cells, not their Set Index?
    # No, we are grouping BY Set Index ("clusters of 8 cells").
    # If the layout is orderly, the clusters are orderly blocks.
    # Therefore, the layout on the 8x13 grid must be "scrambled" or "folded" in some way?
    
    # OR: The "Clusters of 8" are NOT sequential Sets.
    # They are determined by some other factor.
    # User: "appear random... but follow mathematical harmony".
    
    # Let's try grouping by Modulo 13?
    # 52 Sets.
    # Group 1: Set 1, 14, 27, 40? (Spacing by 13)
    # Total 4 sets x 2 = 8 cells.
    # Group 2: Set 2, 15, 28, 41...
    
    # Let's visualize this MODULO grouping on a standard sequential grid.
    # Grid: 0..103.
    # Cell i (where i is 0..103). Set = i // 2 + 1.
    # Coloring by Group.
    
    grid = [['.' for _ in range(13)] for _ in range(8)]
    
    mod_groups = defaultdict(list)
    
    for i in range(104):
        set_idx = (i // 2) + 1 # 1..52
        
        # Partition Algorithm: Modulo 13 on Set ID
        # (set_idx - 1) % 13 -> 0..12 (13 groups)
        group_id = (set_idx - 1) % 13
        
        mod_groups[group_id].append(i)
        
        # Map to 8x13 Grid (Linear fill)
        r = i // 13
        c = i % 13
        
        # Char based on group
        # Groups 0-9 = digits. 10=A, 11=B, 12=C
        if group_id < 10: char = str(group_id)
        elif group_id == 10: char = 'A'
        elif group_id == 11: char = 'B'
        elif group_id == 12: char = 'C'
        
        grid[r][c] = char

    print("\n--- OCTET MAP (Modulo 13 Distribution) ---")
    for row in grid:
        print(" ".join(row))
        
    # Check "Randomness"
    # Row 0 (cells 0-12): Sets 1..7
    # Col 0: Set 1 (Grp 0). Col 1: Set 1 (Grp 0). Col 2: Set 2 (Grp 1)...
    # This creates a diagonal stripe pattern usually.
    
    # Let's try Modulo 4 grouping?
    # No we need 13 groups.
    
    # What about prime steps?
    # 13 Groups of 4 Sets.
    # Step 13 is good.
    # Let's see the output.

if __name__ == "__main__":
    visualize_octets()
