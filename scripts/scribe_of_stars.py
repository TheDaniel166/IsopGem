#!/usr/bin/env python3
"""
The Scribe of Stars - Adyton Documentation Generator.

Reads the Constellation Mythos (Lore) and Shapes (Geometry),
generates high-quality SVG illuminations for each,
and compiles them into "The Book of 91 Stars" (HTML).

Algorithm:
1. Parse ASCII shapes from 'constellation_shapes.json'.
2. Calculate MST (Minimum Spanning Tree) for visual connections.
3. Render SVG strings using svgwrite.
4. Inject into HTML template with print-ready CSS.
"""
import json
import math
import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Set

try:
    import svgwrite
except ImportError:
    print("Error: 'svgwrite' is required. Run 'pip install svgwrite'.")
    sys.exit(1)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "Docs" / "adyton_walls"
DATA_DIR = PROJECT_ROOT / "src" / "pillars" / "adyton" / "data"
ASSETS_DIR = DOCS_DIR / "assets"
OUTPUT_HTML = DOCS_DIR / "The_Book_of_91_Stars.html"

# Files
MYTHOS_FILE = DATA_DIR / "constellation_mythos.json"
SHAPES_FILE = DOCS_DIR / "constellation_shapes.json"
LATTICE_FILE = PROJECT_ROOT / "src" / "pillars" / "mods" / "data" / "planetary_lattices.json"

# Visual Style
CELL_SIZE = 40
WALL_CELL_SIZE = 25  # Smaller cells for full wall view
MARGIN = 20
BG_COLOR = "#050505"  # Deep void
LINE_COLOR = "#D4AF37"  # Metallic Gold
NODE_COLOR = "#FFFFFF"  # Star White
NODE_SIZE = 6
WALL_NODE_SIZE = 4   # Smaller nodes for full wall view

def parse_shape_to_grid(ascii_shape: str) -> List[Tuple[int, int]]:
    """Convert unicode block string to list of (row, col) coordinates."""
    nodes = []
    rows = ascii_shape.strip().split('\n')
    for r, line in enumerate(rows):
        for c, char in enumerate(line):
            if char == "■":
                nodes.append((r, c))
    return nodes

