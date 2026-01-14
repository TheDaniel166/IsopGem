import os

BAD_MARKER = "⚠️  GRANDFATHERED VIOLATION"
END_MARKER_TEXT = "Refactoring plan: See wiki/"

def repair_file(filepath):
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        bad_start = -1
        for i, line in enumerate(lines):
            if BAD_MARKER in line:
                bad_start = i
                break
        
        if bad_start == -1:
            return False
            
        print(f"Repairing {filepath}...")
        
        bad_end = -1
        for i in range(bad_start, len(lines)):
            if END_MARKER_TEXT in lines[i]:
                 # Check next line for quote
                 if i + 1 < len(lines) and lines[i+1].strip() in ['"""', "'''"]:
                     bad_end = i + 1
                 else:
                     bad_end = i
                 break
        
        if bad_end == -1:
            print(f"  Failed: Could not find end of block for {filepath}")
            return False

        # Capture text for header
        header_text_lines = []
        for k in range(bad_start, bad_end + 1):
             l = lines[k].strip()
             if l not in ['"""', "'''"]:
                 header_text_lines.append(l)

        # Smart delete logic:
        # If preceding line was a quote that Opened this block (colliding with previous closure), delete it too.
        start_remove = bad_start
        if bad_start > 1:
             prev = lines[bad_start-1].strip()
             prev_prev = lines[bad_start-2].strip()
             # If we see """ followed by """, the second one likely opened our bad block
             if prev in ['"""', "'''"] and prev_prev in ['"""', "'''"]:
                  start_remove = bad_start - 1
        
        lines_to_keep = lines[:start_remove] + lines[bad_end+1:]
        
        clean_header = ['"""\n']
        for l in header_text_lines:
            clean_header.append(l + "\n")
        clean_header.append('"""\n\n')
        
        final_lines = clean_header + lines_to_keep
        
        with open(filepath, 'w') as f:
            f.writelines(final_lines)
            
        return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

count = 0
for root, dirs, files in os.walk("src/shared"):
    for file in files:
        if file.endswith(".py"):
             if repair_file(os.path.join(root, file)):
                 count += 1
print(f"Total repaired: {count}")
