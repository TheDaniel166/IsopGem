import sys
import os
import csv
from datetime import timedelta

sys.path.append(os.path.abspath("src"))
from pillars.time_mechanics.services.tzolkin_service import TzolkinService

def get_conrune_ternary(trigram):
    res = ""
    for c in trigram:
        if c == '1': res += '2'
        elif c == '2': res += '1'
        else: res += '0'
    return res

def ternary_to_decimal(t_str):
    return int(t_str, 3)

def generate_spiral_matrix():
    print("Generating Conrune Spiral Matrix (10x13)...")
    service = TzolkinService()
    
    # We want a 10 rows x 13 cols matrix
    # representing the Top Half of the Tzolkin Grid (Rows 0-9)
    # Each cell contains the delta to its mirror in the Bottom Half (Rows 19-10)
    
    matrix = [[0 for c in range(13)] for r in range(10)]
    
    for c in range(13): # Columns 0-12
        for r in range(10): # Rows 0-9
            # Kin A at (r, c)
            # Tzolkin fills column by column?
            # Convention: Grid[row][col].
            # Col 1 (index 0) has Kins 1, 21, 41... NO.
            # Tzolkin Grid usually represented as Tone 1-13 horizontal?
            # Standard representation: Rows = 20 Signs. Cols = 13 Tones.
            # Kin 1 = (Row 0, Col 0).
            # Kin 2 = (Row 1, Col 1)? No, Kin 2 is Imix (Row 0) Tone 2? No. Ik (Row 1) Tone 2.
            # Wait. Tzolkin logic `(Kin-1) % 20` is Row. `(Kin-1) % 13` is Col.
            
            # Kin 1 = Sign 0 (Imix), Tone 0 (1). -> Grid[0][0].
            # Kin 2 = Sign 1 (Ik), Tone 1 (2). -> Grid[1][1].
            # Kin 20 = Sign 19 (Ahau), Tone 6 (7). -> Grid[19][6].
            # This "Diagonal" filling is the standard Tzolkin view.
            
            # BUT my `Tzolkin Cycle.csv` might be arranged differently?
            # Let's check how I loaded it in `generate_conrune_deltas.py`:
            # `grid.append(parts)` -> 20 rows.
            # The CSV likely has 20 Rows (Signs) and 13 Columns (Tones).
            # Let's assume the CSV structure: Row i is Sign i+1. Col j is Tone j+1?
            # If so, Kin 1 is at (0,0). Kin 2 is at (1,1).
            # But the csv says "Tone 1, Tone 2...".
            
            # Wait. If the CSV is the standard grid:
            # Row 1 (Imix): Tones 1, 8, 2, 9... ?
            # No, Imix occurs at Tones 1, 8, 2...
            # Kin 1 is Imix-1. Kin 21 is Imix-8. Kin 41 is Imix-2.
            # So Grid[0][0] = Kin 1. Grid[0][1] = Kin 21? (Since it's Imix, Tone 8)
            # Actually, standard grid usually has Columns 1-13 as Tones 1-13.
            # So Column 0 = Tone 1.
            # Row 0 = Sign 1 (Imix).
            # Does Kin 21 (Imix, Tone 8) go in Col 7 (index 7)?
            
            # Let's trust generic `from_gregorian` or just calculate positions.
            # Since I need to create a matrix, I need to know which Kin is at `(r, c)`.
            # If the output format is 10x13, I should define what (r,c) means.
            # I will define `(r, c)` as `Sign r` (0-9) and `Tone c` (0-12).
            # But wait. Kin defined by (Sign, Tone) is NOT unique?
            # Yes it is. 20 Signs x 13 Tones = 260 unique combos.
            # So `(Row r, Col c)` uniquely identifies a Kin.
            
            # Find Kin for Sign r, Tone c.
            # Kin s.t. `(Kin-1)%20 == r` and `(Kin-1)%13 == c`.
            # This is the CRT solution.
            
            # Let's verify Kin 1: (0,0). Correct. (1-1)%20=0.
            # Kin 21: (0, 7)? 20%20=0. 20%13=7. Correct.
            
            # So I need to find `k` in 1..260 for each cell based on CRT.
            
            d_a = None
            d_b = None
            
            # Solve for k_a (The Kin at Top-Half position r,c)
            # k_a = ?
            # (k_a - 1) % 20 = r
            # (k_a - 1) % 13 = c
            
            # Brute force lookup since n is small
            k_a = -1
            for k in range(1, 261):
                if (k-1)%20 == r and (k-1)%13 == c:
                    k_a = k
                    break
            
            if k_a == -1:
                print(f"Error finding kin for r={r}, c={c}")
                continue

            # Now find k_b (The Kin at the Mirror Position in the Grid)
            # Mirror of Top-Half (r, c) is Bottom-Half (19-r, 12-c).
            # This corresponds to geometric centrosymmetry.
            mirror_r = 19 - r
            mirror_c = 12 - c
            
            # Find Kin k_b at that position
            k_b = -1
            for k in range(1, 261):
                if (k-1)%20 == mirror_r and (k-1)%13 == mirror_c:
                    k_b = k
                    break
            
            # Verify k_b should be 261 - k_a?
            # Let's check mathematically.
            # (261 - k - 1) % 20 = (260 - k) % 20 = (-k) % 20 = 20 - (k%20) ??
            # If k%20 = r+1. Then 20 - (r+1) = 19 - r.
            # (260 - k) % 13 = (-k) % 13 = 13 - (k%13) ??
            # If k%13 = c+1. Then 13 - (c+1) = 12 - c.
            # Yes! The mathematical mirror IS the grid mirror.
            # So calculating Delta for Grid(r,c) vs Grid(19-r, 12-c) IS calculating Delta(Kin K vs Kin 261-K).
            
            # Calculate Values
            date_a = service.from_gregorian(service.EPOCH + timedelta(days=k_a-1))
            dit_a = date_a.ditrune_ternary
            
            date_b = service.from_gregorian(service.EPOCH + timedelta(days=k_b-1))
            dit_b = date_b.ditrune_ternary
            
            # User wants "conrune pairs difference".
            # `abs(Conrune(dit_a) - Conrune(dit_b))` ?
            # Or `abs(dit_a - dit_b)`?
            # In the Spiral logic, A and B are ALREADY conrunes of each other.
            # `Conrune(dit_a) == dit_b`.
            # So `abs(Conrune(dit_a) - Conrune(dit_b))` is just `abs(dit_b - dit_a)`.
            # Which is the same as `abs(dit_a - dit_b)`.
            # So just diff the values.
            
            val_a = ternary_to_decimal(dit_a)
            val_b = ternary_to_decimal(dit_b)
            
            delta = abs(val_a - val_b)
            matrix[r][c] = delta

    # Write CSV
    out_path = os.path.abspath("Docs/time_mechanics/conrune_deltas_spiral_matrix.csv")
    with open(out_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Block 1: Decimal
        writer.writerow(["DECIMAL DELTAS"])
        writer.writerow([f"Tone {i+1}" for i in range(13)])
        for r in range(10):
            writer.writerow(matrix[r])
            
        writer.writerow([]) # Spacer
        
        # Block 2: Ternary
        writer.writerow(["TERNARY DELTAS"])
        writer.writerow([f"Tone {i+1}" for i in range(13)])
        for r in range(10):
            # Convert row to ternary
            tern_row = []
            for val in matrix[r]:
                if val == 0:
                    tern_row.append("000000")
                else:
                    # Simple Base 3 conversion
                    nums = []
                    n = val
                    while n:
                        n, r_digit = divmod(n, 3)
                        nums.append(str(r_digit))
                    tern_row.append(''.join(reversed(nums)).zfill(6))
            writer.writerow(tern_row)
            
    print(f"Matrix Generated at {out_path}")

if __name__ == "__main__":
    generate_spiral_matrix()
