import sys
import os
import csv
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

def ternary_to_decimal(t_str):
    # Ternary to Decimal (Base 3)
    return int(t_str, 3)

def generate_deltas():
    print("Generating Conrune Tension Matrix (Full Ditrune Methodology)...")
    
    # Load Grid Manually
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

    cols = len(grid[0]) # 13
    
    # Matrix to store results
    # Rows: Pair 1 (Row 1-20), Pair 2 (Row 2-19)... Pair 10 (Row 10-11)
    # Cols: Tone 1 - 13
    matrix = [[0 for c in range(13)] for r in range(10)]
    
    for c in range(cols):
        # Taking the full Ditrune (6 digits)
        col_ditrunes = [grid[r][c] for r in range(20)]
        
        for r in range(10): # 0..9
            row_top = r
            row_bot = 19 - r
            
            d_top = col_ditrunes[row_top]
            d_bot = col_ditrunes[row_bot]
            
            # Calculate Conrune of the Ditrunes
            c_top = get_conrune(d_top)
            c_bot = get_conrune(d_bot)
            
            # Convert to Decimal (Base 3)
            dec_top = ternary_to_decimal(c_top)
            dec_bot = ternary_to_decimal(c_bot)
            
            # Absolute Difference
            delta = abs(dec_top - dec_bot)
            
            matrix[r][c] = delta

    # Write CSV
    out_path = os.path.abspath("Docs/time_mechanics/Conrune_Deltas.csv")
    with open(out_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Header
        writer.writerow([f"Tone {i+1}" for i in range(13)])
        # Rows
        for r in range(10):
            writer.writerow(matrix[r])
            
    print(f"Matrix Generated at {out_path}")

if __name__ == "__main__":
    generate_deltas()
