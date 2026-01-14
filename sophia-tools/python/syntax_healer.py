import os
import py_compile

def heal_file(filepath):
    # Check syntax first
    try:
        py_compile.compile(filepath, doraise=True)
        return False
    except py_compile.PyCompileError:
        pass
    except Exception:
        pass

    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    # Look for stray triple quotes in header (first 40 lines)
    quote_indices = []
    for i, line in enumerate(lines[:40]):
        s = line.strip()
        if s == '"""' or s == "'''":
            quote_indices.append(i)
    
    # Pattern: Header Start(1), Header End(2), Stray(3), Docstring Start(4)
    # We want to remove Quote 3.
    if len(quote_indices) >= 3:
        target_idx = quote_indices[2] # 0-indexed, so 3rd item
        
        print(f"Attempting to heal {filepath} by removing line {target_idx+1}...")
        
        new_lines = list(lines)
        del new_lines[target_idx]
        
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
print("Starting Syntax Healer...")
for root, dirs, files in os.walk("src/shared"):
    for file in files:
        if file.endswith(".py"):
            if heal_file(os.path.join(root, file)):
                count += 1
print(f"Total healed: {count}")
