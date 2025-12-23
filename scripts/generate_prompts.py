
import json
import os

def generate_prompts():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    json_path = os.path.join(project_root, "src/pillars/adyton/data/constellation_mythos.json")
    out_path = os.path.join(project_root, "Docs/adyton_walls/The_Book_of_Prompts.md")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    lines = []
    lines.append("# The Book of VISCERAL PROMPTS (Nano Banana Pro Edition)")
    lines.append("> *\"Instruction Manual for the Astral Camera\"*")
    lines.append("")
    lines.append("These prompts are optimized for high-fidelity generative AI (specifically tailored for `Nano Banana Pro` syntax).")
    lines.append("They focus on **Materiality**, **Lighting**, **Scent-as-Visual**, and **Hyper-Realism**.")
    lines.append("")
    lines.append("---")
    
    planets = ["Sun", "Mercury", "Venus", "Moon", "Mars", "Jupiter", "Saturn"]
    
    # Planet Styling Definitions
    planet_styles = {
        "Sun": {
            "Border": "intricate Gold and Vitrified Amber Art Nouveau border",
            "Background": "deep golden cosmic nebula with rays of dawn light",
            "Atmosphere": "radiant, majestic, solar, sacred geometry"
        },
        "Mercury": {
            "Border": "fluid Quicksilver and Electrum filigree border",
            "Background": "shifting violet and teal data-streams in a void",
            "Atmosphere": "kinetic, glitch-art, hermetic, airy"
        },
        "Venus": {
            "Border": "ornate Copper and Rose Gold floral border",
            "Background": "soft pearlescent dawn sky with floating cherry blossoms",
            "Atmosphere": "romantic, soft-focus, harmonious, beautiful"
        },
        "Moon": {
            "Border": "tarnished Sterling Silver and Pearl inlay border",
            "Background": "dark midnight ocean reflecting a giant moon",
            "Atmosphere": "mysterious, aquatic, dream-like, subconscious"
        },
        "Mars": {
            "Border": "jagged Iron and Rusted Steel spiked border",
            "Background": "red smoky battlefield with embers drifting",
            "Atmosphere": "aggressive, intense, sharp, martial"
        },
        "Jupiter": {
            "Border": "massive Tin and Purple Enamel architectural border",
            "Background": "stormy electric blue skies with lightning",
            "Atmosphere": "regal, expansive, powerful, stormy"
        },
        "Saturn": {
            "Border": "heavy Lead and Black Iron geometric border",
            "Background": "absolute black void with a single cold star",
            "Atmosphere": "somber, ancient, silent, heavy, entropic"
        }
    }

    for planet in planets:
        if planet not in data: continue
        
        lines.append(f"## {planet.upper()} - The Tarot of {planet}")
        lines.append("---")
        
        style = planet_styles.get(planet, planet_styles["Sun"])
        constellations = data[planet]
        # Sort by ID
        sorted_ids = sorted(constellations.keys(), key=lambda x: int(x))
        
        for cid in sorted_ids:
            c_data = constellations[cid]
            name = c_data['Name']
            key = c_data['GreekKey'].split(' ')[0] # Extract just the Greek word
            texture = c_data['Texture']
            
            # Construct the Tarot Prompt
            nb_prompt = (
                f"**Prompt for {name}:**\n"
                f"> **Format:** A mystical Tarot Card design. **Border:** {style['Border']}. \n"
                f"> **Central Image:** A hyper-realistic depiction of **{name}**. The object is composed of: {texture} It is floating in the center. \n"
                f"> **Background:** {style['Background']}. \n"
                f"> **Typography:** The Greek word '**{key}**' is written at the *top* of the card in an ancient, glowing Hellenic font. "
                f"The English name '**{name}**' is written at the *bottom* in a fancy, magical serif font on a parchment scroll banner. \n"
                f"> **Style:** {style['Atmosphere']}, 8k resolution, cinematic lighting, octane render, highly detailed material textures."
            )
            
            lines.append(f"### {planet} #{cid}: {name}")
            lines.append(nb_prompt)
            lines.append("")
            
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
        
    print(f"Prompt Book generated at {out_path}")

if __name__ == "__main__":
    generate_prompts()
