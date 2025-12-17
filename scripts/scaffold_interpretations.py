#!/usr/bin/env python3
"""
The Scaffolding Scribe.
Generates the skeleton of the Interpretation Grimoires so the Magus need only fill in the Truth.
"""
import json
from pathlib import Path
from typing import Dict, Any

# The Archetypes
PLANETS = [
    "Sun", "Moon", "Mercury", "Venus", "Mars", 
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", 
    "Chiron", "North Node"
]

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

HOUSES = [str(i) for i in range(1, 13)]

# The Deep Structure Template
DEEP_TEMPLATE = {
    "text": "",
    "archetype": "",
    "essence": "",
    "shadow": "",
    "gift": "",
    "alchemical_process": "",
    "keywords": []
}

DATA_DIR = Path("src/pillars/astrology/data/interpretations")

def load_or_create(filename: str) -> Dict[str, Any]:
    path = DATA_DIR / filename
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_json(filename: str, data: Dict[str, Any]):
    path = DATA_DIR / filename
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Updated {path}")

def scaffold_signs():
    filename = "planets_in_signs.json"
    data = load_or_create(filename)
    
    for planet in PLANETS:
        if planet not in data:
            data[planet] = {}
        for sign in SIGNS:
            if sign not in data[planet]:
                data[planet][sign] = DEEP_TEMPLATE.copy()
            # If exists but is simple string, upgrade it
            elif isinstance(data[planet][sign], str):
                old_text = data[planet][sign]
                new_obj = DEEP_TEMPLATE.copy()
                new_obj["text"] = old_text
                data[planet][sign] = new_obj
                
    save_json(filename, data)

def scaffold_houses():
    filename = "planets_in_houses.json"
    data = load_or_create(filename)
    
    for planet in PLANETS:
        if planet not in data:
            data[planet] = {}
        for house in HOUSES:
            if house not in data[planet]:
                data[planet][house] = DEEP_TEMPLATE.copy()
            elif isinstance(data[planet][house], str):
                old_text = data[planet][house]
                new_obj = DEEP_TEMPLATE.copy()
                new_obj["text"] = old_text
                data[planet][house] = new_obj
                
    save_json(filename, data)

def scaffold_combinatorial():
    filename = "combinatorial.json"
    data = load_or_create(filename)
    
    # Combinatorial is huge (12x12x12 = 1728 entries per planet list). 
    # We will ONLY scaffold keys that already explicitly exist to avoid multiple MB file.
    # OR we can scaffold top-level keys.
    # Let's just ensure the structure exists for manual entry.
    
    for planet in PLANETS:
        if planet not in data:
            data[planet] = {}
            
    save_json(filename, data)

if __name__ == "__main__":
    print("Summoning the Scaffolding Scribe...")
    scaffold_signs()
    scaffold_houses()
    scaffold_combinatorial()
    print("The Grimoires are prepared.")
