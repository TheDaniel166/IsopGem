"""
Generate The Catalog of Fixed Stars v2.0
- 41 Void Stars distributed across 7 walls (5-6 per wall)
- 63 Seed Stars (some shared between walls)
- Each star gets: Name, Etymology, Nature, Whisper, Decimal Value
"""

import json
import os
import random
from collections import defaultdict

# Mythical name pools
VOID_NAME_ROOTS = [
    "Sheol", "Tehom", "Tohu", "Bohu", "Mavet", "Abaddon", "Gehenna", "Dumah",
    "Erebos", "Nyx", "Thanatos", "Hypnos", "Lethe", "Styx", "Acheron", "Cocytus",
    "Tartarus", "Chaos", "Chronos", "Ananke", "Moira", "Duat", "Ammit", "Apep", 
    "Nun", "Neith", "Nephthys", "Nigredo", "Mortificatio", "Putrefactio", 
    "Calcinatio", "Separatio", "Vacuum", "Silentium", "Umbra", "Tenebrae", 
    "Abyssus", "Kenoma", "Saklas", "Samael", "Yaldabaoth", "Hyle"
]

SEED_NAME_ROOTS = [
    "Kether", "Chokmah", "Binah", "Chesed", "Geburah", "Tiphareth",
    "Netzach", "Hod", "Yesod", "Malkuth", "Daath", "Helios", "Selene", 
    "Eos", "Phosphoros", "Hesperos", "Aether", "Nous", "Logos", "Psyche", 
    "Sophia", "Pneuma", "Dynamis", "Archai", "Theos", "Ouranos", "Gaia", 
    "Eros", "Ra", "Thoth", "Isis", "Osiris", "Horus", "Maat", "Ptah",
    "Aten", "Amun", "Sekhmet", "Khepri", "Hathor", "Albedo", "Rubedo", 
    "Citrinitas", "Quintessentia", "Azoth", "Lux", "Sol", "Luna", "Stella", 
    "Ignis", "Aqua", "Terra", "Aer", "Aurum", "Argentum", "Ferrum", "Cuprum",
    "Barbelo", "Autogenes", "Pleroma", "Syzygos", "Bythos", "Aletheia",
    "Ennoia", "Anthropos", "Ecclesia", "Zoe", "Pistis"
]

