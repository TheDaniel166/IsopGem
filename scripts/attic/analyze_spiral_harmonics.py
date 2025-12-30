import sys
import os
import csv
import math

# Sequence identified in mystic column
MYSTIC_SEQ = [5, 7, 11, 13, 12, 10, 8, 6, 4, 2]

def gcd_list(nums):
    if not nums: return 1
    res = nums[0]
    for n in nums[1:]:
        res = math.gcd(res, n)
    return res

def analyze_harmonics():
    print("Performing Deep Harmonic Analysis...")
    
    file_path = os.path.abspath("Docs/time_mechanics/conrune_deltas_spiral_matrix.csv")
    
    # Read decimal block (Rows 3-12 in file, which are matrix rows 0-9)
    # Actually wait, file structure:
    # Line 1: DECIMAL DELTAS
    # Line 2: Header
    # Line 3-12: Data
    
    matrix = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        lines = list(reader)
        # Slicing hardcoded based on known structure
        data_lines = lines[2:12]
        for l in data_lines:
            matrix.append([int(x) for x in l])
            
    # Matrix is 10 rows x 13 cols.
    # Let's analyze harmonic properties of Columns.
    
    cols = []
    for c in range(13):
        col_data = [matrix[r][c] for r in range(10)]
        cols.append(col_data)
        
    print(f"\n{'='*60}")
    print(f"{'TONE':<5} | {'GCD':<5} | {'NORMALIZED SEQUENCE'}")
    print(f"{'-'*60}")
    
    for i, col in enumerate(cols):
        # We look at the "Base Sequence" from Bottom Up (as per my previous analysis)
        # Indices 0..9 are Top..Bottom.
        # My previous analysis found the sequence 5,7,11... by reading UP.
        # So let's reverse the column for analysis? Or just consistently look at it.
        # Mystic Column (Tone 7, Index 6) reading TOP DOWN (0..9):
        # 140, 196, 308, 364, 336, 280, 224, 168, 112, 56
        # Div by 28:
        # 5, 7, 11, 13, 12, 10, 8, 6, 4, 2
        # This is EXACTLY the Mystic Seq I found.
        
        freq = gcd_list(col)
        norm = [x // freq for x in col]
        
        # Check against Mystic
        match = " UNIQUE"
        if norm == MYSTIC_SEQ:
            match = " == MYSTIC"
        elif norm == list(reversed(MYSTIC_SEQ)):
            match = " == MYSTIC(REV)"
        
        norm_str = str(norm)
        if len(norm_str) > 40: norm_str = norm_str[:37] + "..."
        
        print(f" {i+1:<4} | {freq:<5} | {norm_str}{match}")

    print(f"{'='*60}")
    
    # 2. Analyze the "Warp"
    # Row 3 (Index 2 was 308). Row 4 (Index 3 was 364 - Peak).
    # The Sequence 5, 7, 11... jumps.
    # 5 -> 7 (+2)
    # 7 -> 11 (+4)
    # 11 -> 13 (+2)
    # 13 -> 12 (-1) -- INFLECTION POINT
    # 12 -> 10 (-2)
    # 10 -> 8 (-2)
    # 8 -> 6 (-2)
    # 6 -> 4 (-2)
    # 4 -> 2 (-2)
    
    # The descent is linear (-2).
    # The ascent is 5,7,11,13. (+2, +4, +2).
    # Why the jump?
    # Because 5 (Top row) is actually Row 0.
    # Real physical bottom is Row 9 (Value 2).
    # 2 (+2) -> 4
    # 4 (+2) -> 6
    # 6 (+2) -> 8
    # 8 (+2) -> 10
    # 10 (+2) -> 12
    # 12 (+1) -> 13 (PEAK)
    # 13 (-2) -> 11
    # 11 (-4) -> 7
    # 7 (-2) -> 5
    
    # It looks like a Wave that compresses at the top?
    # Or maybe there is a missing row? (Row -1?)
    
    print("\nDeep Pattern Search Complete.")

if __name__ == "__main__":
    analyze_harmonics()
