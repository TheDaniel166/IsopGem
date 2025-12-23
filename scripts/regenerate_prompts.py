"""
Regenerate The Book of Prompts with improved formatting.
Key improvements:
1. Explicit portrait/vertical aspect ratio (2:3 or 9:16)
2. Planet-specific borders, backgrounds, and styles - derived from CARD HEADER
3. Enhanced material and texture descriptions
4. Cleaner typography instructions
5. Optimized quality keywords
"""

import re
import os

SOURCE_FILE = "/home/burkettdaniel927/projects/isopgem/Docs/adyton_walls/The_Book_of_Prompts.md"
OUTPUT_FILE = "/home/burkettdaniel927/projects/isopgem/Docs/adyton_walls/The_Book_of_Prompts_v2.md"

# Planetary theme definitions
PLANET_THEMES = {
    "SUN": {
        "border": "ornate Art Nouveau border of molten gold and amber flames, intricate filigree",
        "background": "celestial golden dawn, radiant solar corona, sacred geometry rays emanating from center",
        "style": "divine radiance, photorealistic, volumetric god rays, 8K UHD, masterwork oil painting, hyper-detailed textures"
    },
    "MERCURY": {
        "border": "fluid quicksilver and electrum filigree border, constantly shifting patterns, Hermetic sigils",
        "background": "infinite data-streams of violet and teal, neural network patterns, digital aether, glitch-art fractals",
        "style": "kinetic energy, iridescent surfaces, Hermetic symbolism, 8K UHD, cybernetic art nouveau, hyper-detailed textures"
    },
    "VENUS": {
        "border": "blooming rose vines and copper filigree, art nouveau curves, romantic flourishes, dove feathers",
        "background": "blushing pink and emerald nebulae, spiral galaxies of love, soft Venus light, rose petals drifting",
        "style": "sensual beauty, Pre-Raphaelite romanticism, 8K UHD, dreamy soft focus, masterwork oil painting"
    },
    "MOON": {
        "border": "silver lunar phases and pearl filigree, oceanic waves, mother-of-pearl inlay, crescent motifs",
        "background": "deep indigo night sky, silver moonbeams, reflective waters, astral mist, tidal patterns",
        "style": "ethereal luminescence, dreamlike quality, tidal symbolism, 8K UHD, watercolor fantasy, hyper-detailed textures"
    },
    "MARS": {
        "border": "iron and bronze war insignia, angular geometric patterns, blood-red enamel, sword and shield motifs",
        "background": "volcanic crimson nebulae, forge fires, battlefield smoke, iron oxide dust, molten metal rivers",
        "style": "fierce intensity, heroic realism, 8K UHD, dramatic chiaroscuro, hyper-detailed textures"
    },
    "JUPITER": {
        "border": "royal purple velvet and gold leaf, thunderbolts, oak leaves, imperial eagles, crown motifs",
        "background": "majestic purple and gold storm clouds, lightning arcs, throne room grandeur, celestial temple",
        "style": "regal majesty, baroque opulence, 8K UHD, palatial grandeur, masterwork oil painting"
    },
    "SATURN": {
        "border": "heavy lead and obsidian, geometric patterns, hourglass motifs, skeletal hands, scythe blades",
        "background": "infinite void black, cold starlight, crystalline time fractals, entropy patterns, frozen cosmos",
        "style": "grave solemnity, memento mori, 8K UHD, chiaroscuro darkness, hyper-detailed textures"
    }
}

def normalize_planet(name):
    """Normalize planet name to uppercase key."""
    name_upper = name.upper().strip()
    if name_upper in PLANET_THEMES:
        return name_upper
    return "SUN"  # default fallback