ETYMOLOGY_LANGS = {
    "Sheol": ("Hebrew", "The Pit, Underworld"),
    "Tehom": ("Hebrew", "The Deep, Primordial Waters"),
    "Tohu": ("Hebrew", "Formlessness, Chaos"),
    "Bohu": ("Hebrew", "Emptiness, Void"),
    "Mavet": ("Hebrew", "Death"),
    "Abaddon": ("Hebrew", "Destruction, The Destroyer"),
    "Gehenna": ("Hebrew", "Valley of Hinnom, Hell"),
    "Dumah": ("Hebrew", "Silence, Stillness"),
    "Erebos": ("Greek", "Deep Darkness, Shadow"),
    "Nyx": ("Greek", "Night, Primordial Darkness"),
    "Thanatos": ("Greek", "Death Personified"),
    "Hypnos": ("Greek", "Sleep, Slumber"),
    "Lethe": ("Greek", "Forgetfulness, Oblivion"),
    "Styx": ("Greek", "The River of Hate"),
    "Acheron": ("Greek", "River of Woe"),
    "Cocytus": ("Greek", "River of Lamentation"),
    "Tartarus": ("Greek", "The Abyss, Deepest Pit"),
    "Chaos": ("Greek", "The Primordial Void"),
    "Chronos": ("Greek", "Time, Saturn"),
    "Ananke": ("Greek", "Necessity, Fate"),
    "Moira": ("Greek", "Destiny, Portion"),
    "Duat": ("Egyptian", "The Underworld, Realm of Osiris"),
    "Ammit": ("Egyptian", "Devourer of the Dead"),
    "Apep": ("Egyptian", "Serpent of Chaos"),
    "Nun": ("Egyptian", "Primordial Waters"),
    "Neith": ("Egyptian", "Weaver of Fate"),
    "Nephthys": ("Egyptian", "Lady of the House"),
    "Nigredo": ("Latin/Alchemical", "Blackening, Putrefaction"),
    "Mortificatio": ("Latin/Alchemical", "Death of the Old Self"),
    "Putrefactio": ("Latin/Alchemical", "Decomposition"),
    "Calcinatio": ("Latin/Alchemical", "Calcination, Burning"),
    "Separatio": ("Latin/Alchemical", "Separation of Elements"),
    "Vacuum": ("Latin", "Empty Space, Void"),
    "Silentium": ("Latin", "Silence"),
    "Umbra": ("Latin", "Shadow"),
    "Tenebrae": ("Latin", "Darkness"),
    "Abyssus": ("Latin", "The Abyss"),
    "Kenoma": ("Gnostic", "The Empty Realm"),
    "Saklas": ("Gnostic", "The Fool, Blind God"),
    "Samael": ("Gnostic/Hebrew", "Poison of God, Blind One"),
    "Yaldabaoth": ("Gnostic", "Child of Chaos"),
    "Hyle": ("Gnostic/Greek", "Matter, Base Substance"),
    "Kether": ("Hebrew/Kabbalistic", "The Crown"),
    "Chokmah": ("Hebrew/Kabbalistic", "Wisdom"),
    "Binah": ("Hebrew/Kabbalistic", "Understanding"),
    "Chesed": ("Hebrew/Kabbalistic", "Mercy, Loving-kindness"),
    "Geburah": ("Hebrew/Kabbalistic", "Severity, Strength"),
    "Tiphareth": ("Hebrew/Kabbalistic", "Beauty, Harmony"),
    "Netzach": ("Hebrew/Kabbalistic", "Victory, Eternity"),
    "Hod": ("Hebrew/Kabbalistic", "Glory, Splendor"),
    "Yesod": ("Hebrew/Kabbalistic", "Foundation"),
    "Malkuth": ("Hebrew/Kabbalistic", "Kingdom, Manifestation"),
    "Daath": ("Hebrew/Kabbalistic", "Knowledge, The Abyss"),
    "Helios": ("Greek", "The Sun God"),
    "Selene": ("Greek", "The Moon Goddess"),
    "Eos": ("Greek", "The Dawn"),
    "Phosphoros": ("Greek", "Light-Bearer, Morning Star"),
    "Hesperos": ("Greek", "Evening Star"),
    "Aether": ("Greek", "Upper Air, Pure Fire"),
    "Nous": ("Greek", "Divine Mind, Intellect"),
    "Logos": ("Greek", "Word, Reason, Divine Order"),
    "Psyche": ("Greek", "Soul, Breath"),
    "Sophia": ("Greek", "Wisdom"),
    "Pneuma": ("Greek", "Spirit, Breath"),
    "Dynamis": ("Greek", "Power, Potential"),
    "Archai": ("Greek", "First Principles, Rulers"),
    "Theos": ("Greek", "God, Divine"),
    "Ouranos": ("Greek", "Heaven, Sky"),
    "Gaia": ("Greek", "Earth Mother"),
    "Eros": ("Greek", "Love, Desire"),
    "Ra": ("Egyptian", "The Sun God"),
    "Thoth": ("Egyptian", "God of Wisdom and Writing"),
    "Isis": ("Egyptian", "Great Mother, Magic"),
    "Osiris": ("Egyptian", "God of the Underworld"),
    "Horus": ("Egyptian", "Sky God, Kingship"),
    "Maat": ("Egyptian", "Truth, Justice, Order"),
    "Ptah": ("Egyptian", "Creator God, Craftsman"),
    "Aten": ("Egyptian", "The Sun Disk"),
    "Amun": ("Egyptian", "The Hidden One"),
    "Sekhmet": ("Egyptian", "Lion Goddess of War"),
    "Khepri": ("Egyptian", "Scarab, Rising Sun"),
    "Hathor": ("Egyptian", "Goddess of Love and Sky"),
    "Albedo": ("Latin/Alchemical", "Whitening, Purification"),
    "Rubedo": ("Latin/Alchemical", "Reddening, Completion"),
    "Citrinitas": ("Latin/Alchemical", "Yellowing, Awakening"),
    "Quintessentia": ("Latin/Alchemical", "Fifth Element, Spirit"),
    "Azoth": ("Alchemical", "Universal Solvent"),
    "Lux": ("Latin", "Light"),
    "Sol": ("Latin", "The Sun"),
    "Luna": ("Latin", "The Moon"),
    "Stella": ("Latin", "Star"),
    "Ignis": ("Latin", "Fire"),
    "Aqua": ("Latin", "Water"),
    "Terra": ("Latin", "Earth"),
    "Aer": ("Latin", "Air"),
    "Aurum": ("Latin", "Gold"),
    "Argentum": ("Latin", "Silver"),
    "Ferrum": ("Latin", "Iron"),
    "Cuprum": ("Latin", "Copper"),
    "Barbelo": ("Gnostic", "First Thought, Divine Feminine"),
    "Autogenes": ("Gnostic", "Self-Generated, The Son"),
    "Pleroma": ("Gnostic", "Fullness, Divine Realm"),
    "Syzygos": ("Gnostic", "Consort, Divine Pair"),
    "Bythos": ("Gnostic", "The Depth, First Principle"),
    "Aletheia": ("Gnostic/Greek", "Truth"),
    "Ennoia": ("Gnostic", "Thought, Intent"),
    "Anthropos": ("Gnostic/Greek", "Primal Human"),
    "Ecclesia": ("Gnostic/Greek", "Assembly, Church"),
    "Zoe": ("Gnostic/Greek", "Life"),
    "Pistis": ("Gnostic/Greek", "Faith"),
}

