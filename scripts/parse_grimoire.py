
import os
import re
import json

def parse_grimoire():
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    grimoire_path = os.path.join(project_root, "Docs", "adyton_walls", "The_Book_of_91_Stars.md")
    out_path = os.path.join(project_root, "src", "pillars", "adyton", "data", "constellation_mythos.json")
    
    # Ensure output dir exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    with open(grimoire_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Split by Wall
    # Regex to find "## WALLNAME"
    wall_sections = re.split(r'^##\s+(SUN|MERCURY|VENUS|MOON|MARS|JUPITER|SATURN)\s*$', content, flags=re.MULTILINE)
    
    # wall_sections[0] is intro.
    # wall_sections[1] is WallName1, wall_sections[2] is Content1, etc.
    
    data = {}
    
    for i in range(1, len(wall_sections), 2):
        wall_name = wall_sections[i].title() # Sun, Mercury...
        wall_content = wall_sections[i+1]
        
        print(f"Processing {wall_name}...")
        
        data[wall_name] = {}
        
        # Split by Constellation Card
        # Format: ### Wall #ID: Description
        card_pattern = r'^###\s+\w+\s+#(\d+):\s+.*$'
        cards = re.split(card_pattern, wall_content, flags=re.MULTILINE)
        
        # cards[0] is content before first card (usually '---')
        # cards[1] is ID, cards[2] is content. cards[3] is ID, cards[4] is content.
        
        for j in range(1, len(cards), 2):
            gid = int(cards[j])
            card_text = cards[j+1]
            
            # Extract Fields
            
            # Name
            name_match = re.search(r'\*\*Name:\*\*\s+(.*)', card_text)
            name = name_match.group(1).strip() if name_match else "Unknown"
            
            # Greek Key
            key_match = re.search(r'\*\*Greek Key:\*\*\s+(.*)', card_text)
            greek_key = key_match.group(1).strip() if key_match else ""
            
            # Mythos
            # Matches from **Mythos:** until **The Texture
            mythos_match = re.search(r'\*\*Mythos:\*\*\s+(.*?)\s+(?=\*\*The Texture|\Z)', card_text, re.DOTALL)
            mythos = mythos_match.group(1).strip() if mythos_match else ""
            
            # Texture
            texture_match = re.search(r'\*\*The Texture \(Visceral\):\*\*\s+(.*?)\s+(?=\*\*The Mantra|\Z)', card_text, re.DOTALL)
            texture = texture_match.group(1).strip() if texture_match else ""
            
            # Mantra
            mantra_match = re.search(r'\*\*The Mantra \(Invocation\):\*\*\s+> (.*?)\s+(?=\###|\Z)', card_text, re.DOTALL)
            # Mantra is usually in a blockquote >, strip the > if regex didn't catch it perfectly or if user edits
            mantra = mantra_match.group(1).strip() if mantra_match else ""
            if mantra.startswith('"') and mantra.endswith('"'):
                mantra = mantra[1:-1] # Remove surrounding quotes
                
            entry = {
                "Name": name,
                "GreekKey": greek_key,
                "Mythos": mythos,
                "Texture": texture,
                "Mantra": mantra
            }
            
            data[wall_name][str(gid)] = entry
            # print(f"  #{gid}: {name}")
            
    # Save JSON
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully parsed Grimoire to {out_path}")
    
if __name__ == "__main__":
    parse_grimoire()
