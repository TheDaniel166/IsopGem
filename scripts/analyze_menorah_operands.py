#!/usr/bin/env python3
"""
The Rite of The Operand (analyze_menorah_operands.py)
-----------------------------------------------------
Decodes the pattern of the factor 'k' where Delta = 26 * k.

Logic:
    1. Load 'Docs/time_mechanics/Converse_Menorah_Deltas.csv'.
    2. Divide every cell by 26.
    3. Check for remainders (Is 26 truly the Universal Constant?).
    4. Print the Matrix of Operands.
    5. Analyze Row Sums, Col Sums, and Symmetry.
"""
import csv
import sys
from pathlib import Path

def analyze_operands():
    print("state_of_mind: decoding_the_26")
    
    input_path = Path("Docs/time_mechanics/Converse_Menorah_Deltas.csv")
    if not input_path.exists():
        print("❌ Error: Menorah table not found.")
        return

    grid = []
    header = []
    
    with open(input_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if row:
                grid.append([int(x) for x in row])
                
    # matrix is 20 rows x 7 cols
    operands_grid = []
    
    print("\n🔮 Multiples of 26 Analysis:")
    
    clean_divisibility = True
    
    for r_idx, row in enumerate(grid):
        op_row = []
        for c_idx, val in enumerate(row):
            if val % 26 != 0:
                print(f"   ❌ ANOMALY at Row {r_idx+1} Col {c_idx+1}: {val} is NOT divisible by 26.")
                clean_divisibility = False
                op_row.append(val / 26.0) # Floating point shame
            else:
                op_row.append(val // 26)
        operands_grid.append(op_row)

    if clean_divisibility:
        print("   ✅ The Law of 26 is Absolute. All values are Integers.")
        
    print("\n📜 The Operand Matrix (The Hidden Integers):")
    # Print formatted table
    col_widths = [5] * 7
    
    # Header indices
    print("      " + " ".join([f"C{i+1}".rjust(5) for i in range(7)]))
    
    for i, row in enumerate(operands_grid):
        row_str = " ".join([str(x).rjust(5) for x in row])
        print(f"R{str(i+1).zfill(2)}: {row_str}")
        
    # Analyze Pattern
    print("\n🔮 Pattern Analysis:")
    # 1. Sum of Row Operands?
    print("   Row Sums:")
    row_sums = [sum(row) for row in operands_grid]
    print(f"   {row_sums}")
    print(f"   Avg Row Sum: {sum(row_sums)/len(row_sums)}")
    
    # 2. Symmetry of Operands
    # Do they sum to something?
    # R1: 4, 16, 20, 0, 21, 19, 13.
    # Col 1 vs Col 7? 4 vs 13.
    # Col 2 vs Col 6? 16 vs 19.
    # Col 3 vs Col 5? 20 vs 21.
    
    print("\n   Symmetry Analysis (Left vs Right):")
    # Check sums of pairs
    # C1+C7, C2+C6, C3+C5
    pair_sums = []
    for row in operands_grid:
        p1 = row[0] + row[6]
        p2 = row[1] + row[5]
        p3 = row[2] + row[4]
        # p4 = row[3] (Axis) is 0
        pair_sums.append((p1, p2, p3))
        
    print("   Pair Sums (C1+C7, C2+C6, C3+C5):")
    for i, p in enumerate(pair_sums):
        print(f"   R{i+1}: {p}")
        
    # 3. Frequency of Operands
    all_ops = [val for row in operands_grid for val in row]
    unique_ops = sorted(list(set(all_ops)))
    print(f"\n   Unique Operands ({len(unique_ops)}): {unique_ops}")


if __name__ == "__main__":
    analyze_operands()
