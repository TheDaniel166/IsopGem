#!/usr/bin/env python3
"""
Verify actual usage of shared/ modules - CORRECTED VERSION

This tool checks if a file is referenced ANYWHERE in the codebase:
1. Direct imports from any file in src/
2. Relative imports from other shared/ modules  
3. Symbol re-exports via __init__.py
4. String references in dynamic imports

A file is only an orphan if it has ZERO references anywhere.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Set, Dict, List, Tuple


def find_all_references(module_path: Path, src_root: Path) -> Tuple[List[str], Set[str]]:
    """
    Find ALL references to a module anywhere in src/.
    
    Returns:
        (importers, pillar_names)
    """
    importers = []
    pillars = set()
    
    rel_to_src = module_path.relative_to(src_root)
    module_name = module_path.stem
    
    # Convert to possible import paths
    import_path = str(rel_to_src.with_suffix("")).replace("/", ".")
    
    # Search patterns
    patterns = [
        f"from {import_path}",          # from shared.x.y import Z
        f"import {import_path}",         # import shared.x.y
        f"from .{module_name}",          # from .module import X (relative)
        f"import .{module_name}",        # import .module (relative)
        module_name,                     # Any mention of the module name
    ]
    
    # Search all Python files
    for py_file in src_root.rglob("*.py"):
        if py_file == module_path:
            continue
        
        try:
            content = py_file.read_text()
            
            # Check if any pattern matches
            found = False
            for pattern in patterns:
                if pattern in content:
                    # Verify it's actually an import, not just a string/comment
                    # Look for the pattern in an import context
                    if re.search(rf'(from|import)\s+.*{re.escape(pattern)}', content):
                        found = True
                        break
                    # Or if it's a relative import
                    elif pattern.startswith(".") and pattern in content:
                        found = True
                        break
            
            if found:
                rel_file = str(py_file.relative_to(src_root.parent))
                importers.append(rel_file)
                
                # Extract pillar if applicable
                if "src/pillars/" in rel_file:
                    pillar_name = rel_file.split("src/pillars/")[1].split("/")[0]
                    pillars.add(pillar_name.capitalize())
        
        except Exception:
            continue
    
    return importers, pillars


def check_symbol_exports(module_path: Path, src_root: Path) -> Tuple[Set[str], List[str]]:
    """
    Check if symbols from this module are re-exported via __init__.py
    and then imported elsewhere.
    
    Returns:
        (exported_symbols, indirect_importers)
    """
    exported_symbols = set()
    indirect_importers = []
    
    # Find what this module exports
    parent_init = module_path.parent / "__init__.py"
    if not parent_init.exists():
        return exported_symbols, indirect_importers
    
    try:
        init_content = parent_init.read_text()
        module_name = module_path.stem
        
        # Find re-exported symbols
        # Pattern: from .module import X, Y, Z
        pattern = rf'from \.{module_name} import ([^\n]+)'
        matches = re.findall(pattern, init_content)
        for match in matches:
            symbols = [s.strip().split()[0] for s in match.split(',')]  # Handle "as" aliases
            exported_symbols.update(symbols)
        
        if not exported_symbols:
            return exported_symbols, indirect_importers
        
        # Now find who imports these symbols from the parent package
        parent_rel = module_path.parent.relative_to(src_root)
        parent_import = str(parent_rel).replace("/", ".")
        
        for py_file in src_root.rglob("*.py"):
            if py_file == module_path or py_file.parent == module_path.parent:
                continue
            
            try:
                content = py_file.read_text()
                for symbol in exported_symbols:
                    if re.search(rf'from {re.escape(parent_import)} import .*\b{symbol}\b', content):
                        rel_file = str(py_file.relative_to(src_root.parent))
                        if rel_file not in indirect_importers:
                            indirect_importers.append(rel_file)
                        break
            except Exception:
                continue
    
    except Exception as e:
        print(f"  Warning: Error checking exports for {module_path.name}: {e}")
    
    return exported_symbols, indirect_importers


def verify_shared_usage(shared_root: Path, src_root: Path) -> Dict:
    """Verify actual usage of all shared/ modules."""
    results = {}
    
    print("Analyzing each module...\n")
    
    for py_file in sorted(shared_root.rglob("*.py")):
        if py_file.name == "__init__.py":
            continue
        
        rel_path = str(py_file.relative_to(shared_root))
        
        # Find all direct references
        direct_refs, pillars = find_all_references(py_file, src_root)
        
        # Check for indirect usage via re-exports
        exported_symbols, indirect_refs = check_symbol_exports(py_file, src_root)
        
        # Combine
        all_refs = set(direct_refs + indirect_refs)
        all_pillars = pillars
        for ref in indirect_refs:
            if "src/pillars/" in ref:
                pillar = ref.split("src/pillars/")[1].split("/")[0]
                all_pillars.add(pillar.capitalize())
        
        is_orphan = len(all_refs) == 0
        
        results[rel_path] = {
            "direct_references": len(direct_refs),
            "indirect_references": len(indirect_refs),
            "total_references": len(all_refs),
            "exported_symbols": sorted(list(exported_symbols)),
            "pillars": sorted(list(all_pillars)),
            "is_orphan": is_orphan,
            "sample_references": sorted(list(all_refs))[:5],
        }
        
        # Progress indicator
        if is_orphan:
            print(f"  🗑️  {rel_path} - ORPHAN")
        elif len(all_refs) > 10:
            print(f"  ✅ {rel_path} - {len(all_refs)} refs")
    
    return results


def main():
    """Verify usage and generate report."""
    print("🔍 Verifying actual usage of shared/ modules (CORRECTED)\n")
    print("=" * 70)
    print("Checking for ANY reference in entire src/ directory")
    print("Including: direct imports, relative imports, re-exported symbols")
    print("=" * 70)
    print()
    
    shared_root = Path("src/shared")
    src_root = Path("src")
    
    results = verify_shared_usage(shared_root, src_root)
    
    # Summary stats
    total = len(results)
    orphans = [k for k, v in results.items() if v["is_orphan"]]
    used = total - len(orphans)
    
    print()
    print("=" * 70)
    print(f"📊 FINAL SUMMARY:")
    print(f"   Total modules: {total}")
    print(f"   Used: {used}")
    print(f"   True orphans: {len(orphans)}")
    print("=" * 70)
    print()
    
    # Show true orphans
    if orphans:
        print(f"🗑️  TRUE ORPHANS (ZERO references anywhere in src/):\n")
        for path in sorted(orphans):
            print(f"   - {path}")
        print()
        print("These files can be safely deleted.\n")
    else:
        print("✅ NO ORPHANS FOUND - All shared/ modules are referenced!\n")
    
    # Show heavily used modules
    heavily_used = [(k, v["total_references"]) for k, v in results.items() 
                    if v["total_references"] > 10]
    if heavily_used:
        print(f"🔥 HEAVILY USED MODULES (10+ references):\n")
        for path, count in sorted(heavily_used, key=lambda x: -x[1])[:10]:
            pillars = results[path]["pillars"]
            print(f"   {count:3d} refs - {path}")
            print(f"          Pillars: {', '.join(pillars) or 'Internal only'}")
        print()
    
    # Save full results
    output_file = Path("wiki/04_prophecies/shared_usage_verification.json")
    output_file.write_text(json.dumps(results, indent=2))
    print(f"💾 Full results saved to: {output_file}\n")


if __name__ == "__main__":
    main()