PLANETS = ["Sun", "Mercury", "Venus", "Moon", "Mars", "Jupiter", "Saturn"]
PLANET_SYMBOLS = {"Sun": "☉", "Mercury": "☿", "Venus": "♀", "Moon": "☽", 
                  "Mars": "♂", "Jupiter": "♃", "Saturn": "♄"}

def load_lattices():
    path = "/home/burkettdaniel927/projects/isopgem/src/pillars/mods/data/planetary_lattices.json"
    with open(path, 'r') as f:
        return json.load(f)

def load_wall_values():
    """Load numeric values for each wall."""
    values = {}
    wall_files = {
        "Sun": "sun_wall.csv",
        "Mercury": "mercury_wall.csv", 
        "Venus": "venus_wall.csv",
        "Moon": "luna_wall.csv",
        "Mars": "mars_wall.csv",
        "Jupiter": "jupiter_wall.csv",
        "Saturn": "saturn_wall.csv"
    }
    base_path = "/home/burkettdaniel927/projects/isopgem/Docs/adyton_walls"
    
    for planet, filename in wall_files.items():
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            grid = []
            with open(filepath, 'r') as f:
                import csv
                reader = csv.reader(f)
                for row in reader:
                    grid.append([int(x) for x in row if x.strip()])
            values[planet] = grid
    return values

def calculate_seeds(lattice):
    """Calculate seed coordinates for a planetary lattice."""
    groups = defaultdict(list)
    for r in range(8):
        for c in range(13):
            gid = lattice[r][c]
            groups[gid].append((r, c))
    
    seeds = {}
    for gid in range(13):
        cells = groups.get(gid, [])
        if not cells:
            continue
        avg_r = sum(r for r, c in cells) / len(cells)
        avg_c = sum(c for r, c in cells) / len(cells)
        min_dist = float('inf')
        seed = cells[0]
        for r, c in cells:
            dist = (r - avg_r) ** 2 + (c - avg_c) ** 2
            if dist < min_dist:
                min_dist = dist
                seed = (r, c)
        seeds[gid] = seed
    return seeds

def find_void_and_seed_coords(lattices):
    """Find all void coords and all seed coords."""
    all_seeds = set()
    seed_by_planet = {}
    
    for planet in PLANETS:
        seeds = calculate_seeds(lattices[planet])
        seed_by_planet[planet] = seeds
        for gid, coord in seeds.items():
            all_seeds.add(coord)
    
    all_cells = set((r, c) for r in range(8) for c in range(13))
    void_coords = sorted(all_cells - all_seeds)
    
    return void_coords, all_seeds, seed_by_planet

def distribute_voids_to_walls(void_coords):
    """Distribute 41 void coords evenly across 7 walls (6,6,6,6,6,6,5)."""
    # Shuffle for variety
    shuffled = void_coords.copy()
    random.shuffle(shuffled)
    
    distribution = {p: [] for p in PLANETS}
    counts = [6, 6, 6, 6, 6, 6, 5]  # 41 total
    
    idx = 0
    for i, planet in enumerate(PLANETS):
        for _ in range(counts[i]):
            if idx < len(shuffled):
                distribution[planet].append(shuffled[idx])
                idx += 1
    
    return distribution

