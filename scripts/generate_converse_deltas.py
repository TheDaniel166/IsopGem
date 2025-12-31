#!/usr/bin/env python3
"""
The Rite of Inscription (generate_converse_deltas.py)
-----------------------------------------------------
Generates 'Converse_Deltas_column.csv'.

Logic:
    1. Iterate Grid (20 Rows x 13 Cols).
    2. For each cell:
       a. Get Ditrune (Ternary).
       b. Swap Trigrams (Converse).
       c. Calculate Delta = |Val - Converse|.
    3. Write matrix to CSV.
"""
import sys
import os
import csv
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from pillars.time_mechanics.services.tzolkin_service import TzolkinService

def get_converse(ditrune: str) -> str:
    """Swap Upper (0-2) and Lower (3-5) Trigrams."""
    if len(ditrune) < 6: return ditrune.zfill(6) # Safety
    upper = ditrune[:3]
    lower = ditrune[3:]
    return lower + upper

def ternary_to_decimal(ternary_str: str) -> int:
    return int(ternary_str, 3)

def generate_menorah():
    service = TzolkinService()
    output_path = Path("Docs/time_mechanics/Converse_Menorah_Deltas.csv")
    
    # Header: 7 Columns (The Pairs)
    header = ["Tone 1|2", "Tone 3|4", "Tone 5|6", "Tone 7 (Axis)", "Tone 8|9", "Tone 10|11", "Tone 12|13"]
    rows = []
    
    print("🔮 Calculating Converse Menorah Deltas (7-Column Lattice)...")
    
    for s_idx in range(20): # Rows (Signs)
        row_deltas = []
        
        # We only need to sample the Odd Tones (1, 3, 5, 7, 9, 11, 13)
        # Because we proved Even Tones are identical mirrors of Odds under this Law.
        # Actually, Tone 1 mirrors 2. Tone 3 mirrors 4.
        # Tone 8 mirrors 9? Or 8-9 are a pair?
        # Law said: 1-2, 3-4, 5-6, [7], 8-9, 10-11, 12-13.
        # So we sample Tones: 1, 3, 5, 7, 8, 10, 12.
        
        # Wait, the pairs are adjacent.
        # Tone Indices: 0, 2, 4, 6, 7, 9, 11.
        
        target_tones = [0, 2, 4, 6, 8, 10, 12] 
        # TIndices: 0 (Tone 1), 2 (Tone 3), 4 (Tone 5), 6 (Tone 7)...
        # Wait, if 1=2 and 3=4...
        # Tone 1 (idx 0)
        # Tone 3 (idx 2)
        # Tone 5 (idx 4)
        # Tone 7 (idx 6) - Axis
        # Tone 8 (idx 7) is paired with 9 (idx 8)? YES.
        # So we want indices: 
        # Pair 1: idx 0
        # Pair 2: idx 2
        # Pair 3: idx 4
        # Axis:   idx 6
        # Pair 4: idx 7 (Tone 8) 
        # Pair 5: idx 9 (Tone 10)
        # Pair 6: idx 11 (Tone 12)
        
        check_indices = [0, 2, 4, 6, 7, 9, 11]
        
        for t_idx in check_indices: 
            val_dec = service._decimal_grid[s_idx][t_idx]
            val_ter = service._ternary_grid[s_idx][t_idx]
            
            converse_ter = get_converse(val_ter)
            converse_dec = ternary_to_decimal(converse_ter)
            
            delta = abs(val_dec - converse_dec)
            row_deltas.append(delta)
            
        rows.append(row_deltas)
        
    print(f"💾 Writing Menorah table to {output_path}...")
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
        
    print("✅ Inscription complete.")
    
    # Sample Row 1
    print(f"   Row 1 Sample: {rows[0]}")

if __name__ == "__main__":
    generate_menorah()