def calculate_mst(nodes: List[Tuple[int, int]]) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    Kruskal/Prim's MST algorithm to connect star nodes.
    Returns list of edge tuples: ((r1,c1), (r2,c2)).
    """
    if len(nodes) < 2:
        return []

    # Simple Prim's implementation matching WallDesigner logic
    connected = set()
    connected.add(nodes[0])
    unconnected = set(nodes[1:])
    edges = []

    while unconnected:
        best_edge = None
        min_dist = float('inf')
        best_node = None
        source_node = None

        for u in connected:
            for v in unconnected:
                # Euclidean distance squared
                d = (u[0]-v[0])**2 + (u[1]-v[1])**2
                
                # Tie-breaker: Prefer orthogonal connections (dist=1)
                if d < min_dist:
                    min_dist = d
                    best_edge = (u, v)
                    best_node = v
                    source_node = u

        if best_edge:
            edges.append(best_edge)
            connected.add(best_node)
            unconnected.remove(best_node)
        else:
            # Should not happen for a single component
            if unconnected:
                # Force jump to next component
                next_node = list(unconnected)[0]
                connected.add(next_node)
                unconnected.remove(next_node)

    return edges

def render_svg(key: str, nodes: List[Tuple[int, int]], edges: List[Tuple[Tuple[int, int], Tuple[int, int]]]) -> str:
    """Generate SVG string for a constellation."""
    if not nodes:
        return ""

    # Determine bounds
    max_r = max(n[0] for n in nodes)
    max_c = max(n[1] for n in nodes)
    
    width = (max_c + 1) * CELL_SIZE + (MARGIN * 2)
    height = (max_r + 1) * CELL_SIZE + (MARGIN * 2)
    
    dwg = svgwrite.Drawing(size=(width, height))
    
    # Draw Edges
    for u, v in edges:
        x1 = MARGIN + u[1] * CELL_SIZE + (CELL_SIZE / 2)
        y1 = MARGIN + u[0] * CELL_SIZE + (CELL_SIZE / 2)
        x2 = MARGIN + v[1] * CELL_SIZE + (CELL_SIZE / 2)
        y2 = MARGIN + v[0] * CELL_SIZE + (CELL_SIZE / 2)
        
        dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke=LINE_COLOR, stroke_width=2))

    # Draw Nodes
    for r, c in nodes:
        cx = MARGIN + c * CELL_SIZE + (CELL_SIZE / 2)
        cy = MARGIN + r * CELL_SIZE + (CELL_SIZE / 2)
        
        dwg.add(dwg.circle(center=(cx, cy), r=NODE_SIZE, fill=BG_COLOR, stroke=LINE_COLOR, stroke_width=2))
        dwg.add(dwg.circle(center=(cx, cy), r=NODE_SIZE/2, fill=LINE_COLOR))

    return dwg.tostring()

def render_full_wall(wall_name: str, grid: List[List[int]]) -> str:
    """Generate SVG for the entire 13x8 wall grid."""
    if not grid:
        return ""
        
    rows = len(grid)
    cols = len(grid[0])
    
    width = (cols * WALL_CELL_SIZE) + (MARGIN * 2)
    height = (rows * WALL_CELL_SIZE) + (MARGIN * 2)
    
    dwg = svgwrite.Drawing(size=(width, height))
    
    # Optional: Draw faint grid background
    # for r in range(rows + 1):
    #     y = MARGIN + r * WALL_CELL_SIZE
    #     dwg.add(dwg.line(start=(MARGIN, y), end=(width-MARGIN, y), stroke="#222", stroke_width=1))
    # for c in range(cols + 1):
    #     x = MARGIN + c * WALL_CELL_SIZE
    #     dwg.add(dwg.line(start=(x, MARGIN), end=(x, height-MARGIN), stroke="#222", stroke_width=1))

    # Group cells by ID
    groups = {}
    for r in range(rows):
        for c in range(cols):
            gid = grid[r][c]
            if gid not in groups:
                 groups[gid] = []
            groups[gid].append((r, c))
            
    # For each group, calculate MST and draw
    for gid, nodes in groups.items():
        edges = calculate_mst(nodes)
        
        # Edges
        for u, v in edges:
            x1 = MARGIN + u[1] * WALL_CELL_SIZE + (WALL_CELL_SIZE / 2)
            y1 = MARGIN + u[0] * WALL_CELL_SIZE + (WALL_CELL_SIZE / 2)
            x2 = MARGIN + v[1] * WALL_CELL_SIZE + (WALL_CELL_SIZE / 2)
            y2 = MARGIN + v[0] * WALL_CELL_SIZE + (WALL_CELL_SIZE / 2)
            
            dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke=LINE_COLOR, stroke_width=1.5))

        # Nodes
        for r, c in nodes:
            cx = MARGIN + c * WALL_CELL_SIZE + (WALL_CELL_SIZE / 2)
            cy = MARGIN + r * WALL_CELL_SIZE + (WALL_CELL_SIZE / 2)
            
            dwg.add(dwg.circle(center=(cx, cy), r=WALL_NODE_SIZE, fill=BG_COLOR, stroke=LINE_COLOR, stroke_width=1.5))
            dwg.add(dwg.circle(center=(cx, cy), r=WALL_NODE_SIZE/2, fill=LINE_COLOR))
            
    return dwg.tostring()

def generate_entry_html(wall: str, const_id: str, data: Dict, svg_content: str) -> str:
    """Build the HTML block for a single constellation."""
    key = f"{wall}_{const_id}"
    name = data.get("Name", "Unknown")
    greek = data.get("GreekKey", "")
    mythos = data.get("Mythos", "").replace("\n", "<br>")
    texture = data.get("Texture", "")
    mantra = data.get("Mantra", "")

    return f"""
    <div class="constellation-entry">
        <div class="header">
            <span class="id-tag">{wall} {const_id}</span>
            <h2>{name}</h2>
            <div class="greek-key">{greek}</div>
        </div>
        
        <div class="visual-container">
            <div class="svg-wrapper">
                {svg_content}
            </div>
        </div>

        <div class="content">
            <div class="mythos">
                <h3>The Mythos</h3>
                <p>{mythos}</p>
            </div>
            
            <div class="attributes">
                <p><strong>Texture:</strong> {texture}</p>
                <div class="mantra">{mantra}</div>
            </div>
        </div>
        <hr class="separator"/>
    </div>
    """

def main():
    print("Reading data...")
    if not MYTHOS_FILE.exists():
        print(f"Error: Mythos file not found at {MYTHOS_FILE}")
        return
    if not SHAPES_FILE.exists():
        print(f"Error: Shapes file not found at {SHAPES_FILE}")
        return

    with open(MYTHOS_FILE, 'r') as f:
        mythos_db = json.load(f)
    
    with open(SHAPES_FILE, 'r') as f:
        shapes_db = json.load(f)

    lattice_db = {}
    if LATTICE_FILE.exists():
        with open(LATTICE_FILE, 'r') as f:
            lattice_db = json.load(f)
    else:
        print(f"Warning: Lattice file not found at {LATTICE_FILE}. Full maps will be skipped.")

    # HTML Header
    html_content = ["""
