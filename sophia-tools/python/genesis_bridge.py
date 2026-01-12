#!/usr/bin/env python3
"""
Sophia Genesis Bridge
Create new pillar structure following the Genesis Ritual.
"""

import sys
import json
from pathlib import Path
from typing import List


PILLAR_STRUCTURE = {
    "models": "__init__.py",
    "repositories": "__init__.py",
    "services": "__init__.py",
    "ui": "__init__.py",
    "utils": "__init__.py"
}

INIT_TEMPLATE = '''"""
{pillar_name} Pillar
{description}
"""

__all__ = []
'''

README_TEMPLATE = '''# {pillar_name} Pillar

{description}

## Structure

- `models/` - Data models
- `repositories/` - Database access layer
- `services/` - Business logic
- `ui/` - User interface components
- `utils/` - Helper utilities

## Sovereignty

This pillar is sovereign and must not directly import from other pillars.
Use shared substrate or signal bus for communication.
'''


def create_pillar_structure(workspace: Path, pillar_name: str, description: str) -> dict:
    """Create complete pillar directory structure."""
    created_dirs = []
    created_files = []
    
    # Create pillar root
    pillar_root = workspace / "src" / "pillars" / pillar_name
    
    if pillar_root.exists():
        return {
            "pillar_name": pillar_name,
            "created_directories": [],
            "created_files": [],
            "status": f"Pillar '{pillar_name}' already exists"
        }
    
    pillar_root.mkdir(parents=True, exist_ok=True)
    created_dirs.append(str(pillar_root.relative_to(workspace)))
    
    # Create subdirectories with __init__.py
    for subdir, init_file in PILLAR_STRUCTURE.items():
        subdir_path = pillar_root / subdir
        subdir_path.mkdir(exist_ok=True)
        created_dirs.append(str(subdir_path.relative_to(workspace)))
        
        if init_file:
            init_path = subdir_path / init_file
            init_content = INIT_TEMPLATE.format(
                pillar_name=pillar_name.title(),
                description=description or f"{pillar_name.title()} pillar components"
            )
            init_path.write_text(init_content)
            created_files.append(str(init_path.relative_to(workspace)))
    
    # Create pillar __init__.py
    pillar_init = pillar_root / "__init__.py"
    pillar_init_content = INIT_TEMPLATE.format(
        pillar_name=pillar_name.title(),
        description=description or f"{pillar_name.title()} pillar"
    )
    pillar_init.write_text(pillar_init_content)
    created_files.append(str(pillar_init.relative_to(workspace)))
    
    # Create README.md
    readme_path = pillar_root / "README.md"
    readme_content = README_TEMPLATE.format(
        pillar_name=pillar_name.title(),
        description=description or "Description pending"
    )
    readme_path.write_text(readme_content)
    created_files.append(str(readme_path.relative_to(workspace)))
    
    # Create grimoire entry
    grimoire_path = workspace / "wiki" / "02_pillars" / f"{pillar_name}.md"
    if not grimoire_path.parent.exists():
        grimoire_path.parent.mkdir(parents=True, exist_ok=True)
    
    grimoire_content = f'''# {pillar_name.title()} Grimoire

**Status**: Genesis
**Created**: {{AUTO_TIMESTAMP}}

## Purpose

{description or "Purpose to be defined"}

## Architecture

This pillar follows the standard structure:
- Models
- Repositories
- Services
- UI
- Utils

## Sovereignty

This pillar maintains sovereignty and communicates with other pillars through:
- Shared substrate
- Signal bus patterns

## Known Issues

None yet.
'''
    grimoire_path.write_text(grimoire_content)
    created_files.append(str(grimoire_path.relative_to(workspace)))
    
    return {
        "pillar_name": pillar_name,
        "created_directories": created_dirs,
        "created_files": created_files,
        "status": f"Pillar '{pillar_name}' created successfully via Genesis Ritual"
    }


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    pillar_name = sys.argv[2]
    description = sys.argv[3] if len(sys.argv) > 3 else ""
    
    result = create_pillar_structure(workspace_root, pillar_name, description)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
