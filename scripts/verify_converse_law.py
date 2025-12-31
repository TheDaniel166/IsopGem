#!/usr/bin/env python3
"""
The Rite of the Converse (verify_converse_law.py)
-------------------------------------------------
Verifies the Law of the Converse:
    Swapping the Upper and Lower Trigrams brings Order to Chaos.

Logic:
    For each cell in the Grid:
        1. Get Ditrune (ternary).
        2. Calculate Converse (swap first 3 chars with last 3).
        3. Convert Converse to Decimal.
        4. Calculate Delta_Converse = |Original - Converse|.
        
    Analyze the Delta_Converse values specifically for the Even Columns (Chaos Zones).
    Do they follow the Harmonic Laws (Base-9, Base-3, etc.)?
"""
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from pillars.time_mechanics.services.tzolkin_service import TzolkinService

def get_converse(ditrune: str) -> str:
    """Swap Upper (0-2) and Lower (3-5) Trigrams."""
    if len(ditrune) != 6:
        return ditrune # Should not happen
    upper = ditrune[:3]
    lower = ditrune[3:]
    return lower + upper

def ternary_to_decimal(ternary_str: str) -> int:
    return int(ternary_str, 3)

def analyze():
    print("state_of_mind: twisting_the_trigrams")
    
    service = TzolkinService()
    
    # We will analyze Column by Column (Tone by Tone)
    
    for t_idx in range(13):
        tone = t_idx + 1
        col_deltas = []
        
        for s_idx in range(20):
            val_dec = service._decimal_grid[s_idx][t_idx]
            val_ter = service._ternary_grid[s_idx][t_idx]
            
            converse_ter = get_converse(val_ter)
            converse_dec = ternary_to_decimal(converse_ter)
            
            delta = abs(val_dec - converse_dec)
            col_deltas.append(delta)
            
        # Analyze the column's Deltas
        div9 = all(d % 9 == 0 for d in col_deltas)
        div3 = all(d % 3 == 0 for d in col_deltas)
        div2 = all(d % 2 == 0 for d in col_deltas)
        
        mod9 = set(d % 9 for d in col_deltas)
        
        print(f"🔮 Tone {tone} (Converse Delta):")
        print(f"   Div9={div9}, Div3={div3}, Div2={div2}")
        print(f"   Mods9={mod9}")
        print(f"   Sample: {col_deltas[:5]}")
        
        if div9:
            print(f"   ✅ ORDER RESTORED: Base-9 (Cubic)")
        elif div3:
            print(f"   ✅ ORDER RESTORED: Base-3 (Ternary)")
        elif div2:
            print(f"   ✅ ORDER RESTORED: Base-2 (Binary/Lunar)")
        else:
            print(f"   ❌ Still Chaotic")

if __name__ == "__main__":
    analyze()
