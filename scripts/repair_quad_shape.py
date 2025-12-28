
from pathlib import Path

def repair():
    p = Path('src/pillars/geometry/services/quadrilateral_shape.py')
    lines = p.read_text().splitlines()
    new_lines = []
    
    # State machine? No, just replace known bad prefixes
    for line in lines:
        # If line starts with 2 spaces and not 4 (and not empty)
        if line.startswith('  ') and not line.startswith('    ') and not line.strip() == '':
            # 2 spaces -> 2 tabs?
            # Check context. The file uses tabs. 
            # The docstring quotes were at 2-tab level (inside __init__ which is 1-tab).
            # So 2 spaces were intended to be 2 tabs?
            # Replace '  ' with '\t\t' if it looks like a docstring part
            # But wait, I've already fixed the quotes with sed to \t\t
            if line.strip().startswith('"""') or line.strip().startswith('Attributes:') or line.strip().startswith('Returns:') or line.strip().startswith('Args:') or "todo:" in line:
                 new_lines.append(line.replace('  ', '\t\t', 1))
                 continue
                 
        # If line starts with 4 spaces
        if line.startswith('    '):
             # Replace 4 spaces with 2 tabs?
             # '    init   logic.' -> '\t\tinit   logic.'
             if 'logic.' in line or 'Description of' in line or 'Result of' in line:
                 new_lines.append(line.replace('    ', '\t\t', 1))
                 continue
                 
        # General safe fallback for the sed-damaged lines?
        # My sed changed `^  """` to `\t\t"""`.
        # So I only need to fix the body lines.
        
        # Let's just be aggressive on lines that look like my Scribe output
        if '   logic.' in line:
             new_lines.append('\t\t' + line.lstrip())
        elif 'Description of ' in line:
             new_lines.append('\t\t\t' + line.lstrip()) # Attributes/Args are usually indented one more level? 
             # Scribe output:
             # Args:
             #     arg: ...
             # "    " (4 spaces). If base is \t\t, then this is \t\t\t?
        elif 'Result of ' in line:
             new_lines.append('\t\t\t' + line.lstrip())
        elif line.strip() == 'Args:' or line.strip() == 'Returns:' or line.strip() == 'Attributes:':
             new_lines.append('\t\t' + line.lstrip())
        elif 'todo: Add public' in line:
             new_lines.append('\t\t    ' + line.lstrip())
        else:
             new_lines.append(line)
             
    p.write_text('\n'.join(new_lines) + '\n')
    print("Repaired.")

if __name__ == '__main__':
    repair()
