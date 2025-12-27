#!/usr/bin/env python3
"""
Wiki Synchronization Engine for IsopGem - Universal Manifestation Ritual.
Transmutes the local hierarchical 'wiki/' directory AND repository organs (scripts, tests)
into a flat, comprehensive GitHub Wiki structure.
"""
import os
import shutil
import subprocess
import sys
import ast
from pathlib import Path

# Configuration
WIKI_LOCAL_DIR = Path("wiki")
SCRIPTS_DIR = Path("scripts")
TESTS_DIR = Path("tests")
WIKI_REMOTE_URL = "https://github.com/TheDaniel166/IsopGem.wiki.git"
TEMP_SYNC_DIR = Path(".wiki_sync_temp")

def run_command(command, cwd=None):
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, cwd=cwd, text=True
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        return None
    return stdout.strip()

def get_docstring(path: Path) -> str:
    """Extracts the first docstring from a Python file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
            doc = ast.get_docstring(tree)
            if doc:
                return doc.split("\n")[0].strip() # Return first line
    except Exception:
        pass
    return "No description available."

def transmute_name(path: Path, base_dir: Path, prefix: str = "") -> str:
    """Converts a local path to a flat GitHub Wiki filename."""
    rel = path.relative_to(base_dir)
    parts = list(rel.parts)
    parts[-1] = Path(parts[-1]).stem
    new_name = "-".join(parts).replace("_", "-")
    if prefix:
        new_name = f"{prefix}-{new_name}"
    return f"{new_name}.md"

def generate_manifest(title: str, dir_path: Path, wiki_prefix: str, record_map: dict) -> str:
    """Generates a manifest page for repository directories (scripts, tests)."""
    content = f"# {title}\n\n"
    content += f"Inventory of the {title.lower()} sphere.\n\n"
    
    # We recursively find .py files
    for root, dirs, files in os.walk(dir_path):
        current_dir = Path(root)
        if "__pycache__" in current_dir.parts: continue
        
        rel_dir = current_dir.relative_to(dir_path)
        if str(rel_dir) != ".":
            content += f"### {str(rel_dir).replace('_', ' ').title()}\n"
        
        for file in sorted(files):
            if not file.endswith(".py"): continue
            file_path = current_dir / file
            flat_ref = transmute_name(file_path, dir_path, wiki_prefix).replace(".md", "")
            
            # Extract docstring
            desc = get_docstring(file_path)
            content += f"- [{file}]({flat_ref}) - *{desc}*\n"
            record_map[str(file_path)] = flat_ref
            
            # Create a simple view page for the script
            page_content = f"# {file}\n\nPath: `{file_path}`\n\n## Description\n{desc}\n\n"
            (TEMP_SYNC_DIR / f"{flat_ref}.md").write_text(page_content)
    
    return content

def sync():
    print("Invocation: Universal Manifestation Ritual...")
    
    if not WIKI_LOCAL_DIR.exists():
        print("Fracture: Local wiki missing.")
        sys.exit(1)

    if TEMP_SYNC_DIR.exists():
        shutil.rmtree(TEMP_SYNC_DIR)
    
    print(f"Cloning remote from {WIKI_REMOTE_URL}...")
    if run_command(f"git clone {WIKI_REMOTE_URL} {TEMP_SYNC_DIR}") is None:
        sys.exit(1)

    # Clean the slate
    for item in TEMP_SYNC_DIR.iterdir():
        if item.name == ".git": continue
        if item.is_dir(): shutil.rmtree(item)
        else: item.unlink()

    record_map = {} # Path String -> Flat Name (minus .md)

    # 1. Flatten the Akaschic Scrolls (wiki/)
    print("Flattening Akaschic scrolls...")
    for root, dirs, files in os.walk(WIKI_LOCAL_DIR):
        for file in files:
            if not file.endswith(".md"): continue
            if file.startswith("_"): continue
            if file == "Home.md": continue
            src_path = Path(root) / file
            if "manual" in src_path.parts: continue
            
            flat_name = transmute_name(src_path, WIKI_LOCAL_DIR)
            shutil.copy2(src_path, TEMP_SYNC_DIR / flat_name)
            record_map[str(src_path)] = flat_name.replace(".md", "")

    # 2. Manifest Repository Organs (Scripts, Tests, Workflows)
    print("Manifesting Scripts...")
    scripts_manifest = generate_manifest("Scripts Manifest", SCRIPTS_DIR, "Scripts", record_map)
    (TEMP_SYNC_DIR / "Scripts-Manifest.md").write_text(scripts_manifest)
    record_map["Scripts-Manifest"] = "Scripts-Manifest"

    print("Manifesting Rituals (Tests)...")
    tests_manifest = generate_manifest("Tests and Rituals Manifest", TESTS_DIR, "Tests", record_map)
    (TEMP_SYNC_DIR / "Tests-Manifest.md").write_text(tests_manifest)
    record_map["Tests-Manifest"] = "Tests-Manifest"

    # 3. Manifest Home and Sidebar
    print("Manifesting index and navigation...")
    if (WIKI_LOCAL_DIR / "Home.md").exists():
        shutil.copy2(WIKI_LOCAL_DIR / "Home.md", TEMP_SYNC_DIR / "Home.md")
    elif (WIKI_LOCAL_DIR / "manual" / "index.md").exists():
        shutil.copy2(WIKI_LOCAL_DIR / "manual" / "index.md", TEMP_SYNC_DIR / "Home.md")

    sidebar_content = "### [Home](Home)\n\n"
    
    halls = {
        "00_foundations": "Hall 0: Foundations",
        "01_blueprints": "Hall 1: Blueprints",
        "02_pillars": "Hall 2: Grimoires (Pillars)",
        "03_lexicon": "Hall 3: Lexicon",
        "04_prophecies": "Hall 4: Prophecies"
    }

    for hall_id, hall_name in halls.items():
        sidebar_content += f"### {hall_name}\n"
        hall_dir = WIKI_LOCAL_DIR / hall_id
        if not hall_dir.exists(): continue
        
        for item in sorted(hall_dir.iterdir()):
            if item.is_file() and item.suffix == ".md":
                flat_ref = record_map.get(str(item))
                if flat_ref:
                    sidebar_content += f"- [{item.stem.replace('_', ' ').title()}]({flat_ref})\n"
            elif item.is_dir():
                sidebar_content += f"- **{item.name.replace('_', ' ').title()}**\n"
                for sub in sorted(item.iterdir()):
                    if sub.is_file() and sub.suffix == ".md":
                        flat_ref = record_map.get(str(sub))
                        if flat_ref:
                            sidebar_content += f"  - [{sub.stem.replace('_', ' ').title()}]({flat_ref})\n"
        sidebar_content += "\n"

    # Add Repositor Organs to Sidebar
    sidebar_content += "### The Workshop\n"
    sidebar_content += "- [Scripts Manifest](Scripts-Manifest)\n"
    sidebar_content += "- [Rituals Manifest](Tests-Manifest)\n"

    (TEMP_SYNC_DIR / "_Sidebar.md").write_text(sidebar_content)

    # 4. Seal and Transmit
    print("Sealing the Record...")
    run_command('git config user.email "sophia@isopgem.ai"', cwd=TEMP_SYNC_DIR)
    run_command('git config user.name "Sophia the Architect"', cwd=TEMP_SYNC_DIR)
    run_command("git add .", cwd=TEMP_SYNC_DIR)
    
    if not run_command("git status --porcelain", cwd=TEMP_SYNC_DIR):
        print("Harmony: Already synchronized.")
        shutil.rmtree(TEMP_SYNC_DIR)
        return

    commit_msg = f"Universal Manifestation: {os.popen('date').read().strip()}"
    run_command(f'git commit -m "{commit_msg}"', cwd=TEMP_SYNC_DIR)
    
    if run_command("git push origin master", cwd=TEMP_SYNC_DIR) is None:
        run_command("git push origin main", cwd=TEMP_SYNC_DIR)

    print("Success: Total Repository Manifestation complete.")
    shutil.rmtree(TEMP_SYNC_DIR)

if __name__ == "__main__":
    sync()
