#!/usr/bin/env python3
"""Fix broken variable names from automated type fixing"""
import sys
import re
from pathlib import Path

# Files and line numbers to fix
FIXES = [
    ("src/pillars/geometry/ui/figurate_3d_window.py", 308, r",_ ", ", _"),
    ("src/pillars/geometry/services/triangle_shape.py", 1606, r",_ ", ", _"),
    (" src/pillars/geometry/services/torus_knot_solid.py", 214, r",_ ", ", _"),
    ("src/pillars/astrology/ui/natal_chart_window.py", 471, r",_", ", _"),
    ("src/pillars/astrology/ui/synastry_aspects_widget.py", 138, r",_ ", ", _"),
    ("src/pillars/tq/services/amun_audio_service.py", 180, r",_ ", ", _"),
    ("src/pillars/correspondences/services/formula_engine.py", 514, r",_ ", ", _"),
    ("src/shared/services/ephemeris_provider.py", 233, r",_ ", ", _"),
    ("src/shared/services/ephemeris_provider.py", 286, r",_ ", ", _"),
]

REPO_ROOT = Path("/home/burkettdaniel927/projects/isopgem")

for file_path, line_num, pattern, replacement in FIXES:
    full_path = REPO_ROOT / file_path.strip()
    
    if not full_path.exists():
        print(f"❌ Not found: {full_path}")
        continue
    
    with open(full_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if line_num > len(lines):
        print(f"⚠️  Line {line_num} past EOF in {file_path}")
        continue
    
    idx = line_num - 1
    original = lines[idx]
    
    if pattern in original:
        fixed = original.replace(pattern, replacement)
        lines[idx] = fixed
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ Fixed {file_path}:{line_num}")
    else:
        print(f"⚠️  Pattern not found on line {line_num} in {file_path}")

print("\n✨ All fixes applied")