def generate_name(used_names, roots, is_void=False):
    """Generate a unique mythical name."""
    suffixes = ["Prima", "Posterior", "Profunda", "Aeterna", "Silens",
                "Ultima", "Perpetua", "Immota", "Fixa", "Occulta",
                "Rex", "Regina", "Magus", "Alpha", "Arche", "Sanctus",
                "", "", "", ""]
    
    for _ in range(100):
        root = random.choice(roots)
        if random.random() < 0.5:
            suffix = random.choice(suffixes)
            name = f"{root} {suffix}".strip() if suffix else root
        else:
            name = root
        
        if name not in used_names:
            used_names.add(name)
            return name
    
    return f"{root}-{len(used_names)}"

def get_etymology(name):
    """Get etymology for a name."""
    root = name.split()[0] if " " in name else name
    if root in ETYMOLOGY_LANGS:
        lang, meaning = ETYMOLOGY_LANGS[root]
        return f"{lang} *{root}* ({meaning})"
    return f"Ancient *{root}*"

def generate_void_nature():
    """Generate nature description for a void star."""
    templates = [
        "A cell of eternal stillness. It anchors the Temple to the bedrock of non-being.",
        "The star of silence. Here, thought dissolves into primordial emptiness.",
        "A fixed point in the Altar of 287. It holds space for what cannot be named.",
        "A drain in the fabric of manifestation. Energy flows into it and is transformed.",
        "The anchor of void. It reminds the Adept that emptiness is the mother of form.",
        "A still point in the turning wheel. It neither gives nor takes, but holds.",
        "The star of pause. Between two breaths, this coordinate exists.",
    ]
    return random.choice(templates)

def generate_seed_nature(planet, gid, depth):
    """Generate nature description for a seed star."""
    depth_desc = ""
    if depth >= 4:
        depth_desc = "A nexus of immense power, seeding multiple realms simultaneously. "
    elif depth >= 2:
        depth_desc = "A shared seed, its influence spanning multiple walls. "
    
    templates = [
        f"{depth_desc}The heart of Constellation #{gid}. From this point, the pattern unfolds.",
        f"{depth_desc}The generative center of Constellation #{gid}. All lines trace back to this origin.",
        f"{depth_desc}The seed from which Constellation #{gid} grows. It pulses with {planet}'s essence.",
        f"{depth_desc}The geometric center of Constellation #{gid}. The algorithm begins here.",
    ]
    return random.choice(templates)

def generate_void_whisper():
    return random.choice([
        "*\"I am the pause. I am the space. In me, all things find rest.\"*",
        "*\"Silence. Stillness. The Altar awaits your offering.\"*",
        "*\"I hold nothing. I am nothing. Yet without me, nothing stands.\"*",
        "*\"Sink into me. Release. The Void embraces all.\"*",
        "*\"Before form, I was. After form, I remain.\"*",
    ])

def generate_seed_whisper(planet):
    planet_whispers = {
        "Sun": "*\"I ignite. I radiate. From my center, the world is born.\"*",
        "Mercury": "*\"I connect. I transmit. Through me, the message flows.\"*",
        "Venus": "*\"I attract. I harmonize. Beauty grows from my heart.\"*",
        "Moon": "*\"I reflect. I remember. The tides obey my pulse.\"*",
        "Mars": "*\"I forge. I defend. Strength radiates from my core.\"*",
        "Jupiter": "*\"I expand. I bless. Abundance flows from my throne.\"*",
        "Saturn": "*\"I bind. I limit. Structure crystallizes around me.\"*",
    }
    return planet_whispers.get(planet, "*\"I am the Seed. The Pattern grows from me.\"*")