def create_improved_prompt(planet, english_name, greek_key, texture_description):
    """Create an improved prompt with portrait orientation and enhanced structure."""
    
    theme = PLANET_THEMES.get(planet, PLANET_THEMES["SUN"])
    
    prompt = f'''**Prompt for {english_name}:**
> **Composition:** Vertical portrait composition (2:3 aspect ratio), traditional Tarot card format. Single mystical artifact centered in frame.
> **Border Frame:** {theme["border"]}, framing the entire card.
> **Central Subject:** A hyper-realistic, three-dimensional rendering of the sacred artifact called **{english_name}**. {texture_description} The artifact floats majestically at the center of the card, softly illuminated from above, casting subtle shadows.
> **Background:** {theme["background"]}, creating depth behind the central artifact.
> **Typography - Top:** The Greek word '**{greek_key}**' inscribed in an ancient, luminous Hellenic font at the card's crown, carved as if in stone or metal.
> **Typography - Bottom:** The English title '**{english_name}**' elegantly displayed on an ornate parchment scroll banner at the card's base, rendered in a mystical serif typeface.
> **Technical:** {theme["style"]}, cinematic lighting, Octane render, physically-based materials, museum-quality detail.'''
    
    return prompt

def parse_and_regenerate():
    """Parse existing prompts and regenerate with improved format."""
    
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # New document header
    new_content = """# The Book of VISCERAL PROMPTS (Tarot Edition v2.0)
> *"Instruction Manual for the Astral Camera"*

These prompts are optimized for high-fidelity generative AI image generation.
They feature **portrait orientation (2:3 aspect ratio)** for authentic Tarot card formatting.

**Key Features:**
- Explicit vertical/portrait composition
- Planet-specific borders, backgrounds, and styles
- Enhanced material and texture descriptions
- Cleaner typography placement instructions
- Optimized quality keywords

---
"""
    
    # Parse line by line
    lines = content.split('\n')
    current_section_planet = None
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for planet section header (## SUN - The Tarot of Sun)
        section_match = re.match(r'^## (SUN|MERCURY|VENUS|MOON|MARS|JUPITER|SATURN)\b', line, re.IGNORECASE)
        if section_match:
            current_section_planet = normalize_planet(section_match.group(1))
            new_content += f"\n## {current_section_planet} - The Tarot of {current_section_planet.title()}\n---\n"
            i += 1
            # Skip the --- line if present
            if i < len(lines) and lines[i].strip() == '---':
                i += 1
            continue
        
        # Check for card header (### Planet #N: Name)
        # Extract planet from the card header itself, not from section
        card_match = re.match(r'^### (Sun|Mercury|Venus|Moon|Mars|Jupiter|Saturn) #(\d+): (.+)', line, re.IGNORECASE)
        if card_match:
            card_planet = normalize_planet(card_match.group(1))
            card_id = card_match.group(2)
            english_name = card_match.group(3).strip()
            
            # Collect the prompt block
            prompt_lines = []
            j = i + 1
            while j < len(lines) and not lines[j].startswith("### "):
                prompt_lines.append(lines[j])
                j += 1
            
            prompt_block = '\n'.join(prompt_lines)
            
            # Extract Greek key
            greek_match = re.search(r"Greek word '\*\*(.+?)\*\*'", prompt_block)
            greek_key = greek_match.group(1) if greek_match else "ΑΡΧΕΤΥΠΟΝ"
            
            # Extract texture description
            texture_match = re.search(r"The object is composed of: (.+?) It is floating", prompt_block, re.DOTALL)
            if texture_match:
                texture = texture_match.group(1).strip().replace('\n', ' ')
            else:
                texture = "A mystical artifact of ancient power."
            
            # Generate improved prompt using the CARD's planet, not section planet
            new_content += f"\n### {card_planet} #{card_id}: {english_name}\n"
            new_content += create_improved_prompt(card_planet, english_name, greek_key, texture)
            new_content += "\n"
            
            i = j
            continue
        
        i += 1
    
    # Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # Count cards per planet
    planet_counts = {}
    for planet in PLANET_THEMES.keys():
        count = new_content.count(f"### {planet} #")
        planet_counts[planet] = count
    
    print(f"Generated improved prompts: {OUTPUT_FILE}")
    print(f"Cards per planet: {planet_counts}")
    print(f"Total cards: {sum(planet_counts.values())}")
    print(f"Total lines: {len(new_content.split(chr(10)))}")

if __name__ == "__main__":
    parse_and_regenerate()
