import sys
import os
import numpy as np

sys.path.append(os.path.abspath("src"))
from pillars.time_mechanics.services.tzolkin_service import TzolkinService

def get_conrune(trigram):
    res = ""
    for c in trigram:
        if c == '1': res += '2'
        elif c == '2': res += '1'
        else: res += '0'
    return res

def verify_grid_symmetry():
    print("Verifying Grid-Based Columnar Symmetry...")
    service = TzolkinService()
    
    # Load Grid directly from CSV lines to ensure 20x13 structure match
    file_path = os.path.abspath("Docs/time_mechanics/Tzolkin Cycle.csv")
    with open(file_path, 'r') as f:
        lines = [l.strip() for l in f.readlines()]
        
    start_ternary = 21
    ternary_rows = []
    for i in range(20):
        idx = start_ternary + i
        if idx >= len(lines): break
        parts = [p.strip() for p in lines[idx].split(',') if p.strip()]
        ternary_rows.append(parts)
        
    # Verify shape
    rows = len(ternary_rows) # 20
    cols = len(ternary_rows[0]) # 13
    print(f"Grid Loaded: {rows}x{cols}")
    
    # Iterate Columns
    for c in range(cols):
        print(f"\n--- Column {c+1} ---")
        col_ditrunes = [ternary_rows[r][c] for r in range(rows)]
        
        uppers = [d[:3] for d in col_ditrunes]
        lowers = [d[3:] for d in col_ditrunes]
        
        # 1. Lower Constant?
        uniq_lower = set(lowers)
        if len(uniq_lower) == 1:
            print(f"Lower: CONSTANT ({list(uniq_lower)[0]})")
        else:
            print(f"Lower: VARIES ({len(uniq_lower)})")
            
        # 2. Upper Reflection (Row i vs Row 19-i)
        mismatches = 0
        for r in range(10): # Check first half vs second half
            top = uppers[r]
            bot = uppers[19-r]
            if top != get_conrune(bot):
                mismatches += 1
                if c == 0: # Detailed debug for Col 1
                    print(f"  Mismatch at Row {r+1}/{20-r}: {top} vs {bot} (Expected {get_conrune(top)})")
        
        if mismatches == 0:
            print("Upper Reflection: PERFECT")
        else:
            print(f"Upper Reflection: FAILED ({mismatches} mismatches)")

if __name__ == "__main__":
    verify_grid_symmetry()
