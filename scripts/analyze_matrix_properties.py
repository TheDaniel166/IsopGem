import sys
import os
import numpy as np
from datetime import timedelta

# Ensure src in path for Service
sys.path.append(os.path.abspath("src"))
from pillars.time_mechanics.services.tzolkin_service import TzolkinService

def analyze_matrix():
    print("Initializing Matrix Analysis...")
    service = TzolkinService()
    epoch = service.get_epoch()

    # 1. Build the Charge Array (Linear 1-260)
    # ----------------------------------------
    print("Constructing 1D Charge Field (Kin 1 -> 260)...")
    charges = []
    
    for i in range(260):
        target_date = epoch + timedelta(days=i)
        tz_date = service.from_gregorian(target_date)
        ditrune = tz_date.ditrune_ternary
        
        # Calculate Charge
        # 1 -> +1
        # 2 -> -1
        # 0 -> 0
        c = 0
        for char in ditrune:
            if char == '1': c += 1
            elif char == '2': c -= 1
        charges.append(c)

    arr_charges = np.array(charges) # Shape (260,)
    
    # 2. visual Heatmap (20x13 representation)
    # ----------------------------------------
    # How does the 260 map to 20x13?
    # Standard Tzolkin: Columns = Tones (1-13)? Rows = Signs (1-20)?
    # But Kin 1 = (0,0), Kin 2 = (1,1)... diagonal.
    # Let's map it by (Sign_Index, Tone_Index) since that's how the CSV is structured
    # (Row=Sign, Col=Tone).
    # But wait, Kin 1 is (Row 0, Col 0). Kin 2 is (Row 1, Col 1).
    # So we populate the matrix based on Kin coordinates.
    
    matrix_20x13 = np.zeros((20, 13), dtype=int)
    
    for i in range(260):
        kin = i + 1
        charge = charges[i]
        
        # Determine Indices based on Standard Tzolkin Logic
        sign_idx = (kin - 1) % 20
        tone_idx = (kin - 1) % 13
        
        matrix_20x13[sign_idx, tone_idx] = charge

    print("\n[Charge Matrix 20x13 Heatmap]")
    print("(Row=Sign, Col=Tone. '+', '-', '.' representation)")
    print("   " + "".join([f"{t+1:<3}" for t in range(13)]))
    for r in range(20):
        row_str = f"{r+1:<2} "
        for c in range(13):
            val = matrix_20x13[r, c]
            sym = "."
            if val > 0: sym = "+"
            if val < 0: sym = "-"
            if abs(val) > 1: sym = "*" # High charge density
            if abs(val) > 3: sym = "!" # Extreme
            
            # Using simple numeric for better readability?
            # Let's show actual number
            row_str += f"{val:<3}"
        print(row_str)

    # 3. The Linear Fold (Conrune Symmetry)
    # -------------------------------------
    # Hypothesis: Charge(k) + Charge(261-k) == 0
    # Array indices: 0..259.
    # fold check: arr[i] + arr[259-i]
    
    print("\n--- Testing Linear Fold (Temporal Reflection) ---")
    folded = arr_charges + arr_charges[::-1]
    non_zero_fold = np.count_nonzero(folded)
    
    if non_zero_fold == 0:
        print("SUCCESS: Perfect Antisymmetry confirmed.")
        print("Sum(Field) + Sum(Retrograde Field) = 0")
    else:
        print(f"FAILURE: {non_zero_fold} asymmetries found.")
        print("First 10 mismatches:", folded[:10])

    # 4. Matrix Analysis
    # ------------------
    # Transpose Symmetery?
    # Sign/Tone relationship
    print("\n--- Matrix Stats ---")
    print(f"Total Net Charge: {np.sum(matrix_20x13)}")
    print(f"Max Charge: {np.max(matrix_20x13)} (at Kin indices {np.where(matrix_20x13 == np.max(matrix_20x13))})")
    print(f"Min Charge: {np.min(matrix_20x13)}")
    
    # Determinant? (Only for square matrices, 20x13 is not square).
    # Singular Value Decomposition?
    # Maybe 2 10x13 matrices?
    
    # Split into Top (Signs 1-10) and Bottom (Signs 11-20)
    top = matrix_20x13[:10, :]
    bot = matrix_20x13[10:, :]
    
    print("\n--- Top vs Bottom Hemisphere ---")
    print(f"Top Sum: {np.sum(top)}")
    print(f"Bot Sum: {np.sum(bot)}")
    
    fold_vertical = top + bot # Element-wise sum of overlapping rows (1+11, 2+12...)
    print(f"Vertical Fold (Row n + Row n+10) Sum: {np.sum(fold_vertical)}")
    
    # Split Left (Tones 1-6) and Right (Tones 8-13), ignore Tone 7
    left = matrix_20x13[:, :6]
    right = matrix_20x13[:, 7:]
    # Reverse right to fold like a book?
    # Tone 1 vs Tone 13, Tone 2 vs Tone 12...
    right_flipped = np.fliplr(right)
    
    fold_horizontal = left + right_flipped
    print(f"Horizontal Fold (Tone k + Tone 14-k) Non-Zeros: {np.count_nonzero(fold_horizontal)}")
    if np.count_nonzero(fold_horizontal) == 0:
         print("SUCCESS: Perfect Horizontal Symmetry (Book Fold).")

if __name__ == "__main__":
    analyze_matrix()
