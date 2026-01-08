#!/usr/bin/env python3
"""
Batch add formulas to geometry shapes.
This script adds LaTeX formulas to shape properties.
"""
import re
from pathlib import Path

# Complete formula definitions for each shape
SHAPE_FORMULAS = {
    'square_shape.py': {
        'side': r's',
        'perimeter': r'P = 4s',
        'area': r'A = s^2',
        'diagonal': r'd = s\sqrt{2}',
        'length': r'l',
        'width': r'w',
    },
    
    'ellipse_shape.py': {
        'semi_major_axis': r'a',
        'semi_minor_axis': r'b',
        'major_axis': r'2a',
        'minor_axis': r'2b',
        'area': r'A = \pi ab',
        'perimeter': r'P \approx \pi\left[3(a+b) - \sqrt{(3a+b)(a+3b)}\right]',
        'eccentricity': r'e = \sqrt{1 - \frac{b^2}{a^2}}',
        'focal_distance': r'c = \sqrt{a^2 - b^2}',
    },
    
    'annulus_shape.py': {
        'outer_radius': r'R',
        'inner_radius': r'r',
        'ring_width': r'w = R - r',
        'outer_diameter': r'D = 2R',
        'inner_diameter': r'd = 2r',
        'area': r'A = \pi(R^2 - r^2)',
        'outer_circumference': r'C_{outer} = 2\pi R',
        'inner_circumference': r'C_{inner} = 2\pi r',
        'radius_ratio': r'\rho = \frac{R}{r}',
    },
    
    'polygon_shape.py': {
        'side': r's',
        'perimeter': r'P = ns',
        'area': r'A = \frac{ns^2}{4\tan(\pi/n)}',
        'wedge_area': r'A_{wedge} = \frac{\pi r^2}{n}',
        'apothem': r'a = \frac{s}{2\tan(\pi/n)}',
        'circumradius': r'R = \frac{s}{2\sin(\pi/n)}',
        'incircle_circumference': r'C_{in} = 2\pi a',
        'circumcircle_circumference': r'C_{out} = 2\pi R',
        'interior_angle': r'\theta_{int} = \frac{(n-2) \cdot 180°}{n}',
        'exterior_angle': r'\theta_{ext} = \frac{360°}{n}',
    },
    
    'vesica_piscis_shape.py': {
        'radius': r'r',
        'diameter': r'd = 2r',
        'separation': r's = r',
        'lens_height': r'h = r\sqrt{3}',
        'lens_area': r'A = 2r^2\left(\frac{2\pi}{3} - \frac{\sqrt{3}}{2}\right)',
        'perimeter': r'P = 4r\arcsin\left(\frac{\sqrt{3}}{2}\right)',
        'apex_angle': r'\theta = 120°',
    },
}


def add_formula_to_property(content, property_key, formula):
    """Add formula parameter to a ShapeProperty definition."""
    
    # Find the property definition
    pattern = rf"(ShapeProperty\s*\(\s*name=['\"][^'\"]+['\"]\s*,\s*key=['\"]" + property_key + r"['\"]([^)]*?))(\s*\))"
    
    def replace_func(match):
        prop_start = match.group(1)
        existing_params = match.group(2)
        closing = match.group(3)
        
        # Check if formula already exists
        if 'formula=' in existing_params:
            return match.group(0)  # Don't modify
        
        # Add formula parameter
        # Clean up whitespace
        if existing_params.strip().endswith(','):
            new_prop = f"{prop_start},\n                formula=r'{formula}'{closing}"
        else:
            new_prop = f"{prop_start},\n                formula=r'{formula}'{closing}"
        
        return new_prop
    
    return re.sub(pattern, replace_func, content, flags=re.MULTILINE | re.DOTALL)


def update_shape_file(filepath, formulas):
    """Update a shape file with formulas."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    modified_count = 0
    
    for key, formula in formulas.items():
        new_content = add_formula_to_property(content, key, formula)
        if new_content != content:
            content = new_content
            modified_count += 1
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        return modified_count
    
    return 0


def main():
    """Main execution."""
    shapes_dir = Path('src/pillars/geometry/services')
    
    print("="*70)
    print("Batch Formula Addition")
    print("="*70)
    print()
    
    total_added = 0
    files_modified = 0
    
    for filename, formulas in SHAPE_FORMULAS.items():
        filepath = shapes_dir / filename
        
        if not filepath.exists():
            print(f"⚠ {filename} not found, skipping")
            continue
        
        count = update_shape_file(filepath, formulas)
        
        if count > 0:
            files_modified += 1
            total_added += count
            print(f"✓ {filename}: Added {count} formulas")
        else:
            print(f"  {filename}: No changes needed")
    
    print()
    print("="*70)
    print(f"Summary:")
    print(f"  Files modified: {files_modified}")
    print(f"  Total formulas added: {total_added}")
    print("="*70)


if __name__ == "__main__":
    import os
    os.chdir('/home/burkettdaniel927/projects/isopgem')
    main()
