import sys
import os
from collections import Counter, defaultdict

# Ensure src is in path
sys.path.append(os.path.abspath("src"))

from pillars.time_mechanics.services.tzolkin_service import TzolkinService
from datetime import timedelta

def analyze_patterns():
    print("Beginning Deep Pattern Analysis of the Ternary Grid...")
    service = TzolkinService()
    epoch = service.get_epoch()
    
    # 1. Data Collection
    # ------------------
    trigram_upper_counts = Counter()
    trigram_lower_counts = Counter()
    ditrunes = [] # List of (Kin, Ditrune)
    
    # Orthogonal Stats
    row_sums = defaultdict(int) # Key: Sign Index (0-19)
    col_sums = defaultdict(int) # Key: Tone Index (0-12)
    
    # Net Charge Stats
    charge_sums = [] # List of (Kin, Charge)

    print("Scanning 260 Kins...")
    for i in range(260):
        kin = i + 1
        target_date = epoch + timedelta(days=i)
        tz_date = service.from_gregorian(target_date)
        
        ditrune = tz_date.ditrune_ternary
        upper, lower = service.get_trigrams(ditrune)
        
        # Trigram Counts
        trigram_upper_counts[upper] += 1
        trigram_lower_counts[lower] += 1
        
        # Charge Calculation (2=-1, 1=1, 0=0)
        charge = 0
        for char in ditrune:
            if char == '1': charge += 1
            elif char == '2': charge -= 1
        
        charge_sums.append((kin, charge))
        
        # Orthogonal (Sign/Tone based on Kin, verifying grid structure)
        # Sign 1-20 -> Index 0-19
        sign_idx = tz_date.sign - 1
        tone_idx = tz_date.tone - 1
        
        # We sum the 'charge' for Rows and Cols to see energy density
        row_sums[sign_idx] += charge
        col_sums[tone_idx] += charge
        
        ditrunes.append((kin, ditrune))

    # 2. Analysis & Reporting
    # -----------------------
    
    print("\n--- [1] Trigram Distribution (Total 260) ---")
    print("Are they uniform? (260 / 27 = ~9.6)")
    print(f"{'Trigram':<10} | {'Upper':<10} | {'Lower':<10} | {'Total':<10}")
    print("-" * 50)
    
    all_trigrams = sorted(list(set(list(trigram_upper_counts.keys()) + list(trigram_lower_counts.keys()))))
    
    for t in all_trigrams:
        u = trigram_upper_counts[t]
        l = trigram_lower_counts[t]
        print(f"{t:<10} | {u:<10} | {l:<10} | {u+l:<10}")

    print("\n--- [2] Orthogonal Energy (Net Charge) ---")
    print("\n[Rows / Signs - Energy Density]")
    # Sorted by Sign Index
    for s_idx in range(20):
        name = service.SIGN_NAMES[s_idx]
        print(f"{s_idx+1:<2} {name:<10}: {row_sums[s_idx]}")

    print("\n[Cols / Tones - Energy Density]")
    for t_idx in range(13):
        print(f"Tone {t_idx+1:<2}: {col_sums[t_idx]}")

    print("\n--- [3] The Palindromes (Static Nodes) ---")
    print(f"{'Kin':<5} | {'Ditrune':<10}")
    print("-" * 20)
    palindrome_count = 0
    for kin, dit in ditrunes:
        if dit == dit[::-1]:
            print(f"{kin:<5} | {dit:<10}")
            palindrome_count += 1
            
    print(f"Total Palindromes: {palindrome_count}")

    print("\n--- [4] Charge Oscillation (First 20 Kins) ---")
    print("Kin | Charge")
    for k, c in charge_sums[:20]:
         bar = "+" * c if c > 0 else "-" * abs(c)
         print(f"{k:<3} | {c:<3} {bar}")

if __name__ == "__main__":
    analyze_patterns()
