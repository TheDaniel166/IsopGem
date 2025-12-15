import os
import re
from pathlib import Path

def audit_documentation():
    project_root = Path("/home/burkettdaniel927/projects/isopgem")
    src_pillars = project_root / "src/pillars"
    wiki_pillars = project_root / "wiki/pillars"

    # 1. Collect actual source files
    source_files = set()
    for root, dirs, files in os.walk(src_pillars):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                # key = filename only (e.g. "openastro_service.py")
                # Warning: duplicates possible across pillars? 
                # Better to use relative path? 
                # The documentation usually refers to the file by name in the header: ### **[filename.py](...)**
                # So we verify if the filename is present.
                source_files.add(file)

    # 2. Collect documented files
    documented_files = set()
    for root, dirs, files in os.walk(wiki_pillars):
        for file in files:
            if file.endswith(".md"):
                content = (wiki_pillars / file).read_text()
                # Pattern: ### **[filename.py](...)**
                matches = re.findall(r"\[([\w_]+\.py)\]", content)
                documented_files.update(matches)

    # 3. Compare
    missing = source_files - documented_files
    
    print(f"Total Source Files: {len(source_files)}")
    print(f"Total Documented Files: {len(documented_files)}")
    print(f"Missing Files: {len(missing)}")
    
    if missing:
        print("\n--- MISSING FILES ---")
        for f in sorted(list(missing)):
            print(f)

if __name__ == "__main__":
    audit_documentation()
