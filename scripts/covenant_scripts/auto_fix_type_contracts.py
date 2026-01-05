#!/usr/bin/env python3
"""
THE RITE OF AUTOMATED CONTRACT RESTORATION

Applies intelligent type fixes to backend code:
1. Adds missing imports (Face, Vec3, cast)
2. Casts faces/vertices lists for type compatibility
3. Casts metadata dicts to dict[str, float]
4. Adds None guards in setters before arithmetic operations

Usage:
    python scripts/covenant_scripts/auto_fix_type_contracts.py [--target PATH] [--commit]

Options:
    --target PATH    Target file or directory (default: src/pillars/geometry/services)
    --commit         Apply fixes (default: dry run)
"""

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BASEDPYRIGHT_CMD = [str(REPO_ROOT / ".venv" / "bin" / "basedpyright"), "--outputjson"]


def run_basedpyright(target_path: Path) -> dict[str, Any]:
    """Run basedpyright and return JSON output."""
    result = subprocess.run(
        BASEDPYRIGHT_CMD + [str(target_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"generalDiagnostics": []}


def needs_face_import(diagnostics: list[dict[str, Any]]) -> bool:
    """Check if file needs Face import."""
    for diag in diagnostics:
        msg = diag.get("message", "")
        if "cannot be assigned to parameter \"faces\"" in msg and "Face" in msg:
            return True
    return False


def needs_vec3_import(diagnostics: list[dict[str, Any]]) -> bool:
    """Check if file needs Vec3 import."""
    for diag in diagnostics:
        msg = diag.get("message", "")
        if "Type of \"append\" is partially unknown" in msg or "list[Unknown]" in msg:
            return True
    return False


def needs_cast_import(diagnostics: list[dict[str, Any]]) -> bool:
    """Check if file needs cast."""
    return needs_face_import(diagnostics) or "dict[Unknown, Unknown]" in str(diagnostics)


def find_faces_assignments(content: str, diagnostics: list[dict[str, Any]]) -> list[int]:
    """Find line numbers where faces need casting."""
    lines_needing_cast = []
    for diag in diagnostics:
        msg = diag.get("message", "")
        if "cannot be assigned to parameter \"faces\"" in msg:
            line_num = diag["range"]["start"]["line"]
            lines_needing_cast.append(line_num)
    return lines_needing_cast


def find_metadata_returns(content: str, diagnostics: list[dict[str, Any]]) -> list[int]:
    """Find line numbers where metadata needs casting."""
    lines_needing_cast = []
    for diag in diagnostics:
        msg = diag.get("message", "")
        if "dict[Unknown, Unknown]" in msg and "metadata" in msg:
            line_num = diag["range"]["start"]["line"]
            lines_needing_cast.append(line_num)
    return lines_needing_cast


def find_none_arithmetic_lines(diagnostics: list[dict[str, Any]]) -> list[tuple[int, str]]:
    """Find lines where None arithmetic happens (need guards)."""
    lines_needing_guard = []
    for diag in diagnostics:
        msg = diag.get("message", "")
        if 'Operator "' in msg and '" not supported for "None"' in msg:
            line_num = diag["range"]["start"]["line"]
            # Extract variable name from message if possible
            lines_needing_guard.append((line_num, msg))
    return lines_needing_guard


def fix_imports(content: str, needs_face: bool, needs_vec3: bool, needs_cast: bool) -> str:
    """Add missing imports to solid_payload."""
    lines = content.split('\n')
    
    # Find the solid_payload import line
    import_idx = -1
    for i, line in enumerate(lines):
        if 'from ..shared.solid_payload import' in line:
            import_idx = i
            break
    
    if import_idx == -1:
        return content
    
    # Parse existing imports
    import_line = lines[import_idx]
    match = re.search(r'from ..shared.solid_payload import (.+)', import_line)
    if not match:
        return content
    
    imports = [s.strip() for s in match.group(1).split(',')]
    
    # Add missing imports
    if needs_face and 'Face' not in imports:
        imports.insert(0, 'Face')
    if needs_vec3 and 'Vec3' not in imports:
        imports.insert(1, 'Vec3')
    
    # Also check typing imports
    typing_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('from typing import'):
            typing_idx = i
            break
    
    if typing_idx != -1 and needs_cast:
        typing_line = lines[typing_idx]
        if 'cast' not in typing_line:
            # Add cast to typing imports
            typing_line = typing_line.rstrip()
            if typing_line.endswith(')'):
                # Multi-line or has parens
                typing_line = typing_line[:-1] + ', cast)'
            else:
                typing_line = typing_line + ', cast'
            lines[typing_idx] = typing_line
    
    # Reconstruct import line
    lines[import_idx] = f"from ..shared.solid_payload import {', '.join(imports)}"
    
    return '\n'.join(lines)


def fix_faces_casting(content: str, lines_to_fix: list[int]) -> str:
    """Add cast(List[Face], faces) to problematic lines."""
    lines = content.split('\n')
    
    for line_num in lines_to_fix:
        if line_num >= len(lines):
            continue
        line = lines[line_num]
        
        # Pattern: faces=faces,
        if 'faces=faces,' in line and 'cast(' not in line:
            lines[line_num] = line.replace('faces=faces,', 'faces=cast(List[Face], faces),')
        # Pattern: faces=faces)
        elif 'faces=faces)' in line and 'cast(' not in line:
            lines[line_num] = line.replace('faces=faces)', 'faces=cast(List[Face], faces))')
    
    return '\n'.join(lines)


def fix_metadata_casting(content: str, lines_to_fix: list[int]) -> str:
    """Add cast for metadata returns."""
    lines = content.split('\n')
    
    for line_num in lines_to_fix:
        if line_num >= len(lines):
            continue
        line = lines[line_num]
        
        # Pattern: return ComplexSolidResult(payload, payload.metadata)
        if 'payload.metadata)' in line and 'cast(' not in line:
            lines[line_num] = line.replace(
                'payload.metadata)',
                'cast(Dict[str, float], payload.metadata))'
            )
        # Pattern: return dict(self._result.payload.metadata)
        elif 'dict(self._result.payload.metadata)' in line and 'cast(' not in line:
            lines[line_num] = line.replace(
                'return dict(self._result.payload.metadata)',
                'return cast(dict[str, float], self._result.payload.metadata)'
            )
    
    return '\n'.join(lines)


def fix_vertex_list_annotations(content: str) -> str:
    """Add type annotations to vertex lists."""
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Pattern: v_prism = []
        if re.match(r'\s+v_\w+ = \[\]', line):
            var_name = re.search(r'v_(\w+)', line).group(0)
            lines[i] = line.replace('= []', f': List[Vec3] = []')
    
    return '\n'.join(lines)


def add_none_guards(content: str, lines_with_issues: list[tuple[int, str]]) -> str:
    """Add None guards before arithmetic operations in setters."""
    lines = content.split('\n')
    
    # Group consecutive errors (likely same setter)
    for line_num, msg in lines_with_issues:
        if line_num >= len(lines) or line_num < 2:
            continue
        
        # Check if we're in a setter (look back for 'elif key ==')
        in_setter = False
        setter_start = line_num
        for i in range(line_num - 1, max(0, line_num - 10), -1):
            if 'elif key ==' in lines[i]:
                in_setter = True
                setter_start = i
                break
        
        if not in_setter:
            continue
        
        # Check if guard already exists
        has_guard = False
        for i in range(setter_start, min(len(lines), line_num + 2)):
            if 'if value is None' in lines[i]:
                has_guard = True
                break
        
        if has_guard:
            continue
        
        # Add guard after the elif line
        indent = len(lines[setter_start]) - len(lines[setter_start].lstrip())
        guard_line = ' ' * (indent + 4) + 'if value is None:'
        return_line = ' ' * (indent + 8) + 'return False'
        
        # Insert guard
        lines.insert(setter_start + 1, guard_line)
        lines.insert(setter_start + 2, return_line)
    
    return '\n'.join(lines)


def process_file(file_path: Path, commit: bool = False) -> dict[str, int]:
    """Process a single file."""
    print(f"🔍 Analyzing {file_path.relative_to(REPO_ROOT)}...")
    
    # Run basedpyright
    output = run_basedpyright(file_path)
    diagnostics = output.get("generalDiagnostics", [])
    
    if not diagnostics:
        print("   ✅ No type errors")
        return {"fixed": 0, "errors": 0}
    
    # Read file
    content = file_path.read_text()
    original_content = content
    
    # Determine needed fixes
    needs_face = needs_face_import(diagnostics)
    needs_vec3 = needs_vec3_import(diagnostics)
    needs_cast_imp = needs_cast_import(diagnostics)
    
    # Apply fixes
    if needs_face or needs_vec3 or needs_cast_imp:
        content = fix_imports(content, needs_face, needs_vec3, needs_cast_imp)
    
    faces_lines = find_faces_assignments(content, diagnostics)
    if faces_lines:
        content = fix_faces_casting(content, faces_lines)
    
    metadata_lines = find_metadata_returns(content, diagnostics)
    if metadata_lines:
        content = fix_metadata_casting(content, metadata_lines)
    
    content = fix_vertex_list_annotations(content)
    
    none_lines = find_none_arithmetic_lines(diagnostics)
    if none_lines:
        content = add_none_guards(content, none_lines)
    
    # Check if anything changed
    if content == original_content:
        print(f"   ⚠️  {len(diagnostics)} errors, no automatic fixes available")
        return {"fixed": 0, "errors": len(diagnostics)}
    
    if commit:
        file_path.write_text(content)
        print(f"   ✅ Applied fixes, re-checking...")
        # Re-run to see remaining errors
        output = run_basedpyright(file_path)
        remaining = len(output.get("generalDiagnostics", []))
        fixed = len(diagnostics) - remaining
        print(f"   📊 Fixed {fixed} errors, {remaining} remaining")
        return {"fixed": fixed, "errors": remaining}
    else:
        print(f"   🔧 Would fix issues in {len(diagnostics)} error locations (dry run)")
        return {"fixed": 0, "errors": len(diagnostics)}


def main():
    parser = argparse.ArgumentParser(description="Auto-fix type contract violations")
    parser.add_argument(
        "--target",
        type=Path,
        default=REPO_ROOT / "src" / "pillars" / "geometry" / "services",
        help="Target file or directory"
    )
    parser.add_argument("--commit", action="store_true", help="Apply fixes")
    args = parser.parse_args()
    
    target = args.target.resolve()
    if not target.exists():
        print(f"❌ Target not found: {target}")
        sys.exit(1)
    
    print("=" * 60)
    print("THE RITE OF AUTOMATED CONTRACT RESTORATION")
    print("=" * 60)
    print(f"Mode: {'COMMIT' if args.commit else 'DRY RUN'}")
    print(f"Target: {target.relative_to(REPO_ROOT)}")
    print()
    
    # Collect files
    if target.is_file():
        files = [target]
    else:
        files = sorted(target.glob("*.py"))
        files = [f for f in files if f.name != "__init__.py"]
    
    # Process files
    total_fixed = 0
    total_errors = 0
    
    for file_path in files:
        result = process_file(file_path, args.commit)
        total_fixed += result["fixed"]
        total_errors += result["errors"]
    
    print()
    print("=" * 60)
    print(f"📊 Summary: {len(files)} files processed")
    if args.commit:
        print(f"✅ Fixed {total_fixed} type errors")
        print(f"⚠️  {total_errors} errors remaining")
    else:
        print(f"🔧 {total_errors} errors detected (use --commit to apply fixes)")
    print("=" * 60)


if __name__ == "__main__":
    main()
