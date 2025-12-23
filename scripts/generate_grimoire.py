
import os
import csv
import json
import collections

def generate_grimoire():
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    docs_dir = os.path.join(project_root, "Docs", "adyton_walls")
    
    metrics_path = os.path.join(docs_dir, "constellation_metrics.csv")
    shapes_path = os.path.join(docs_dir, "constellation_shapes.json")
    out_path = os.path.join(docs_dir, "The_Book_of_91_Stars.md")
    
    # Load Data
    with open(shapes_path, 'r') as f:
        shapes = json.load(f)
        
    metrics = []
    with open(metrics_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            metrics.append(row)
            
    # --- Shape Identification Logic ---
    # Invert Dictionary to find duplicates: ShapeStr -> List of IDs
    shape_to_ids = collections.defaultdict(list)
    for sid, shape_str in shapes.items():
        shape_to_ids[shape_str].append(sid)
        
    # Assign Names to Shapes
    # Heuristic Naming map (Human-in-the-loop simulation)
    # We can try to guess names for common shapes, or just index them.
    # Given the user wants "Art", let's give them "Form I, Form II" etc.
    # But better: Use the ASCII to check dimensions
    
    sorted_shapes = sorted(shape_to_ids.keys(), key=lambda k: len(shape_to_ids[k]), reverse=True)
    
    shape_registry = {} # ShapeStr -> {Name, Description, Count}
    
    roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", 
                      "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]
                      
    for i, shape_str in enumerate(sorted_shapes):
        count = len(shape_to_ids[shape_str])
        
        # Auto-naming based on dimensions
        lines = shape_str.split('\n')
        h = len(lines)
        w = max(len(l) for l in lines)
        
        name = f"Form {i+1}"
        desc = f"{h}x{w} Lattice"
        
        # Specific overrides for common/recognizable shapes (based on view_file data)
        if shape_str.count("■") == 8: # All refer to 8 cells
            if h == 5 and w == 2: desc = "The Pillar"
            if h == 2 and w == 5: desc = "The Beam"
            if h == 4 and w == 2: desc = "The High Seat"
            if h == 3 and w == 3: 
                if lines[0] == "■■■" and lines[1] == "■■■": desc = "The Tablet"
                
        shape_registry[shape_str] = {
            "ID": i+1,
            "Name": name,
            "Desc": desc,
            "Count": count
        }

    # Generate MD
    md_lines = []
    md_lines.append("# The Book of 91 Stars")
    md_lines.append("## A Grimoire of the Adyton Constellations")
    md_lines.append("")
    md_lines.append("> *\"Every shape is a word; every form is a story.\"*")
    md_lines.append("")
    
    # --- The Legend ---
    md_lines.append("## The Common Forms (The Legend)")
    md_lines.append("Some shapes echo across the walls. These are the resonant archetypes.")
    md_lines.append("")
    
    # List top 10 most common
    for i, shape_str in enumerate(sorted_shapes):
        if i >= 10: break # Only show top 10 in legend
        
        meta = shape_registry[shape_str]
        count = meta['Count']
        if count < 2: break # Don't show unique ones in Legend
        
        md_lines.append(f"### {meta['Name']}: {meta['Desc']}")
        md_lines.append(f"**Appears {count} times**")
        md_lines.append("```")
        md_lines.append(shape_str)
        md_lines.append("```")
        md_lines.append(f"*Found in: {', '.join(shape_to_ids[shape_str])}*")
        md_lines.append("")

    md_lines.append("---")
    
    current_wall = ""
    
    for row in metrics:
        wall = row['Wall']
        gid = row['GroupID']
        # s_val = row['Sum'] # NOT USED
        
        # New Wall Section
        if wall != current_wall:
            current_wall = wall
            md_lines.append(f"\n## {wall.upper()}")
            md_lines.append("---")
            
        # Get Shape
        shape_key = f"{wall}_{gid}"
        shape_ascii = shapes.get(shape_key, "No Shape")
        
        meta = shape_registry.get(shape_ascii, {"Name": "Unknown", "Desc": "Unique"})
        
        # Format Card
        md_lines.append(f"### {wall} #{gid}: {meta['Desc']}")
        # Removed Gematria Line
        md_lines.append("")
        md_lines.append("```")
        md_lines.append(shape_ascii)
        md_lines.append("```")
        md_lines.append(f"**Name:** ______________")
        md_lines.append(f"**Mythos:** (Enter the story of the {meta['Desc']})")
        md_lines.append("")
        
    with open(out_path, 'w') as f:
        f.write("\n".join(md_lines))
        
    print(f"Grimoire generated at {out_path}")
if __name__ == "__main__": generate_grimoire()
