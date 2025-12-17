#!/usr/bin/env python3
"""
The Grand Scribe.
Populates the Grimoires with the Ancient Wisdom of the Stars.
"""
import json
from pathlib import Path

# --- THE WISDOM ---

SIGNS_DATA = {
    "Aries": {
        "archetype": "The Pioneer",
        "essence": "Cardianl Fire. Pure vitality, impulse, and the will to exist.",
        "shadow": "Aggression, selfishness, impatience.",
        "gift": "Courage to begin and the strength to stand alone.",
        "keywords": ["Initiative", "Independence", "Action"]
    },
    "Taurus": {
        "archetype": "The Builder",
        "essence": "Fixed Earth. Determining value, sustaining growth, and sensory embodiment.",
        "shadow": "Stubbornness, greed, stagnation.",
        "gift": "Unshakable stability and the creation of lasting beauty.",
        "keywords": ["Stability", "Resource", "Sensation"]
    },
    "Gemini": {
        "archetype": "The Messenger",
        "essence": "Mutable Air. Curiosity, connection, and the weaving of ideas.",
        "shadow": "Scattered energy, superficiality, deceit.",
        "gift": "Versatility and the ability to bridge paradoxes.",
        "keywords": ["Communication", "Learning", "Adaptability"]
    },
    "Cancer": {
        "archetype": "The Mother",
        "essence": "Cardinal Water. Emotional security, nurturing, and ancestral memory.",
        "shadow": "Clinging, moodiness, defensive shells.",
        "gift": "Profound empathy and the power to protect life.",
        "keywords": ["Home", "Emotion", "Nurture"]
    },
    "Leo": {
        "archetype": "The King/Queen",
        "essence": "Fixed Fire. Self-expression, creativity, and the joy of being.",
        "shadow": "Arrogance, narcissism, drama.",
        "gift": "Radiant generosity and the power to inspire others.",
        "keywords": ["Creativity", "Pride", "Heart"]
    },
    "Virgo": {
        "archetype": "The Healer",
        "essence": "Mutable Earth. Purification, service, and the refinement of matter.",
        "shadow": "Perfectionism, criticism, anxiety.",
        "gift": "Discernment and the skill to make things whole.",
        "keywords": ["Service", "Analysis", "Purity"]
    },
    "Libra": {
        "archetype": "The Diplomat",
        "essence": "Cardinal Air. Balance, harmony, and the mirror of the Other.",
        "shadow": "Indecision, codependency, superficial harmony.",
        "gift": "Justice and the creation of beauty in relationship.",
        "keywords": ["Balance", "Relationship", "Beauty"]
    },
    "Scorpio": {
        "archetype": "The Sorcerer",
        "essence": "Fixed Water. Transformation, intensity, and the depths of the psyche.",
        "shadow": "Obsession, manipulation, vengeance.",
        "gift": "Regeneration and the courage to face the darkness.",
        "keywords": ["Transformation", "Power", "Depth"]
    },
    "Sagittarius": {
        "archetype": "The Explorer",
        "essence": "Mutable Fire. Quest for meaning, expansion, and truth.",
        "shadow": "Dogmatism, recklessness, escapism.",
        "gift": "Optimism and the wisdom to see the big picture.",
        "keywords": ["Wisdom", "Adventure", "Philosophy"]
    },
    "Capricorn": {
        "archetype": "The Elder",
        "essence": "Cardinal Earth. Structure, ambition, and the mastery of time.",
        "shadow": "Rigidity, ruthlessness, depression.",
        "gift": "Integrity and the power to build expanding legacies.",
        "keywords": ["Ambition", "Discipline", "Legacy"]
    },
    "Aquarius": {
        "archetype": "The Visionary",
        "essence": "Fixed Air. Innovation, humanity, and the breaking of patterns.",
        "shadow": "Detachment, rebellion without cause, aloofness.",
        "gift": "Genius and the dedication to future progress.",
        "keywords": ["Innovation", "Humanity", "Freedom"]
    },
    "Pisces": {
        "archetype": "The Mystic",
        "essence": "Mutable Water. Dissolution, unity, and the ocean of consciousness.",
        "shadow": "Delusion, victimhood, escapism.",
        "gift": "Compassion and the realization of Oneness.",
        "keywords": ["Dreams", "Unity", "Compassion"]
    }
}

