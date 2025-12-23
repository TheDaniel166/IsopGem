import re
import os

TARGET_FILE = "/home/burkettdaniel927/projects/isopgem/Docs/adyton_walls/The_Book_of_91_Stars.md"

def text_to_grid(text):
    lines = [line for line in text.strip().split('\n') if line.strip()]
    grid = []
    for line in lines:
        # 1 for Star (■), 0 for Empty (·)
        row = [1 if c == '■' else 0 for c in line.strip()]
        grid.append(row)
    return grid

def render_asterism(grid):
    if not grid:
        return ""
    
    height = len(grid)
    width = len(grid[0])
    
    output_lines = []
    
    for y in range(height):
        # 1. Star Row
        row_str = ""
        for x in range(width):
            # Render Node
            if grid[y][x]:
                row_str += "★"
            else:
                row_str += "·"
            
            # Render Horizontal Link (East)
            if x < width - 1:
                # If both current and next are stars, connect them
                if grid[y][x] and grid[y][x+1]:
                    row_str += "──"
                else:
                    row_str += "  "
        output_lines.append(row_str)
        
        # 2. Vertical Link Row (South) - only if not the last row
        if y < height - 1:
            link_row_str = ""
            for x in range(width):
                # Check South connection
                # Logic: If both current(x,y) and below(x,y+1) are stars, connect
                if grid[y][x] and grid[y+1][x]:
                    link_row_str += "│"
                else:
                    link_row_str += " "
                
                # Spacer matching the horizontal link length (2 chars)
                if x < width - 1:
                    link_row_str += "  "
            
            # Optimization: Don't add blank link rows if they are empty?
            # No, we need them to maintain the aspect ratio/visual logic, 
            # otherwise disjointed stars look weird.
            output_lines.append(link_row_str)
            
    return "\n".join(output_lines)

def process_match(match):
    content = match.group(1)
    # Sanity check: ensure it looks like a grid
    if not all(c in '■· \n' for c in content):
        return match.group(0) # Return unchanged if it contains other chars
        
    try:
        grid = text_to_grid(content)
        new_visual = render_asterism(grid)
        return f"```\n{new_visual}\n```"
    except Exception as e:
        print(f"Error processing block: {e}")
        return match.group(0)

def main():
    if not os.path.exists(TARGET_FILE):
        print(f"File not found: {TARGET_FILE}")
        return

    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to find code blocks containing only our target characters
    # We look for blocks that look like grids
    # pattern = r"```\n([■·\n]+)\n```" 
    # slightly more permissive with whitespace
    pattern = r"```\n([■·\s]+?)```"
    
    new_content = re.sub(pattern, process_match, content)
    
    # Check if changes were made
    if new_content == content:
        print("No changes were made. Regex might not have matched.")
    else:
        with open(TARGET_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Successfully transformed diagrams in {TARGET_FILE}")

if __name__ == "__main__":
    main()
