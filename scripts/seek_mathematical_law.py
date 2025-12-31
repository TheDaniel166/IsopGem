#!/usr/bin/env python3
"""
The Rite of Deep Seeking (seek_mathematical_law.py)
---------------------------------------------------
Analyzes the progression of Conrune Deltas to find the governing Law.

Hypotheses:
1. Is there a constant Step between sorted unique values?
2. Do the Deltas along the "Spiral" (Kin 1, 2, 3...) follow a pattern?
3. Are the Deltas related to the Kin number via a modulus?
"""
import csv
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from pillars.time_mechanics.services.tzolkin_service import TzolkinService

def get_conrune(ditrune: str) -> str:
    conrune = []
    for char in ditrune:
        if char == '1': conrune.append('2')
        elif char == '2': conrune.append('1')
        else: conrune.append('0')
    return "".join(conrune)

def ternary_to_decimal(ternary_str: str) -> int:
    return int(ternary_str, 3)

def analyze():
    print("state_of_mind: calculating_the_law")
    
    service = TzolkinService()
    
    # Calculate Deltas for Kin 1 to 260 ordered
    deltas = []
    
    for k in range(1, 261):
        s_idx = (k - 1) % 20
        t_idx = (k - 1) % 13
        
        val_dec = service._decimal_grid[s_idx][t_idx]
        val_ter = service._ternary_grid[s_idx][t_idx]
        conrune_ter = get_conrune(val_ter)
        conrune_dec = ternary_to_decimal(conrune_ter)
        
        delta = abs(val_dec - conrune_dec)
        deltas.append(delta)
        
    print(f"🔮 Analyzed {len(deltas)} Kins.")
    
    # 1. Sequential Difference (Kin 2 - Kin 1)
    print("\n🔮 Sequential Differences (First 20 steps):")
    diffs = []
    for i in range(len(deltas) - 1):
        diffs.append(deltas[i+1] - deltas[i])
    print(f"   {diffs[:20]}")
    
    # Look for pattern in diffs
    # Are they repeating?
    # Sequence of diffs
    
    # 2. Sorted Uniques Analysis
    unique_vals = sorted(list(set(deltas)))
    print(f"\n🔮 Sorted Unique Values (First 20):")
    print(f"   {unique_vals[:20]}")
    
    # Gaps between sorted uniques
    sorted_diffs = [unique_vals[i+1] - unique_vals[i] for i in range(len(unique_vals)-1)]
    print(f"   Gaps between uniques (First 20): {sorted_diffs[:20]}")
    
    # 3. Modulo Analysis
    # Is Delta % X == Constant?
    # Tzolkin is 260. 13, 20.
    # Base 3 -> 3^n.
    print(f"\n🔮 Modulo Analysis (Delta % 27):")
    mods = [d % 27 for d in deltas[:13]] # First trecena
    print(f"   First Trecena Mods (27): {mods}")
    
    # 4. The Winding Law (Columnar)
    # How does Delta change as we go down Column 1 of the CSV (Tone 1, Signs 1-20)?
    print(f"\n🔮 Column 1 Progression (Tone 1, Signs 1-20):")
    col1_deltas = []
    
    # We need to find which Kin corresponds to (Sign S, Tone 1)
    # Map (Sign, Tone) -> Kin
    kin_map = {}
    for k in range(1, 261):
        s = (k - 1) % 20
        t = (k - 1) % 13
        kin_map[(s, t)] = k
        
    for s_idx in range(20): # Iterate down the rows of Column 1
        t_idx = 0 # Tone 1
        kin = kin_map.get((s_idx, t_idx))
        if kin:
            d = deltas[kin - 1]
            col1_deltas.append(d)
        
    print(f"   Val: {col1_deltas}")
    diff_col = [col1_deltas[i+1] - col1_deltas[i] for i in range(len(col1_deltas)-1)]
    print(f"   Dif: {diff_col}")

    # 5. Base-9 Reduction
    print(f"\n🔮 Base-9 Reduction of Column 1 Deltas:")
    base9 = [x % 9 for x in col1_deltas]
    print(f"   Mod 9: {base9}")

    # 6. Columnar Harmonics Analysis
    print(f"\n🔮 Columnar Harmonics (Base Analysis per Tone):")
    
    # We need to map Kin back to Tone/Sign or just iterate 
    # Use the map we built earlier
    
    for t_idx in range(13): # Tones 0-12 (Col 1-13)
        col_deltas = []
        for s_idx in range(20):
            kin = kin_map.get((s_idx, t_idx))
            if kin:
                col_deltas.append(deltas[kin-1])
        
        # Analyze this column
        # Check divisibility by 9, 3, 27
        div9 = all(d % 9 == 0 for d in col_deltas)
        div3 = all(d % 3 == 0 for d in col_deltas)
        div2 = all(d % 2 == 0 for d in col_deltas)
        
        # Check constant residues
        mod9 = set(d % 9 for d in col_deltas)
        mod3 = set(d % 3 for d in col_deltas)
        
        print(f"   Tone {t_idx+1}: Div9={div9}, Div3={div3}, Div2={div2} | Mods9={mod9}, Mods3={mod3}")
        if div9:
            print(f"      -> Harmonic Base: 9 (Cubic)")
        elif div3:
             print(f"      -> Harmonic Base: 3 (Ternary)")
             
        # Check for arithmetic progression in the column
        diffs = [col_deltas[i+1] - col_deltas[i] for i in range(len(col_deltas)-1)]
        uniq_diffs = set(diffs)
        print(f"      -> Diffs: {list(uniq_diffs)[:5]}...")

if __name__ == "__main__":
    analyze()
