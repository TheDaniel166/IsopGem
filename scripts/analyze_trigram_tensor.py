import sys
import os
import numpy as np
from datetime import timedelta

# Ensure src in path
sys.path.append(os.path.abspath("src"))
from pillars.time_mechanics.services.tzolkin_service import TzolkinService

def trigram_to_charge(t_str):
    # 1=+1, 2=-1, 0=0
    c = 0
    for char in t_str:
        if char == '1': c += 1
        elif char == '2': c -= 1
    return c

def trigram_to_id(t_str):
    # Base 3 integer
    return int(t_str, 3)

def analyze_tensor():
    print("Constructing Trigram Tensor (20 x 13 x 2)...")
    service = TzolkinService()
    epoch = service.get_epoch()
    
    # 3D Arrays
    # Dim 0: Sign (Row)
    # Dim 1: Tone (Col)
    # Dim 2: Layer (0=Upper/Sky, 1=Lower/Earth)
    
    tensor_charge = np.zeros((20, 13, 2), dtype=int)
    tensor_id = np.zeros((20, 13, 2), dtype=int)
    
    for i in range(260):
        kin = i + 1
        target_date = epoch + timedelta(days=i)
        tz_date = service.from_gregorian(target_date)
        
        ditrune = tz_date.ditrune_ternary
        upper, lower = service.get_trigrams(ditrune)
        
        # Coordinates
        r = (kin - 1) % 20 # Sign Index
        c = (kin - 1) % 13 # Tone Index
        
        # Layer 0: Sky
        tensor_charge[r, c, 0] = trigram_to_charge(upper)
        tensor_id[r, c, 0] = trigram_to_id(upper)
        
        # Layer 1: Earth
        tensor_charge[r, c, 1] = trigram_to_charge(lower)
        tensor_id[r, c, 1] = trigram_to_id(lower)

    # Analysis 1: Sky + Earth Correlation (Charge)
    # ---------------------------------------------
    print("\n--- [1] Sky + Earth Charge Sum ---")
    # Sum across the Layer dimension (Dim 2)
    sum_layers = np.sum(tensor_charge, axis=2) # Result is (20, 13)
    
    print(f"Max Sum: {np.max(sum_layers)}")
    print(f"Min Sum: {np.min(sum_layers)}")
    print(f"Mean Sum: {np.mean(sum_layers):.2f}")
    
    # Is it constant?
    if np.min(sum_layers) == np.max(sum_layers):
        print("SUCCESS: Sky + Earth = Constant")
    else:
        print("Result: Varies.")
        
    # Analysis 2: Hemispheric Reflection
    # ----------------------------------
    # Definition: Does Upper World Sky match Lower World Earth?
    # Top 10 Rows (0-9) vs Bottom 10 Rows (10-19)
    
    sky_top = tensor_id[:10, :, 0] # (10, 13)
    earth_bot = tensor_id[10:, :, 1] # (10, 13)
    
    # Check if they are identical? Or mirrored?
    # Let's try direct equality first
    match_count = np.sum(sky_top == earth_bot)
    print(f"\n--- [2] Hemispheric Check (Sky Top vs Earth Bot) ---")
    print(f"Direct Match: {match_count} / 130 cells")
    
    # What about Anti-Symmetry (Charge inversion)?
    sky_charge_top = tensor_charge[:10, :, 0]
    earth_charge_bot = tensor_charge[10:, :, 1]
    
    # Check SkyTop + EarthBot == 0 ?
    fold_hemisphere = sky_charge_top + earth_charge_bot
    zeros = np.count_nonzero(fold_hemisphere == 0)
    print(f"Charge Cancellation (Sky Top + Earth Bot): {zeros} / 130 cells")
    
    # Analysis 3: The Cross-Over (Sky vs Earth across the cycle)
    # ----------------------------------------------------------
    # Let's print heatmaps of Sky vs Earth for the first 5 columns to see visual pattern
    
    print("\n[Visual Sample: Cols 1-5]")
    print("Row | Sky Charge | Earth Charge")
    for r in range(20):
        s_row = tensor_charge[r, :5, 0]
        e_row = tensor_charge[r, :5, 1]
        print(f"{r+1:<3} | {s_row} | {e_row}")
        
    # Check for 'Identity' Trigrams (Sky == Earth)
    # Where does the Trigram repeat itself in the same Kin?
    # i.e. Palindrome halves?
    identity_ditrunes = np.sum(tensor_id[:,:,0] == tensor_id[:,:,1])
    print(f"\nTotal Identity Kins (Sky == Earth): {identity_ditrunes}")

if __name__ == "__main__":
    analyze_tensor()
