import sys
import os
import csv
import random
from datetime import timedelta

sys.path.append(os.path.abspath("src"))
from pillars.time_mechanics.services.tzolkin_service import TzolkinService

# Word Banks (Curated for Evocative Power)
# Based on Physics: Charge, Frequency, Spiral Position

# Nouns - The Subject
NOUNS_LIGHT = ["The Crown", "The Flame", "The Star", "The Beacon", "The Dawn", "The Summit", "The Radiance", "The Throne", "The Phoenix", "The Aurora"]
NOUNS_DARK = ["The Abyss", "The Void", "The Shadow", "The Root", "The Obsidian", "The Cavern", "The Eclipse", "The Anchor", "The Crypt", "The Well"]
NOUNS_NEUTRAL = ["The Horizon", "The Bridge", "The Veil", "The Mirror", "The Gate", "The Path", "The Threshold", "The Pendulum", "The Axis", "The Prism"]

# Verbs/Actions - The Movement
VERBS_ASCENDING = ["Ascending", "Rising", "Igniting", "Awakening", "Unfurling", "Reaching", "Blazing", "Crowning", "Exalting", "Illuminating"]
VERBS_DESCENDING = ["Descending", "Sinking", "Deepening", "Rooting", "Grounding", "Anchoring", "Dissolving", "Returning", "Withdrawing", "Shadowing"]
VERBS_STABLE = ["Holding", "Reflecting", "Balancing", "Bridging", "Witnessing", "Centering", "Transmuting", "Weaving", "Sealing", "Channeling"]

# Modifiers - The Flavor
MODS_ALPHA = ["of Genesis", "at Origin", "of First Light", "at the Gate", "of the Seed"]
MODS_OMEGA = ["of Return", "at Terminus", "of Last Light", "at the Veil", "of the Fruit"]
MODS_AXIS = ["in Stillness", "at the Core", "of Perfect Silence", "in the Eye", "of the Mirror"]
MODS_FLUX = ["in the Storm", "of the Flux", "through Chaos", "within the Spiral", "against the Tide"]
MODS_TRINITY = ["through the Triad", "of the Threefold", "binding the Three", "of the Weave", "in Harmony"]

def get_charge(ditrune):
    charge = 0
    for c in ditrune:
        if c == '1': charge += 1
        elif c == '2': charge -= 1
    return charge

def generate_name(k, tone, ditrune, charge, spiral_pos):
    """Generate a unique poetic name based on physics."""
    
    # 1. Select Noun based on Charge
    if charge >= 4:
        noun = random.choice(NOUNS_LIGHT[:3])  # High Light
    elif charge >= 1:
        noun = random.choice(NOUNS_LIGHT[3:])  # Low Light
    elif charge == 0:
        noun = random.choice(NOUNS_NEUTRAL)
    elif charge >= -3:
        noun = random.choice(NOUNS_DARK[3:])   # Low Dark
    else:
        noun = random.choice(NOUNS_DARK[:3])   # High Dark
        
    # 2. Select Verb based on Spiral Position (1-130 ascending, 131-260 descending)
    if spiral_pos <= 65:
        verb = random.choice(VERBS_ASCENDING)
    elif spiral_pos <= 130:
        verb = random.choice(VERBS_STABLE)
    elif spiral_pos <= 195:
        verb = random.choice(VERBS_STABLE)
    else:
        verb = random.choice(VERBS_DESCENDING)
    
    # 3. Select Modifier based on Column Class
    if tone in [1]:
        mod = random.choice(MODS_ALPHA)
    elif tone in [13]:
        mod = random.choice(MODS_OMEGA)
    elif tone in [7]:
        mod = random.choice(MODS_AXIS)
    elif tone in [3, 11]:
        mod = random.choice(MODS_TRINITY)
    else:
        mod = random.choice(MODS_FLUX)
    
    # Combine
    name = f"{noun} {verb} {mod}"
    return name

def generate_kairoi():
    print("Forging the 260 Kairoi...")
    random.seed(42)  # Reproducible randomness
    
    service = TzolkinService()
    
    out_path = os.path.abspath("Docs/time_mechanics/The_260_Kairoi.csv")
    
    used_names = set()
    
    with open(out_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Kairos", "Poetic Name", "Tone", "Sign", "Charge", "Ditrune"])
        
        for k in range(1, 261):
            d = service.EPOCH + timedelta(days=k-1)
            tz = service.from_gregorian(d)
            
            ditrune = tz.ditrune_ternary
            charge = get_charge(ditrune)
            tone = tz.tone
            sign = tz.sign_name
            
            # Generate unique name
            attempts = 0
            while True:
                name = generate_name(k, tone, ditrune, charge, k)
                if name not in used_names or attempts > 50:
                    used_names.add(name)
                    break
                attempts += 1
            
            writer.writerow([k, name, tone, sign, charge, ditrune])
            
    print(f"The 260 Kairoi generated at {out_path}")

if __name__ == "__main__":
    generate_kairoi()
