#!/usr/bin/env python3
"""
Automate Inscription Engine for IsopGem - The Ritual of Connection.
Recursively scans the repository to ensure EVERY file is referenced and documented.
Now audits Consumers (Who imports this) and Key Interactions (Public interface).
"""
import os
import ast
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
WIKI_DIR = PROJECT_ROOT / "wiki"
PILLARS_DIR = PROJECT_ROOT / "src" / "pillars"
SHARED_DIR = PROJECT_ROOT / "src" / "shared"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
TESTS_DIR = PROJECT_ROOT / "tests"

# Sacred Geometry Template
TEMPLATE = """
---

**File:** `{file_path}`

**Role:** `{role}`

**Purpose:** {purpose}

**Input (Ingests):**
{inputs}

**Output (Emits):**
{outputs}

**Dependencies (It Needs):**
{dependencies}

**Consumers (Who Needs It):**
{consumers}

**Key Interactions:**
{interactions}
"""

class ProjectMapper:
    """Surveys the Temple to map diplomatic relations (Imports)."""
    def __init__(self):
        self.importers = defaultdict(list) # Target Module -> List of relative file paths
        self.file_to_mod = {} # Path -> Module Name
        self.mod_to_file = {} # Module Name -> Path

    def survey(self):
        """Perform a total scan of Python files."""
        for root, _, files in os.walk(PROJECT_ROOT / "src"):
            if "__pycache__" in root: continue
            for file in files:
                if not file.endswith(".py"): continue
                path = Path(root) / file
                rel_path = path.relative_to(PROJECT_ROOT)
                
                # Derive module name (e.g., shared.ui.theme)
                if "src" in path.parts:
                    src_idx = path.parts.index("src")
                    mod_parts = path.parts[src_idx+1:]
                    mod_name = ".".join(mod_parts).replace(".py", "")
                    if mod_name.endswith(".__init__"):
                        mod_name = mod_name[:-9]
                    self.file_to_mod[str(rel_path)] = mod_name
                    self.mod_to_file[mod_name] = str(rel_path)

        # Now scan for imports
        for root, _, files in os.walk(PROJECT_ROOT):
            if any(p in root for p in [".venv", ".git", "__pycache__"]): continue
            for file in files:
                if not file.endswith(".py"): continue
                path = Path(root) / file
                rel_path = path.relative_to(PROJECT_ROOT)
                
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for n in node.names:
                                self.importers[n.name].append(str(rel_path))
                        elif isinstance(node, ast.ImportFrom):
                            mod = node.module or ""
                            # Handle relative imports if needed, but project uses absolute mostly
                            self.importers[mod].append(str(rel_path))
                            for n in node.names:
                                full_mod = f"{mod}.{n.name}"
                                self.importers[full_mod].append(str(rel_path))
                except: pass

    def get_consumers(self, file_path_rel: str) -> str:
        """Finds who imports the given file."""
        mod = self.file_to_mod.get(file_path_rel)
        if not mod: return "* None detected."
        
        consumers = []
        # Check for direct module match or parent module match
        for m, paths in self.importers.items():
            if m == mod or m.startswith(mod + "."):
                consumers.extend(paths)
        
        consumers = sorted(list(set([c for c in consumers if c != file_path_rel])))
        if not consumers: return "* None detected."
        return "\n".join([f"* `{c}`" for c in consumers])

def get_file_metadata(path: Path, mapper: ProjectMapper):
    """Parses a Python file to extract metadata for documentation."""
    rel_path = path.relative_to(PROJECT_ROOT)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content)
            
        # 1. Purpose
        purpose = ast.get_docstring(tree) or "Soul not yet specified."
        purpose = purpose.split("\n")[0].strip()
        
        # 2. Role
        role = "[Scout]"
        parts = path.parts
        if "ui" in parts: role = "[Skin] (UI/View)"
        elif "services" in parts: role = "[Muscle] (Service)"
        elif "models" in parts: role = "[Bone] (Model)"
        elif "repositories" in parts or "repos" in parts: role = "[Memory] (Repository)"
        elif "utils" in parts: role = "[Tool] (Utility)"
        
        # 3. Dependencies
        deps = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names: deps.append(f"* `{n.name}`")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for n in node.names: deps.append(f"* `{module}.{n.name}`")
        deps = "\n".join(sorted(list(set(deps))))[:500] or "* None."

        # 4. Inputs/Outputs & Interactions
        inputs = []
        outputs = []
        interactions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == "__init__":
                    args = [arg.arg for arg in node.args.args if arg.arg != "self"]
                    inputs.extend([f"* `{a}`" for a in args])
                elif not node.name.startswith("_"):
                    doc = ast.get_docstring(node) or "Functional interface."
                    # Truncate long docstrings
                    doc = doc.split("\n")[0][:100]
                    interactions.append(f"**Exposes:** `{node.name}()` - *{doc}*")
            
            # Look for Signals
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if isinstance(node.value, ast.Call):
                            func = node.value.func
                            if isinstance(func, ast.Name) and func.id == "pyqtSignal":
                                interactions.append(f"**Emits:** `{target.id}` - *Nervous System Signal.*")
            
            # Look for dataclass fields (ClassDef with @dataclass decorator)
            if isinstance(node, ast.ClassDef):
                is_dataclass = any(
                    (isinstance(d, ast.Name) and d.id == "dataclass") or
                    (isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "dataclass")
                    for d in node.decorator_list
                )
                if is_dataclass:
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            inputs.append(f"* `{item.target.id}` (Field)")
                
                # Look for SQLAlchemy Columns
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and isinstance(item.value, ast.Call):
                                func = item.value.func
                                if isinstance(func, ast.Name) and func.id == "Column":
                                    inputs.append(f"* `{target.id}` (Column)")
                                elif isinstance(func, ast.Attribute) and func.attr == "Column":
                                    inputs.append(f"* `{target.id}` (Column)")

        inputs = "\n".join(inputs) or "* Pure data structure or utility module."
        outputs = "* Data primitives or DTOs." # Heuristic
        interactions = "\n".join(interactions) or "* Internal logic only."
        
        return {
            "purpose": purpose,
            "role": role,
            "dependencies": deps,
            "inputs": inputs,
            "outputs": outputs,
            "consumers": mapper.get_consumers(str(rel_path)),
            "interactions": interactions
        }
    except Exception as e:
        return {
            "purpose": f"Error parsing soul: {str(e)}",
            "role": "[Fracture]",
            "dependencies": "* Unknown.",
            "inputs": "* Unknown.",
            "outputs": "* Unknown.",
            "consumers": "* Unknown.",
            "interactions": "* Unknown."
        }

