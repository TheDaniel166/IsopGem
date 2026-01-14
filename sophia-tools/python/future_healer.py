import os
import py_compile

def heal_future(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    # Check for future import
    has_future = False
    for i, line in enumerate(lines[:30]):
        if "from __future__ import" in line:
            has_future = True
            break
            
    if not has_future:
        return False
        
    # Check if we have the specific bad header at the top
    # The header created by repair_headers.py starts with """ and contains GRANDFATHERED
    
    if len(lines) > 5 and lines[0].strip() == '"""' and ("GRANDFATHERED" in "".join(lines[1:10])):
        print(f"Healing __future__ conflict in {filepath}...")
        
        # Find closing quote of the bad header
        end_idx = -1
        for k in range(1, 20):
            # We look for a line that is JUST triple quotes
            if lines[k].strip() == '"""':
                end_idx = k
                break
        
        if end_idx != -1:
            # We want to remove lines 0 to end_idx
            # This leaves the file starting at end_idx + 1 (which might be blank lines, then REAL docstring)
            print(f"  Removing lines 1-{end_idx+1} (Header Block)...")
            new_lines = lines[end_idx+1:]
            
            with open(filepath, 'w') as f:
                f.writelines(new_lines)
                
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
print("Starting Future Healer...")
for root, dirs, files in os.walk("src/shared"):
    for file in files:
        if file.endswith(".py"):
            if heal_future(os.path.join(root, file)):
                count += 1
print(f"Total healed: {count}")
