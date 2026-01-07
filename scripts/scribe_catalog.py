import json
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "src" / "pillars" / "adyton" / "data"
DOCS_DIR = BASE_DIR / "Docs" / "adyton_walls"
CATALOG_FILE = DOCS_DIR / "The_Catalog_of_Fixed_Stars.md"

MYTHOS_FILE = DATA_DIR / "constellation_mythos.json"
STAR_CATALOG_FILE = DATA_DIR / "star_catalog.json"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_markdown(catalog, mythos):
    lines = []
    lines.append("# The Catalog of Fixed Stars")
    lines.append("> *\"The Points of Light from which the Mythos hangs.\"*")
    lines.append("")
    lines.append("This catalog defines the **104 Fixed Stars** (Coordinates) of the Adyton system.")
    lines.append("Unlike the Constellations (which are interpretative forms), these Stars are fixed mathematical points.")
    lines.append("They possess unique Gematria (Decimal Values) and act as the structural anchors of the Temple.")
    lines.append("")
    
    walls = ["Sun", "Mercury", "Venus", "Moon", "Mars", "Jupiter", "Saturn"]
    symbols = {
        "Sun": "☉", "Mercury": "☿", "Venus": "♀", "Moon": "☽",
        "Mars": "♂", "Jupiter": "♃", "Saturn": "♄"
    }

    for wall_name in walls:
        if wall_name not in catalog["walls"]:
            continue
            
        wall_data = catalog["walls"][wall_name]
        symbol = symbols.get(wall_name, "")
        
        lines.append(f"## {symbol} {wall_name} Wall")
        lines.append("")
        
        # Seeds
        seeds = wall_data.get("seeds", [])
        if seeds:
            lines.append("### Seed Stars")
            lines.append("| Star Name | Coord | Value | Etymology | Structural Role |")
            lines.append("|---|---|---|---|---|")
            
            for seed in seeds:
                name = seed.get("name", "Unknown")
                coord = f"({seed.get('coordinate')[0]},{seed.get('coordinate')[1]})"
                decimal = seed.get("decimal", 0)
                etymology = seed.get("etymology", "").replace("*", "") # efficient clean
                c_id = seed.get("constellation_id")
                
                # Structural Role
                depth = seed.get("depth", 1)
                shared = seed.get("shared_with", [])
                
                # Constellation Name Reference
                constellation_data = mythos.get(wall_name, {}).get(str(c_id), {})
                const_name = constellation_data.get("Name", f"C#{c_id}")
                
                role_parts = []
                role_parts.append(f"Anchor of **{const_name}**")
                if len(shared) > 1:
                    others = [w for w in shared if w != wall_name]
                    role_parts.append(f"Links to {', '.join(others)}")
                
                role = "<br>".join(role_parts)

                lines.append(f"| **{name}** | {coord} | **{decimal}** | {etymology} | {role} |")

            lines.append("")

        # Voids
        actual_voids = wall_data.get("void_stars") or wall_data.get("voids") or []
        if actual_voids:
            lines.append("### Void Stars")
            lines.append("| Void Name | Coord | Value | Etymology | Nature |")
            lines.append("|---|---|---|---|---|")
            
            for void in actual_voids:
                name = void.get("name", "Unknown")
                coord = f"({void.get('coordinate')[0]},{void.get('coordinate')[1]})"
                decimal = void.get("decimal", 0)
                etymology = void.get("etymology", "").replace("*", "")
                
                # Simplistic nature extraction or shortening
                nature = void.get("nature", "Static Void point.")
                if "anchor" in nature.lower():
                    short_nature = "Anchors the Empty Net"
                elif "still point" in nature.lower():
                    short_nature = "Still Point"
                elif "pause" in nature.lower():
                    short_nature = "The Pause"
                elif "silence" in nature.lower():
                    short_nature = "Silence"
                elif "drain" in nature.lower():
                    short_nature = "Entropy Drain"
                else:
                    short_nature = "Void State"

                lines.append(f"| **{name}** | {coord} | **{decimal}** | {etymology} | {short_nature} |")
            
            lines.append("")
        
        lines.append("---")
        lines.append("")

    return "\n".join(lines)

def main():
    if not MYTHOS_FILE.exists():
        print(f"Error: Mythos file not found at {MYTHOS_FILE}")
        return
    if not STAR_CATALOG_FILE.exists():
        print(f"Error: Catalog file not found at {STAR_CATALOG_FILE}")
        return

    mythos = load_json(MYTHOS_FILE)
    catalog = load_json(STAR_CATALOG_FILE)

    markdown = generate_markdown(catalog, mythos)

    with open(CATALOG_FILE, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    print(f"Successfully scribed {CATALOG_FILE}")

if __name__ == "__main__":
    main()
