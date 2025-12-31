#!/usr/bin/env python3
"""
The Rite of the Master Key (verify_trigram_identity.py)
-------------------------------------------------------
Verifies the Algebraic Identity:
    Delta_Converse = 26 * |Upper_Trigram_Value - Lower_Trigram_Value|

Derivation:
    Let Ditrune D = Upper * 27 + Lower
    Converse C = Lower * 27 + Upper
    Delta = |(27U + L) - (27L + U)|
          = |26U - 26L|
          = 26 * |U - L|

If this holds true, the 'Operand' K is simply the difference between the two halves of the Ditrune.
"""
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from pillars.time_mechanics.services.tzolkin_service import TzolkinService

def get_trigrams(ditrune: str):
    """Return decimal values of Upper and Lower trigrams."""
    if len(ditrune) < 6: ditrune = ditrune.zfill(6)
    u_str = ditrune[:3]
    l_str = ditrune[3:]
    return int(u_str, 3), int(l_str, 3)

def get_converse(ditrune: str) -> str:
    if len(ditrune) < 6: ditrune = ditrune.zfill(6)
    upper = ditrune[:3]
    lower = ditrune[3:]
    return lower + upper

def analyze():
    print("state_of_mind: simplifying_the_equation")
    service = TzolkinService()
    
    failures = 0
    total_checks = 0
    
    for s_idx in range(20):
        for t_idx in range(13):
            total_checks += 1
            val_ter = service._ternary_grid[s_idx][t_idx]
            val_dec = service._decimal_grid[s_idx][t_idx]
            
            # 1. Calculate Actual Delta
            conv_ter = get_converse(val_ter)
            conv_dec = int(conv_ter, 3)
            delta_actual = abs(val_dec - conv_dec)
            
            # 2. Calculate Theoretical Delta (26 * |U - L|)
            U, L = get_trigrams(val_ter)
            delta_theory = 26 * abs(U - L)
            
            if delta_actual != delta_theory:
                print(f"❌ FAIL at {s_idx}, {t_idx}")
                print(f"   Ditrune: {val_ter} (U={U}, L={L})")
                print(f"   Actual: {delta_actual}, Theory: {delta_theory}")
                failures += 1
                
    if failures == 0:
        print(f"✅ THE MASTER KEY IS CONFIRMED.")
        print(f"   Checked {total_checks} cells.")
        print(f"   Law: Converse Delta is ALWAYS 26 * |Upper - Lower|")
    else:
        print(f"   ❌ Theory Failed with {failures} errors.")

if __name__ == "__main__":
    analyze()
