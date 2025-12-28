import os
import re
import sys

def check_sovereignty():
    root = "src/pillars"
    violations = []
    print(f"Auditing Sovereignty in {root}...")
    
    if not os.path.exists(root):
        print(f"Error: {root} does not exist.")
        return

    for pillar in os.listdir(root):
        pillar_path = os.path.join(root, pillar)
        if not os.path.isdir(pillar_path) or pillar == "__pycache__":
            continue
        
        # print(f"Scanning Pillar: {pillar}...")
        
        for dirpath, _, filenames in os.walk(pillar_path):
            for filename in filenames:
                if not filename.endswith(".py"):
                    continue
                
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            # Check 'from pillars.X'
                            match = re.search(r"^\s*from\s+pillars\.(\w+)", line)
                            if match:
                                target_pillar = match.group(1)
                                if target_pillar != pillar:
                                    violations.append(f"VIOLATION: {filepath}:{i} imports pillars.{target_pillar}")
                            
                            # Check 'import pillars.X'
                            match = re.search(r"^\s*import\s+pillars\.(\w+)", line)
                            if match:
                                target_pillar = match.group(1)
                                if target_pillar != pillar:
                                    violations.append(f"VIOLATION: {filepath}:{i} imports pillars.{target_pillar}")
                except Exception as e:
                    print(f"Could not read {filepath}: {e}")

    if violations:
        print(f"\nFAILED: Found {len(violations)} Sovereignty Violations:")
        for v in violations:
            print(v)
    else:
        print("\nSUCCESS: Sovereignty Verified. No cross-pillar imports found.")

if __name__ == "__main__":
    check_sovereignty()
