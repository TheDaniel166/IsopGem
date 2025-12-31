#!/usr/bin/env python3
"""
The Rite of the Ouroboros (verify_ouroboros.py)
-----------------------------------------------
Verifies the Law of the Ouroboros:
    Kin(t) and Kin(261-t) must be Conrunes of each other.

Logic:
    For t in 1 to 130 (half cycle):
        Ditrune_A = Tzolkin(Kin t)
        Ditrune_B = Tzolkin(Kin 261-t)
        
        Conrune_A = invert(Ditrune_A)
        
        Assert Ditrune_B == Conrune_A
"""
import sys
import os
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

def verify():
    service = TzolkinService()
    
    # We need to access kins by index or number.
    # The service calculates by date.
    # Let's use the Grid directly if accessible, or reverse engineer from Kin.
    # Calculating from Kin is easier:
    # Kin k -> (Tone, Sign) -> Grid Look up
    
    print("🐍 Verifying the Law of the Ouroboros...\n")
    
    failures = 0
    
    for k in range(1, 131): # Check first half (1 to 130)
        k_mirror = 261 - k
        
        # Get Ditrune for Kin k
        # Standard Tzolkin Logic:
        # Sign = (k-1) % 20
        # Tone = (k-1) % 13
        s_idx = (k - 1) % 20
        t_idx = (k - 1) % 13
        
        ditrune_a = service._ternary_grid[s_idx][t_idx]
        
        # Get Ditrune for Kin mirror
        s_idx_m = (k_mirror - 1) % 20
        t_idx_m = (k_mirror - 1) % 13
        
        ditrune_b = service._ternary_grid[s_idx_m][t_idx_m]
        
        # Calculate Conrune of A
        conrune_a = get_conrune(ditrune_a)
        
        if ditrune_b != conrune_a:
            print(f"❌ FAIL at Kin {k} / {k_mirror}")
            print(f"   Kin {k} Ditrune: {ditrune_a}")
            print(f"   Kin {k} Conrune: {conrune_a}")
            print(f"   Kin {k_mirror} Actual:  {ditrune_b}")
            failures += 1
            
    if failures == 0:
        print("✅ SUCCESS: The Ouroboros is perfect. The cycle is a closed loop.")
    else:
        print(f"\n💀 FAILED: Found {failures} distortions in the mirror.")

if __name__ == "__main__":
    verify()
