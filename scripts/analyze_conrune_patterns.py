#!/usr/bin/env python3
"""
The Rite of Pattern Recognition (analyze_conrune_patterns.py)
-------------------------------------------------------------
Analyzes the structure of Docs/time_mechanics/Conrune_Deltas_column.csv.

Outputs:
1. Unique Delta Values found.
2. Symmetry Analysis (Row mirrored? Column mirrored?).
3. Notable Anomalies.
"""
import csv
from collections import Counter

def analyze():
    print("state_of_mind: seeking_patterns")
    
    grid = []
    with open("Docs/time_mechanics/Conrune_Deltas_column.csv", "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if row:
                grid.append([int(x) for x in row])
                
    # 1. Unique Values
    all_values = [val for row in grid for val in row]
    unique_vals = sorted(list(set(all_values)))
    counts = Counter(all_values)
    
    print(f"\n🔮 Unique Delta Values ({len(unique_vals)}):")
    print(unique_vals)
    print("\n   Frequency Map:")
    for v in unique_vals:
        print(f"   Val {v}: {counts[v]} occurrences")
        
    # 2. Column Symmetry (Is Col 1 == Col 13?)
    print(f"\n🔮 Column Symmetry (Wings):")
    cols = list(zip(*grid)) # Transpose to get columns
    sym_cols = 0
    for i in range(6): # Check 0-5 against 12-7
        left = cols[i]
        right = cols[12-i]
        if left == right:
            print(f"   ✅ Col {i+1} mirrors Col {13-i}")
            sym_cols += 1
        else:
            print(f"   ❌ Col {i+1} DOES NOT mirror Col {13-i}")
            
    # 3. Row Symmetry
    print(f"\n🔮 Row Symmetry:")
    sym_rows = 0
    # Rows 0-19. Does Row 0 mirror Row 19? (Kin 1-13 vs Kin 248-260)
    # Actually, Ouroboros suggests Kin 1 mirrors Kin 260.
    # Kin 1 is Row 0, Col 0. Kin 260 is Row 19, Col 12.
    # Symmetry is centrally inverted, not just row-mirror.
    
    # Check simple row mirroring first (Row 0 == Row 19?)
    for i in range(10):
        top = grid[i]
        bottom = grid[19-i]
        if top == bottom:
            print(f"   ✅ Row {i+1} mirrors Row {20-i}")
            sym_rows += 1
        else:
            # Maybe they are reversed?
            if top == bottom[::-1]:
                print(f"   🔄 Row {i+1} mirrors Row {20-i} (REVERSED)")
            else:
                 print(f"   ❌ Row {i+1} DOES NOT mirror Row {20-i}")

if __name__ == "__main__":
    analyze()
