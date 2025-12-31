#!/usr/bin/env python3
"""
The Rite of The Shift (verify_menorah_shifts.py)
------------------------------------------------
Verifies the Arithmetic Shifts between the Left and Right Branches of the Menorah.

Hypothesis:
    Bridge Shift: (Tone 8/9) - (Tone 5/6) == +1
    Shoulder Shift: (Tone 10/11) - (Tone 3/4) == +3
    Wing Shift: (Tone 12/13) - (Tone 1/2) == ??

Data is sourced from 'Docs/time_mechanics/Converse_Menorah_Deltas.csv'.
"""
import csv
import sys
from pathlib import Path

def analyze_shifts():
    print("state_of_mind: calculating_the_shift")
    
    input_path = Path("Docs/time_mechanics/Converse_Menorah_Deltas.csv")
    
    grid = []
    with open(input_path, 'r') as f:
        reader = csv.reader(f)
        try:
            next(reader) # skip header
        except StopIteration:
            pass
        for row in reader:
            if row:
                # Store as Operands (div 26)
                grid.append([int(int(x)/26) for x in row])
                
    # Grid Cols: 0(T1/2), 1(T3/4), 2(T5/6), 3(Axis), 4(T8/9), 5(T10/11), 6(T12/13)
    
    bridge_shifts = []
    shoulder_shifts = []
    wing_shifts = []
    
    print("\n🔮 Analyzing Constant Shifts (Right - Left):")
    
    for i, row in enumerate(grid):
        # Bridge: Col 4 - Col 2
        b_shift = row[4] - row[2]
        bridge_shifts.append(b_shift)
        
        # Shoulder: Col 5 - Col 1
        s_shift = row[5] - row[1]
        shoulder_shifts.append(s_shift)
        
        # Wing: Col 6 - Col 0
        w_shift = row[6] - row[0]
        wing_shifts.append(w_shift)
        
    # Verify Bridge (+1?)
    unique_b = set(bridge_shifts)
    print(f"   Bridge Shifts (T8/9 - T5/6): {unique_b}")
    if unique_b == {1}:
        print("   ✅ BRIDGE LAW CONFIRMED: Always +1")
    else:
        print(f"   ❌ BRIDGE LAW FAILED: {unique_b}")
        
    # Verify Shoulder (+3?)
    unique_s = set(shoulder_shifts)
    print(f"   Shoulder Shifts (T10/11 - T3/4): {unique_s}")
    if unique_s == {3}:
        print("   ✅ SHOULDER LAW CONFIRMED: Always +3")
    else:
        print(f"   ❌ SHOULDER LAW FAILED: {unique_s}")

    # Analyze Wing Shift
    unique_w = set(wing_shifts)
    print(f"   Wing Shifts (T12/13 - T1/2): {unique_w}")
    # Print wing shifts list
    print(f"   Sequence: {wing_shifts}")

if __name__ == "__main__":
    analyze_shifts()
