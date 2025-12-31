#!/usr/bin/env python3
"""
The Rite of Remapping (remap_conrune_deltas.py)
-----------------------------------------------
Generates a new 'Conrune_Deltas_column.csv' with accurate, unique values.

Logic:
    1. Load Tzolkin Grid (Decimal and Ternary).
    2. For each Day (Sign 0-19, Tone 0-12):
       a. Get Value A (Decimal).
       b. Get Ternary T.
       c. Calculate Conrune C_ter (invert 1<->2).
       d. Calculate Value B (Base-3 convert C_ter).
       e. Delta = |A - B|.
    3. Output as CSV (20 Rows, 13 Columns).
"""
import sys
import os
import csv
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from pillars.time_mechanics.services.tzolkin_service import TzolkinService

def get_conrune(ditrune: str) -> str:
    """Invert 1s and 2s."""
    conrune = []
    for char in ditrune:
        if char == '1':
            conrune.append('2')
        elif char == '2':
            conrune.append('1')
        else:
            conrune.append('0')
    return "".join(conrune)

def ternary_to_decimal(ternary_str: str) -> int:
    """Convert Ternary string to int (Base 3)."""
    return int(ternary_str, 3)

def generate_map():
    service = TzolkinService()
    
    output_path = Path("Docs/time_mechanics/Conrune_Deltas_column.csv")
    
    # Prepare header: Tone 1 to Tone 13
    header = [f"Tone {i+1}" for i in range(13)]
    
    rows = []
    
    print("🔮 Calculating Conrune Deltas for all 260 Kins...")
    
    # Iterate Signs (Rows 0-19)
    for sign_idx in range(20):
        row_deltas = []
        for tone_idx in range(13):
            # 1. Get Values
            # Note: service._decimal_grid[sign][tone]
            val_a_dec = service._decimal_grid[sign_idx][tone_idx]
            val_t_str = service._ternary_grid[sign_idx][tone_idx]
            
            # 2. Conrune Logic
            conrune_str = get_conrune(val_t_str)
            val_b_dec = ternary_to_decimal(conrune_str)
            
            # 3. Delta
            delta = abs(val_a_dec - val_b_dec)
            row_deltas.append(delta)
            
        rows.append(row_deltas)
        
    # Write to CSV
    print(f"💾 Writing valid map to {output_path}...")
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
        
    print("✅ Remapping complete.")
    
    # verification sample
    print("\n🔍 Sample Verification (Row 1 - Sign 1 Imix):")
    print(f"   Deltas: {rows[0]}")

if __name__ == "__main__":
    generate_map()
