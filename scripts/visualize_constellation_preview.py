
def text_to_grid(text):
    lines = text.strip().split('\n')
    grid = []
    for line in lines:
        row = [1 if c in ['■', '#'] else 0 for c in line]
        grid.append(row)
    return grid

def render_stars_only(grid):
    output = []
    for row in grid:
        line = "".join(["★ " if cell else "· " for cell in row])
        output.append(line)
    return "\n".join(output)

def render_asterism_cardinal(grid):
    height = len(grid)
    width = len(grid[0])
    
    # Canvas size: (Height * 2 - 1) x (Width * 2 - 1)
    # Actually, let's just use simple mapping
    # Rows will be: StarRow, LinkRow, StarRow...
    
    output_lines = []
    
    for y in range(height):
        # 1. Star Row
        row_str = ""
        for x in range(width):
            if grid[y][x]:
                row_str += "★"
            else:
                row_str += "·"
            
            # Check East connection
            if x < width - 1:
                if grid[y][x] and grid[y][x+1]:
                    row_str += "──"
                else:
                    row_str += "  "
        output_lines.append(row_str)
        
        # 2. Vertical Link Row (if not last row)
        if y < height - 1:
            link_row_str = ""
            for x in range(width):
                # Check South connection
                if grid[y][x] and grid[y+1][x]:
                    link_row_str += "│"
                else:
                    link_row_str += " "
                
                # Spacer between vertical links
                if x < width - 1:
                    link_row_str += "  "
            output_lines.append(link_row_str)
            
    return "\n".join(output_lines)

example_1 = """
■■■■
■■■■
"""

example_2 = """
·■·
■■■
·■·
"""

example_3 = """
■
■
■
■
"""

print("--- STYLE A: Stars Only ---")
print(render_stars_only(text_to_grid(example_1)))
print("\n")
print(render_stars_only(text_to_grid(example_2)))

print("\n--- STYLE B: Connected Asterism ---")
print(render_asterism_cardinal(text_to_grid(example_1)))
print("\n")
print(render_asterism_cardinal(text_to_grid(example_2)))
print("\n")
print(render_asterism_cardinal(text_to_grid(example_3)))