def generate_catalog():
    """Generate the full star catalog."""
    random.seed(441)
    
    lattices = load_lattices()
    wall_values = load_wall_values()
    void_coords, all_seeds, seed_by_planet = find_void_and_seed_coords(lattices)
    void_distribution = distribute_voids_to_walls(list(void_coords))
    
    # Count seed depth (how many walls share each seed position)
    seed_depth = defaultdict(list)
    for planet, seeds in seed_by_planet.items():
        for gid, coord in seeds.items():
            seed_depth[coord].append(planet)
    
    used_names = set()
    catalog = {"walls": {}}
    
    for planet in PLANETS:
        catalog["walls"][planet] = {
            "symbol": PLANET_SYMBOLS[planet],
            "seeds": [],
            "voids": []
        }
        
        # Generate Seed Stars for this wall
        seeds = seed_by_planet[planet]
        for gid in range(13):
            if gid not in seeds:
                continue
            r, c = seeds[gid]
            
            # Get decimal value
            decimal = 0
            if planet in wall_values and r < len(wall_values[planet]):
                decimal = wall_values[planet][r][c]
            
            depth = len(seed_depth[(r, c)])
            name = generate_name(used_names, SEED_NAME_ROOTS)
            
            catalog["walls"][planet]["seeds"].append({
                "constellation_id": gid,
                "coordinate": [r, c],
                "name": name,
                "decimal": decimal,
                "depth": depth,
                "shared_with": seed_depth[(r, c)],
                "etymology": get_etymology(name),
                "nature": generate_seed_nature(planet, gid, depth),
                "whisper": generate_seed_whisper(planet)
            })
        
        # Generate Void Stars for this wall
        for r, c in sorted(void_distribution[planet]):
            decimal = 0
            if planet in wall_values and r < len(wall_values[planet]):
                decimal = wall_values[planet][r][c]
            
            name = generate_name(used_names, VOID_NAME_ROOTS, is_void=True)
            
            catalog["walls"][planet]["voids"].append({
                "coordinate": [r, c],
                "name": name,
                "decimal": decimal,
                "etymology": get_etymology(name),
                "nature": generate_void_nature(),
                "whisper": generate_void_whisper()
            })
    
    return catalog

def write_markdown(catalog):
    """Write the catalog as Markdown."""
    output = "/home/burkettdaniel927/projects/isopgem/Docs/adyton_walls/The_Catalog_of_Fixed_Stars.md"
    
    lines = [
        "# The Catalog of Fixed Stars",
        "> *\"Each Star has a Name. Each Name has Power.\"*",
        "",
        "This catalog names the **104 Fixed Stars** of the Adyton — organized by Wall.",
        "Each wall contains **13 Seed Stars** (hearts of constellations) and **5-6 Void Stars** (the Empty Net).",
        "",
        "---",
        ""
    ]
    
    for planet in PLANETS:
        wall = catalog["walls"][planet]
        lines.append(f"## {wall['symbol']} {planet} Wall")
        lines.append("")
        
        # Seed Stars
        lines.append("### Seed Stars (Hearts of Constellations)")
        lines.append("")
        
        for star in wall["seeds"]:
            r, c = star["coordinate"]
            lines.append(f"#### {star['name']}")
            lines.append(f"**Coord:** ({r},{c}) | **Const.:** #{star['constellation_id']} | **Decimal:** {star['decimal']} | **Depth:** {star['depth']}")
            lines.append(f"**Etymology:** {star['etymology']}")
            lines.append(f"**Nature:** {star['nature']}")
            lines.append(f"**Whisper:** {star['whisper']}")
            lines.append("")
        
        # Void Stars
        lines.append("### Void Stars (The Empty Net)")
        lines.append("")
        
        for star in wall["voids"]:
            r, c = star["coordinate"]
            lines.append(f"#### {star['name']}")
            lines.append(f"**Coord:** ({r},{c}) | **Decimal:** {star['decimal']}")
            lines.append(f"**Etymology:** {star['etymology']}")
            lines.append(f"**Nature:** {star['nature']}")
            lines.append(f"**Whisper:** {star['whisper']}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    lines.append("> *\"The Stars are Fixed. The Magus moves among them.\"*")
    
    with open(output, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"Markdown written to: {output}")

def write_json(catalog):
    """Write the catalog as JSON."""
    output = "/home/burkettdaniel927/projects/isopgem/src/pillars/adyton/data/star_catalog.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)
    print(f"JSON written to: {output}")

if __name__ == "__main__":
    catalog = generate_catalog()
    write_markdown(catalog)
    write_json(catalog)
    
    # Stats
    total_seeds = sum(len(w["seeds"]) for w in catalog["walls"].values())
    total_voids = sum(len(w["voids"]) for w in catalog["walls"].values())
    print(f"\nGenerated: {total_seeds} Seed Stars, {total_voids} Void Stars")
    print(f"Total: {total_seeds + total_voids} Fixed Stars across 7 walls")
