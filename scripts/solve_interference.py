import sys
import os
import csv
import numpy as np

# Load Matrix
def load_matrix():
    file_path = os.path.abspath("Docs/time_mechanics/conrune_deltas_spiral_matrix.csv")
    matrix = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        lines = list(reader)
        # Slicing hardcoded based on known structure (Lines 3-12)
        data_lines = lines[2:12]
        for l in data_lines:
            matrix.append([int(x) for x in l])
    return matrix

def solve():
    print("Solving Column Interference...")
    m = load_matrix()
    
    # Columns as vectors
    cols = []
    for c in range(13):
        cols.append(np.array([m[r][c] for r in range(10)]))

    # Known Harmonics
    # C0 (Tone 1) = Freq 9
    # C2 (Tone 3) = Freq 3
    # C6 (Tone 7) = Freq 28
    # C10 (Tone 11) = Freq 3
    # C12 (Tone 13) = Freq 9
    
    # Targets: C1, C3, C4, C5 (and mirrors C11, C9, C8, C7 wait indices)
    # C1 is chaotic. Neighbors C0 and C2.
    # Hypothesis: C1 = (C0 + C2) / 2 ? Or some linear diff?
    
    print("\nAnalyzing C1 (Tone 2) vs C0 & C2:")
    delta_sum = cols[0] + cols[2]
    delta_diff = abs(cols[0] - cols[2])
    print(f"C1: {cols[1]}")
    print(f"C0 + C2: {delta_sum}")
    print(f"|C0 - C2|: {delta_diff}")
    
    # Let's check if C1 is related to C6?
    # C1 - C6?
    
    # Let's bruteforce small integer coefficients for C_target = a*C_left + b*C_right + k?
    
    # Analyze C5 (Tone 6) - Neighbor to Mystic C6.
    print("\nAnalyzing C5 (Tone 6) vs C6:")
    print(f"C5: {cols[5]}")
    print(f"C6: {cols[6]}")
    
    # 32 vs 5 (No)
    # 20 vs 7
    # 16 vs 11
    # 14 vs 13
    # 15 vs 12
    # 17 vs 10
    # 19 vs 8
    # 21 vs 6
    # 23 vs 4
    # 25 vs 2
    
    # Look at sum:
    # 32+5=37, 20+7=27 (3^3), 16+11=27, 14+13=27, 15+12=27, 17+10=27, 19+8=27, 21+6=27, 23+4=27, 25+2=27.
    # HOLY.
    # From Row 2 downwards (Index 1..9), C5 + C6 = 27.
    # Row 1 (Index 0) is 37. (27 + 10).
    
    print("\nHYPOTHESIS CONFIRMED: C5 + C6 = 27 (except Row 1)")
    check = (cols[5] + cols[6])
    print(f"Sum: {check}")
    
    # Check C7 (Tone 8) vs C6
    print("\nAnalyzing C7 (Tone 8) vs C6:")
    check_right = (cols[7] + cols[6])
    print(f"Sum: {check_right}")
    # 22+5=27. 34+7=41? No.
    # 22, 34, 38, 40, 39, 37, 35, 33, 31, 29
    # vs 5, 7, 11, 13, 12, 10, 8, 6, 4, 2
    # 22+5=27.
    # 34-7=27.
    # 38-11=27.
    # 40-13=27.
    # 39-12=27.
    # ...
    # So C7 - C6 = 27 (for most)?
    
    # Let's automate this search for "27" relations.
    # The number 27 (3^3) is clearly the Binding Force.
    
    print("\nSearch complete.")

if __name__ == "__main__":
    solve()
