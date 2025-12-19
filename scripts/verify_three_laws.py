import sys
import os
import numpy as np

sys.path.append(os.path.abspath("src"))
from pillars.time_mechanics.services.tzolkin_service import TzolkinService

def get_conrune(ditrune):
    res = ""
    for c in ditrune:
        if c == '1': res += '2'
        elif c == '2': res += '1'
        else: res += '0'
    return res

def swap_trigrams(ditrune):
    # Swap first 3 and last 3
    return ditrune[3:] + ditrune[:3]

def verify_laws():
    print("Verifying The Three Laws of the Tzolkin...")
    # Load Grid manually to ensure direct csv indexing
    file_path = os.path.abspath("Docs/time_mechanics/Tzolkin Cycle.csv")
    with open(file_path, 'r') as f:
        lines = [l.strip() for l in f.readlines()]
        
    start_ternary = 21
    grid = [] # 20 rows of lists
    for i in range(20):
        idx = start_ternary + i
        if idx >= len(lines): break
        parts = [p.strip() for p in lines[idx].split(',') if p.strip()]
        grid.append(parts)
        
    # Flatten for Law 1
    # Grid is filled Left-to-Right, Top-to-Bottom?
    # No, Tzolkin fills... actually the CSV is displayed as a Grid.
    # We need to map Kin to Grid Coordinates properly.
    # Based on TzolkinService: decimal_grid[sign_idx][tone_idx]
    # So Grid[Row][Col].
    # Kin 1 is at 0,0.
    # Kin 2 is at... where?
    # Standard Tzolkin: Kin 1 (1 Imix), Kin 2 (2 Ik).
    # So Kin 1 is Row 0, Col 0.
    # Kin 2 is Row 1, Col 1 ?? No usually they step down.
    # IF the CSV is the standard 20x13 grid:
    # Row 1 is Imix (Sign 1). Col 1 is Tone 1.
    # Kin 1 = Imix 1 = (0,0).
    # Kin 2 = Ik 2 = (1,1).
    # ...
    # Kin 20 = Ahau 7 = (19, 6).
    # Kin 21 = Imix 8 = (0, 7).
    # Let's rely on TzolkinService to map Kin to (Row, Col).
    
    service = TzolkinService()
    epoch = service.get_epoch()
    from datetime import timedelta
    
    kin_map = {} # Kin -> Ditrune
    for i in range(260):
        kin = i + 1
        d = service.EPOCH + timedelta(days=i)
        tz = service.from_gregorian(d)
        
        # We need the value from OUR loaded grid to be sure
        r = tz.sign - 1
        c = tz.tone - 1
        ditrune = grid[r][c]
        kin_map[kin] = ditrune

    # LAW 1: The Conrune Spiral
    # -------------------------
    print("\n--- Law 1: The Conrune Spiral (Global Reflection) ---")
    law1_failures = 0
    for k in range(1, 131): # Check up to midpoint
        d_k = kin_map[k]
        d_inv = kin_map[261 - k]
        
        # Property: D(k) == Conrune(D(261-k))
        if d_k != get_conrune(d_inv):
            law1_failures += 1
            if law1_failures < 5:
                print(f"FAIL Kin {k}: {d_k} != Conrune({d_inv})")
    
    if law1_failures == 0:
        print("SUCCESS: The Spiral is perfect.")
    else:
        print(f"FAILURE: {law1_failures} mismatches.")

    # LAW 2: The Law of Converse (Column Pairs)
    # -----------------------------------------
    print("\n--- Law 2: The Law of Converse (Column Pairs) ---")
    # Pairs: (0,1), (2,3), (4,5) ... (13 is odd count, center is 6?)
    # Cols indices: 0..12
    # Pairs: (0,1), (2,3), (4,5), (6 is center?), (7,8), (9,10), (11,12) ??
    # User said "column 1... row 20... conrunes".
    # User implies Center Column is separate.
    # Let's check Pairs (0,1), (2,3), (4,5) AND (7,8), (9,10), (11,12).
    # Skipping 6 (Tone 7).
    pairs = [(0,1), (2,3), (4,5), (7,8), (9,10), (11,12)]
    
    law2_failures = 0
    for c1, c2 in pairs:
        # Check if Col c2 is converse of Col c1
        col_failures = 0
        for r in range(20):
            val1 = grid[r][c1]
            val2 = grid[r][c2]
            
            # Converse = Swap Trigrams
            if val2 != swap_trigrams(val1):
                col_failures += 1
        
        if col_failures == 0:
            print(f"Pair ({c1+1}, {c2+1}): MATCH")
        else:
            print(f"Pair ({c1+1}, {c2+1}): FAIL ({col_failures} rows)")
            law2_failures += 1
            
    # Check Center Column (Index 6 / Tone 7) Self-Consistency?
    # Maybe it is its own Converse? swap(val) == val?
    print(f"Checking Pillar (Col 7)...")
    c7_self_converse = 0
    for r in range(20):
        val = grid[r][6]
        if val == swap_trigrams(val):
            c7_self_converse += 1
    print(f"Col 7 Self-Converse Count: {c7_self_converse} / 20")

    # LAW 3: The Pillar Law (Reflections)
    # -----------------------------------
    print("\n--- Law 3: The Pillar Law (Anchor & Flux) ---")
    # For every column (except maybe 7?), there is an Anchor and a Flux
    # Flux property: Top[r] == Conrune(Top[19-r]) OR Bot[r] == Conrune(Bot[19-r])
    
    for c in range(13):
        col_vals = [grid[r][c] for r in range(20)]
        uppers = [v[:3] for v in col_vals]
        lowers = [v[3:] for v in col_vals]
        
        # Check Anchors
        u_anchor = (len(set(uppers)) == 1)
        l_anchor = (len(set(lowers)) == 1)
        
        # Check Flex (Reflection)
        u_reflect_fails = 0
        l_reflect_fails = 0
        for x in range(10):
            if uppers[x] != get_conrune(uppers[19-x]): u_reflect_fails += 1
            if lowers[x] != get_conrune(lowers[19-x]): l_reflect_fails += 1
            
        u_reflect = (u_reflect_fails == 0)
        l_reflect = (l_reflect_fails == 0)
        
        type_str = "CHAOS"
        if l_anchor and u_reflect: type_str = "ODD-TYPE (Earth Fixed)"
        if u_anchor and l_reflect: type_str = "EVEN-TYPE (Sky Fixed)"
        if u_reflect and l_reflect: type_str = "DOUBLE-REFLECT"
        
        print(f"Col {c+1}: {type_str} [Anc: U={u_anchor} L={l_anchor} | Ref: U={u_reflect} L={l_reflect}]")

if __name__ == "__main__":
    verify_laws()