PLANET_THEMES = {
    "Sun": "Your core identity and vitality. How you shine.",
    "Moon": "Your emotional nature and subconscious needs. How you comfort yourself.",
    "Mercury": "Your mind and communication style. How you perceive the world.",
    "Venus": "Your values, love style, and aesthetic sense. What you attract.",
    "Mars": "Your drive, desire, and conflict style. How you get what you want.",
    "Jupiter": "Your growth, abundance, and philosophy. Where you find luck.",
    "Saturn": "Your boundaries, fears, and responsibilities. Where you must do the work.",
    "Uranus": "Your liberation and awakening. Where you break the rules.",
    "Neptune": "Your dreams and spirituality. Where you dissolve boundaries.",
    "Pluto": "Your power and transformation. Where you undergo metamorphosis.",
    "Chiron": "Your deepest wound and your power to heal.",
    "North Node": "Your destiny and evolutionary path."
}

HOUSE_THEMES = {
    "1": "The House of Self. Appearance, vitality, and first impressions.",
    "2": "The House of Value. Personal resources, money, and self-worth.",
    "3": "The House of Mind. Communication, siblings, and local environment.",
    "4": "The House of Home. Roots, ancestry, and emotional foundation.",
    "5": "The House of Joy. Creativity, romance, children, and play.",
    "6": "The House of Service. Daily work, health, and rituals.",
    "7": "The House of Others. Relationships, contracts, and open enemies.",
    "8": "The House of Transformation. Intimacy, shared resources, and death/rebirth.",
    "9": "The House of Spirit. Philosophy, long travel, and higher mind.",
    "10": "The House of Reputation. Career, public standing, and legacy.",
    "11": "The House of Community. Friends, groups, and future hopes.",
    "12": "The House of Secrets. The unconscious, isolation, and spiritual transcendence."
}

def generate_sign_content(planet, sign):
    theme = PLANET_THEMES.get(planet, "Planetary influence")
    s_data = SIGNS_DATA[sign]
    
    text = f"{theme} Expressed through the lens of {sign}: {s_data['essence']}."
    if planet == "Sun":
        text += f" You identify as {s_data['archetype']}. Your path involves mastering {s_data['keywords'][0]} and {s_data['keywords'][1]}."
    elif planet == "Moon":
        text += f" You find safety in {s_data['keywords'][2]} and react with {s_data['keywords'][0]}. Your emotional self is {s_data['archetype']}."

    return {
        "text": text,
        "archetype": s_data['archetype'],
        "essence": s_data['essence'],
        "shadow": f"{planet} expressed as {s_data['shadow']}",
        "gift": s_data['gift'],
        "keywords": s_data['keywords']
    }

def generate_house_content(planet, house):
    h_theme = HOUSE_THEMES.get(house, "Life Area")
    p_theme = PLANET_THEMES.get(planet, "Planetary energy")
    
    return {
        "text": f"{planet} in House {house}. {p_theme} Focused on {h_theme}.",
        "archetype": f"{planet} of the {house}th House",
        "essence": f"Focusing {planet} energy into {h_theme}",
        "shadow": f"Over-identification with {house}th house matters; neglecting other areas.",
        "gift": f"Mastery of {house}th house affairs through {planet}."
    }

DATA_DIR = Path("src/pillars/astrology/data/interpretations")

def populate_signs():
    path = DATA_DIR / "planets_in_signs.json"
    with open(path, "r") as f:
        data = json.load(f)
        
    for planet in PLANET_THEMES.keys():
        if planet not in data:
            data[planet] = {}
        for sign in SIGNS_DATA.keys():
             # Only overwrite if empty or simple scaffold
             current = data[planet].get(sign)
             if not current or (isinstance(current, dict) and not current.get("text")):
                 data[planet][sign] = generate_sign_content(planet, sign)
                 
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    print("Populated Signs.")

def populate_houses():
    path = DATA_DIR / "planets_in_houses.json"
    with open(path, "r") as f:
        data = json.load(f)
        
    for planet in PLANET_THEMES.keys():
        if planet not in data:
            data[planet] = {}
        for i in range(1, 13):
            house = str(i)
            current = data[planet].get(house)
            if not current or (isinstance(current, dict) and not current.get("text")):
                data[planet][house] = generate_house_content(planet, house)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    print("Populated Houses.")

if __name__ == "__main__":
    populate_signs()
    populate_houses()
