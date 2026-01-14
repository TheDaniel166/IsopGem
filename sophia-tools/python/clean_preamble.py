import os
import py_compile

def clean_preamble(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    future_idx = -1
    for i, line in enumerate(lines[:50]):
        if "from __future__ import" in line:
            future_idx = i
            break
            
    if future_idx == -1:
        return False
        
    # Scan backwards from future_idx to find the "Official" docstring
    # Iterate backwards skipping blanks/comments
    doc_end = -1
    doc_start = -1
    
    scan_idx = future_idx - 1
    while scan_idx >= 0:
        line = lines[scan_idx].strip()
        if not line or line.startswith("#"):
            scan_idx -= 1
            if scan_idx < 0: break
            continue
        
        # Found content. Check if it ends with triple quotes.
        if line.endswith('"""') or line.endswith("'''"):
            doc_end = scan_idx
            marker = '"""' if line.endswith('"""') else "'''"
            
            # Check if this line ALSO starts the block (one-liner)
            if line.startswith(marker) and line.count(marker) >= 2:
                doc_start = scan_idx
            else:
                # Multiline. Scan back for opener.
                temp_idx = scan_idx - 1
                while temp_idx >= 0:
                    l = lines[temp_idx].strip()
                    if marker in l: 
                        doc_start = temp_idx
                        break
                    temp_idx -= 1
            break
        else:
             break
        scan_idx -= 1
        
    cleaned = False
    new_content = []
    
    if doc_start > 0:
        # Check if there is garbage before doc_start
        # Look for the BAD Header or Stray Quotes
        preamble = "".join(lines[:doc_start])
        if "GRANDFATHERED" in preamble or '"""' in preamble:
            print(f"Cleaning preamble for {filepath} (Docstring starts line {doc_start+1})...")
            kept_lines = lines[doc_start:]
            if lines[0].startswith("#!"):
                 kept_lines = [lines[0]] + kept_lines
            new_content = kept_lines
            cleaned = True
            
    elif doc_start == -1:
        # No docstring found immediately before future
        # Remove everything before future if we see garbage
        preamble = "".join(lines[:future_idx])
        if "GRANDFATHERED" in preamble or '"""' in preamble:
            print(f"Cleaning preamble for {filepath} (No docstring found)...")
            kept_lines = lines[future_idx:]
            if lines[0].startswith("#!"):
                 kept_lines = [lines[0]] + kept_lines
            new_content = kept_lines
            cleaned = True

    if cleaned:
        with open(filepath, 'w') as f:
            f.writelines(new_content)
        try:
            py_compile.compile(filepath, doraise=True)
            print("  -> Success!")
            return True
        except py_compile.PyCompileError:
            print("  -> Failed, reverting.")
            with open(filepath, 'w') as f:
                f.writelines(lines)

    return False

count = 0
print("Starting Clean Preamble...")
for root, dirs, files in os.walk("src/shared"):
    for file in files:
        if file.endswith(".py"):
            if clean_preamble(os.path.join(root, file)):
                count += 1
print(f"Total healed: {count}")
