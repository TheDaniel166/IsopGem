import sys
import os
import csv
from datetime import timedelta

sys.path.append(os.path.abspath("src"))
from pillars.time_mechanics.services.tzolkin_service import TzolkinService

def get_conrune(trigram):
    res = ""
    for c in trigram:
        if c == '1': res += '2'
        elif c == '2': res += '1'
        else: res += '0'
    return res

def ternary_to_decimal(t_str):
    return int(t_str, 3)

def generate_spiral_deltas():
    print("Generating Conrune Spiral Analysis...")
    service = TzolkinService()
    
    # We will analyze pairs 1..130 (which map to 260..131)
    # The Spiral is symmetric, so 130 rows covers the whole relation.
    
    out_path = os.path.abspath("Docs/time_mechanics/conrune_deltas_spiral.csv")
    
    with open(out_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Kin A", "Ditrune A", "Decimal A", "Kin B", "Ditrune B", "Decimal B", "Delta (Abs Diff)"])
        
        for k in range(1, 131): # 1 to 130
            # Kin A
            date_a = service.from_gregorian(service.EPOCH + timedelta(days=k-1))
            dit_a = date_a.ditrune_ternary
            
            # Kin B (Mirror)
            k_mirror = 261 - k
            date_b = service.from_gregorian(service.EPOCH + timedelta(days=k_mirror-1))
            dit_b = date_b.ditrune_ternary
            
            # Decimals
            dec_a = ternary_to_decimal(dit_a)
            dec_b = ternary_to_decimal(dit_b)
            
            # Delta
            # User asked for "absolute difference between conrune pairs".
            # Since B IS the Conrune of A (Law 1), we are comparing the Value vs its Reflection.
            delta = abs(dec_a - dec_b)
            
            writer.writerow([k, dit_a, dec_a, k_mirror, dit_b, dec_b, delta])
            
    print(f"Spiral Analysis generated at {out_path}")

if __name__ == "__main__":
    generate_spiral_deltas()
