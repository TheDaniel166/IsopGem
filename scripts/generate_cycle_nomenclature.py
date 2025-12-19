import sys
import os
import csv
import math
from datetime import timedelta

sys.path.append(os.path.abspath("src"))
from pillars.time_mechanics.services.tzolkin_service import TzolkinService

# MAPPINGS
COLUMN_MAP = {
    1:  ("Alpha", "A"),
    2:  ("Flux",  "F-I"), # Interference
    3:  ("Trinity", "T"),
    4:  ("Flux",  "F-II"),
    5:  ("Flux",  "F-III"),
    6:  ("Flux",  "F-IV"),
    7:  ("Axis",  "X"),
    8:  ("Flux",  "F-V"),
    9:  ("Flux",  "F-VI"),
    10: ("Flux",  "F-VII"),
    11: ("Trinity", "T"),
    12: ("Flux",  "F-VIII"),
    13: ("Omega", "O")
}

# Sign Charge Mapping (based on Trigram Sums)
# 1 Imix: 211 (Need to calculate or hardcode?)
# Let's verify charges.
# Imix (1): Top 211 (+4 -1 +1? No.)
# Trigram Logic: 1=Yang(+1), 2=Yin(-1), 0=Neu(0)?
# Let's assume standard Trigram logic or use Trigram Net Sum.
# Sign 4 (Kan): Top 111 (+3). Bottom 111 (+3). Net +6.
# Sign 17 (Caban): Top 222 (-3). Bottom 222 (-3). Net -6.
# I will compute Net Charge dynamically.

def get_charge(ditrune):
    # ditrune is 6 digits.
    # 1=+1, 2=-1, 0=0
    charge = 0
    for c in ditrune:
        if c == '1': charge += 1
        elif c == '2': charge -= 1
    return charge

def get_sign_code(charge):
    if charge > 0: return f"P{charge}" # Positron
    if charge < 0: return f"N{abs(charge)}" # Negatron
    return "E0" # Equator

def generate_nomenclature():
    print("Forging the Lexicon...")
    service = TzolkinService()
    
    out_path = os.path.abspath("Docs/time_mechanics/Cycle_Nomenclature.csv")
    
    with open(out_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Kin", "Col Class", "Sign Class", "Coordinate Name", "Short Code", "Ditrune"])
        
        for k in range(1, 261):
            d = service.EPOCH + timedelta(days=k-1)
            tz = service.from_gregorian(d)
            
            ditrune = tz.ditrune_ternary
            charge = get_charge(ditrune)
            
            col_name, col_sym = COLUMN_MAP[tz.tone]
            sign_code = get_sign_code(charge)
            
            # Full Coordinate Name: "Alpha-01 : P2"
            # Or "Alpha-Positron-2"
            full_name = f"{col_name}-{tz.tone:02d} : {sign_code}"
            
            # Short Code: "A1-P2"
            short_code = f"{col_sym}{tz.tone}-{sign_code}"
            
            writer.writerow([k, col_name, sign_code, full_name, short_code, ditrune])
            
    print(f"Cycle Nomenclature generated at {out_path}")

if __name__ == "__main__":
    generate_nomenclature()