<!DOCTYPE html>
<html>
<head>
    <title>The Book of 91 Stars</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lato:wght@400;700&display=swap');
        
        body {
            background-color: #080808;
            color: #E0E0E0;
            font-family: 'Lato', sans-serif;
            margin: 0;
            padding: 40px;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }
        
        h1.title {
            font-family: 'Cinzel', serif;
            text-align: center;
            color: #D4AF37;
            font-size: 3em;
            margin-bottom: 0.2em;
        }
        
        .subtitle {
            text-align: center;
            color: #888;
            font-style: italic;
            margin-bottom: 4em;
        }

        .wall-header {
            text-align: center;
            margin-top: 80px;
            margin-bottom: 40px;
            page-break-before: always;
        }
        
        .wall-title {
            font-family: 'Cinzel', serif;
            font-size: 3em;
            color: #D4AF37;
            text-transform: uppercase;
            letter-spacing: 0.2em;
            margin-bottom: 20px;
        }
        
        .wall-map {
            background: #080808;
            border: 1px solid #333;
            padding: 20px;
            display: inline-block;
            margin-bottom: 30px;
            box-shadow: 0 0 30px rgba(212, 175, 55, 0.1);
        }

        .constellation-entry {
            background: #111;
            border: 1px solid #333;
            padding: 40px;
            margin-bottom: 60px;
            border-radius: 4px;
            page-break-inside: avoid;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 1px solid #333;
            padding-bottom: 20px;
        }

        .id-tag {
            font-family: 'Courier New', monospace;
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        h2 {
            font-family: 'Cinzel', serif;
            color: #D4AF37;
            font-size: 2em;
            margin: 10px 0;
        }

        .greek-key {
            color: #AAA;
            font-family: 'Cinzel', serif;
        }

        .visual-container {
            display: flex;
            justify-content: center;
            margin: 30px 0;
            background: #050505;
            padding: 20px;
            border: 1px solid #222;
        }
        
        .svg-wrapper svg {
            /* SVGs are responsive */
            max-width: 100%;
        }

        .mythos p {
            line-height: 1.6;
            font-size: 1.1em;
            color: #CCC;
        }
        
        h3 {
             font-family: 'Cinzel', serif;
             color: #888;
             border-bottom: 1px solid #333;
             display: inline-block;
             margin-bottom: 10px;
        }

        .attributes {
            margin-top: 30px;
            background: #151515;
            padding: 20px;
            border-left: 3px solid #D4AF37;
        }

        .mantra {
            font-family: 'Cinzel', serif;
            font-style: italic;
            color: #D4AF37;
            margin-top: 15px;
            text-align: center;
            font-size: 1.2em;
        }
        
        .separator {
            border: 0;
            height: 1px;
            background: #333;
            margin: 40px 0;
            display: none; /* Hidden visually, just for structure */
        }

        @media print {
            body { 
                background: white; 
                color: black; 
            }
            .constellation-entry {
                background: white;
                border: 1px solid #ccc;
                color: black;
                box-shadow: none;
                page-break-after: always;
            }
            .visual-container {
                background: white;
                border: 1px solid #ddd;
            }
            h2, .mantra, h1.title, .wall-title {
                color: #000;
            }
            .attributes {
                background: #f9f9f9;
                border-left: 3px solid #000;
            }
            .wall-map {
                background: white;
                border: 1px solid #000;
                box-shadow: none;
            }
        }
    </style>
</head>
<body>
    <h1 class="title">The Book of 91 Stars</h1>
    <div class="subtitle">A Grimoire of the Adyton Constellations</div>
    """]

    # Process order: Sun, Mercury, Venus, Moon, Mars, Jupiter, Saturn
    wall_order = ["Sun", "Mercury", "Venus", "Moon", "Mars", "Jupiter", "Saturn"]
    
    count = 0
    for wall_name in wall_order:
        if wall_name not in mythos_db:
            continue
            
        # 1. Start Wall Section with Full Map
        if wall_name in lattice_db:
            wall_svg = render_full_wall(wall_name, lattice_db[wall_name])
            html_content.append(f"""
            <div class="wall-header">
                <div class="wall-title">The {wall_name} Wall</div>
                <div class="wall-map">
                    {wall_svg}
                </div>
            </div>
            """)
        else:
            html_content.append(f"""
            <div class="wall-header">
                <div class="wall-title">The {wall_name} Wall</div>
            </div>
            """)

        wall_data = mythos_db[wall_name]
        # Sort IDs numerically
        sorted_ids = sorted(wall_data.keys(), key=lambda x: int(x) if x.isdigit() else 99)
        
        for cid in sorted_ids:
            shape_key = f"{wall_name}_{cid}"
            
            # 1. Get Geometry
            nodes = []
            if shape_key in shapes_db:
                nodes = parse_shape_to_grid(shapes_db[shape_key])
            
            # 2. Generate SVG
            svg_str = ""
            if nodes:
                edges = calculate_mst(nodes)
                svg_str = render_svg(shape_key, nodes, edges)
            else:
                svg_str = "<!-- No Shape Data -->"
                
            # 3. Generate HTML
            entry_html = generate_entry_html(wall_name, cid, wall_data[cid], svg_str)
            html_content.append(entry_html)
            count += 1

    html_content.append("</body></html>")

    print(f"Generating Book with {count} entries...")
    with open(OUTPUT_HTML, 'w') as f:
        f.write("\n".join(html_content))
    
    print(f"Success! Book inscribed at: {OUTPUT_HTML}")

if __name__ == "__main__":
    main()
