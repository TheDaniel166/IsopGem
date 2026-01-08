#!/usr/bin/env python3
"""
Script to add LaTeX formulas to geometry shape properties.
Provides common formulas for standard geometric shapes.
"""
import os
import sys
import re
from pathlib import Path

# Formula library for common shapes
FORMULA_LIBRARY = {
    'rectangle': {
        'length': r'l',
        'width': r'w',
        'perimeter': r'P = 2(l + w)',
        'area': r'A = l \times w',
        'diagonal': r'd = \sqrt{l^2 + w^2}',
    },
    'square': {
        'side': r's',
        'perimeter': r'P = 4s',
        'area': r'A = s^2',
        'diagonal': r'd = s\sqrt{2}',
    },
    'ellipse': {
        'semi_major': r'a \text{ (semi-major axis)}',
        'semi_minor': r'b \text{ (semi-minor axis)}',
        'area': r'A = \pi ab',
        'perimeter': r'P \approx \pi(3(a+b) - \sqrt{(3a+b)(a+3b)})', # Ramanujan approximation
        'eccentricity': r'e = \sqrt{1 - \frac{b^2}{a^2}}',
    },
    'triangle': {
        'side_a': r'a',
        'side_b': r'b',
        'side_c': r'c',
        'perimeter': r'P = a + b + c',
        'semiperimeter': r's = \frac{a + b + c}{2}',
        'area': r'A = \sqrt{s(s-a)(s-b)(s-c)} \text{ (Heron)}',
        'area_base_height': r'A = \frac{1}{2}bh',
    },
    'polygon': {
        'sides': r'n \text{ (number of sides)}',
        'side_length': r's',
        'perimeter': r'P = ns',
        'area': r'A = \frac{ns^2}{4\tan(\pi/n)}',
        'interior_angle': r'\theta = \frac{(n-2) \times 180°}{n}',
        'apothem': r'a = \frac{s}{2\tan(\pi/n)}',
        'circumradius': r'R = \frac{s}{2\sin(\pi/n)}',
    },
    'annulus': {
        'outer_radius': r'R \text{ (outer)}',
        'inner_radius': r'r \text{ (inner)}',
        'area': r'A = \pi(R^2 - r^2)',
        'width': r'w = R - r',
    },
    'vesica_piscis': {
        'radius': r'r',
        'area': r'A = 2r^2(\frac{2\pi}{3} - \frac{\sqrt{3}}{2})',
        'height': r'h = r\sqrt{3}',
        'width': r'w = r',
    }
}


def analyze_shape_file(filepath):
    """Analyze a shape file to find properties without formulas."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find all ShapeProperty definitions
    pattern = r"ShapeProperty\s*\(\s*name=['\"]([^'\"]+)['\"]\s*,\s*key=['\"]([\w_]+)['\"]([^)]*)\)"
    matches = re.finditer(pattern, content)
    
    properties = []
    for match in matches:
        name = match.group(1)
        key = match.group(2)
        rest = match.group(3)
        
        has_formula = 'formula=' in rest
        
        properties.append({
            'name': name,
            'key': key,
            'has_formula': has_formula,
            'line': content[:match.start()].count('\n') + 1
        })
    
    return properties


def suggest_formulas(shape_name, properties):
    """Suggest formulas for properties based on shape type."""
    suggestions = {}
    
    # Normalize shape name
    shape_key = shape_name.lower().replace('shape', '').strip()
    
    if shape_key in FORMULA_LIBRARY:
        formulas = FORMULA_LIBRARY[shape_key]
        for prop in properties:
            key = prop['key']
            if key in formulas:
                suggestions[key] = formulas[key]
    
    return suggestions


def generate_report():
    """Generate a report of all shapes and their formula status."""
    shapes_dir = Path('src/pillars/geometry/services')
    
    print("="*70)
    print("Geometry Shape Formula Coverage Report")
    print("="*70)
    print()
    
    total_shapes = 0
    total_properties = 0
    properties_with_formulas = 0
    
    for shape_file in sorted(shapes_dir.glob('*_shape.py')):
        if shape_file.name == 'base_shape.py':
            continue
        
        total_shapes += 1
        shape_name = shape_file.stem.replace('_', ' ').title()
        
        properties = analyze_shape_file(shape_file)
        if not properties:
            continue
        
        total_properties += len(properties)
        with_formulas = sum(1 for p in properties if p['has_formula'])
        properties_with_formulas += with_formulas
        
        coverage = (with_formulas / len(properties) * 100) if properties else 0
        
        status = "✓" if coverage == 100 else "⚠" if coverage > 0 else "✗"
        
        print(f"{status} {shape_name}")
        print(f"   File: {shape_file.name}")
        print(f"   Coverage: {with_formulas}/{len(properties)} properties ({coverage:.0f}%)")
        
        # Show properties without formulas
        missing = [p for p in properties if not p['has_formula']]
        if missing:
            print(f"   Missing formulas:")
            for prop in missing:
                print(f"      - {prop['name']} (key: {prop['key']})")
            
            # Check if we have suggestions
            suggestions = suggest_formulas(shape_file.stem, properties)
            if suggestions:
                print(f"   Suggested formulas:")
                for key, formula in suggestions.items():
                    print(f"      - {key}: {formula}")
        
        print()
    
    # Summary
    print("="*70)
    print(f"Summary:")
    print(f"  Total shapes: {total_shapes}")
    print(f"  Total properties: {total_properties}")
    print(f"  Properties with formulas: {properties_with_formulas}")
    print(f"  Overall coverage: {properties_with_formulas/total_properties*100:.1f}%")
    print("="*70)


if __name__ == "__main__":
    os.chdir('/home/burkettdaniel927/projects/isopgem')
    generate_report()