def update_documentation(ref_file: Path, entries_map: dict):
    """Updates the REFERENCE.md file, replacing existing entries or appending new ones."""
    if not ref_file.exists():
        content = "# Manifest\n\n"
        content += f"<!-- Last Verified: {datetime.now().strftime('%Y-%m-%d')} -->\n\n"
    else:
        with open(ref_file, "r", encoding="utf-8") as f:
            content = f.read()

    # Split by horizontal rules
    sections = content.split("\n---")
    header = sections[0]
    existing_entries = {}
    
    for section in sections[1:]:
        match = re.search(r"\*\*File:\*\* `(.+?)`", section)
        if match:
            existing_entries[match.group(1)] = section
            
    # Merge
    final_sections = [header]
    all_files = sorted(list(set(list(existing_entries.keys()) + list(entries_map.keys()))))
    
    for file in all_files:
        if file in entries_map:
            final_sections.append(entries_map[file])
        else:
            final_sections.append(existing_entries[file])
            
    with open(ref_file, "w", encoding="utf-8") as f:
        f.write("\n".join(final_sections).strip() + "\n")

def inscribe_pillar(pillar_name: str, mapper: ProjectMapper):
    pillar_src = PILLARS_DIR / pillar_name
    pillar_wiki = WIKI_DIR / "02_pillars" / pillar_name
    ref_file = pillar_wiki / "REFERENCE.md"
    
    entries_map = {}
    for root, _, files in os.walk(pillar_src):
        for file in sorted(files):
            if not file.endswith(".py") or file == "__init__.py": continue
            file_path = Path(root) / file
            rel_path = file_path.relative_to(PROJECT_ROOT)
            
            print(f"Auditing: {rel_path}")
            meta = get_file_metadata(file_path, mapper)
            entries_map[str(rel_path)] = TEMPLATE.format(
                file_path=rel_path,
                role=meta["role"],
                purpose=meta["purpose"],
                inputs=meta["inputs"],
                outputs=meta["outputs"],
                dependencies=meta["dependencies"],
                consumers=meta["consumers"],
                interactions=meta["interactions"]
            )
    
    update_documentation(ref_file, entries_map)

def inscribe_manifest(base_dir: Path, wiki_file: Path, title: str, mapper: ProjectMapper):
    entries_map = {}
    for root, _, files in os.walk(base_dir):
        if "__pycache__" in root: continue
        for file in sorted(files):
            if not file.endswith(".py") or file == "__init__.py": continue
            file_path = Path(root) / file
            rel_path = file_path.relative_to(PROJECT_ROOT)
            
            print(f"Auditing: {rel_path}")
            meta = get_file_metadata(file_path, mapper)
            entries_map[str(rel_path)] = TEMPLATE.format(
                file_path=rel_path,
                role=meta["role"],
                purpose=meta["purpose"],
                inputs=meta["inputs"],
                outputs=meta["outputs"],
                dependencies=meta["dependencies"],
                consumers=meta["consumers"],
                interactions=meta["interactions"]
            )
            
    update_documentation(wiki_file, entries_map)

def main():
    print("Invocation: The Ritual of Connection...")
    mapper = ProjectMapper()
    print("Surveying the Temple's diplomatic map...")
    mapper.survey()
    
    # 1. Inscribe Pillars
    if PILLARS_DIR.exists():
        for item in sorted(PILLARS_DIR.iterdir()):
            if item.is_dir() and not item.name.startswith("__"):
                inscribe_pillar(item.name, mapper)
                
    # 2. Inscribe Shared Library
    if SHARED_DIR.exists():
        inscribe_manifest(SHARED_DIR, WIKI_DIR / "00_foundations" / "SHARED_REFERENCE.md", "Shared Library - Foundations", mapper)

    # 3. Inscribe Scripts
    if SCRIPTS_DIR.exists():
        inscribe_manifest(SCRIPTS_DIR, WIKI_DIR / "00_foundations" / "SCRIPTS_REFERENCE.md", "Automation Library - Scripts", mapper)
        
    # 4. Inscribe Tests
    if TESTS_DIR.exists():
        inscribe_manifest(TESTS_DIR, WIKI_DIR / "00_foundations" / "TESTS_REFERENCE.md", "Planetary Trials - Tests", mapper)

    print("Success: The Ritual of Connection is complete.")

if __name__ == "__main__":
    main()
