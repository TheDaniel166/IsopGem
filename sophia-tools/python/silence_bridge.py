#!/usr/bin/env python3
"""
Sophia Silence Bridge
Cognitive Load Guardian

"This file is correct, but hostile to understanding."

This tool measures the violence that complexity does to human cognition.
It does not simplify code. It protects the mind.
"""

import sys
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter


def count_concepts(file_path: Path) -> int:
    """Count distinct concepts that must be held in mind."""
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
        
        concepts = set()
        
        # Class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                concepts.add(f"class:{node.name}")
            elif isinstance(node, ast.FunctionDef):
                concepts.add(f"function:{node.name}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    concepts.add(f"import:{alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    concepts.add(f"from:{node.module}")
        
        # External dependencies (imports from other modules)
        imports = re.findall(r'from\s+(\S+)\s+import', content)
        imports += re.findall(r'import\s+(\S+)', content)
        
        # Add unique module references
        for imp in imports:
            base_module = imp.split('.')[0]
            concepts.add(f"module:{base_module}")
        
        return len(concepts)
    except Exception:
        return 0


def measure_indirection_depth(file_path: Path) -> int:
    """Measure layers of abstraction required for comprehension."""
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
        
        max_depth = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Inheritance depth
                if node.bases:
                    max_depth = max(max_depth, len(node.bases))
                
                # Method nesting depth
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # Count nested function calls
                        call_depth = 0
                        for subnode in ast.walk(item):
                            if isinstance(subnode, ast.Call):
                                # Count chained calls (a.b.c.d())
                                if isinstance(subnode.func, ast.Attribute):
                                    chain_length = 1
                                    current = subnode.func
                                    while isinstance(current, ast.Attribute):
                                        chain_length += 1
                                        current = current.value
                                    call_depth = max(call_depth, chain_length)
                        max_depth = max(max_depth, call_depth)
        
        # Decorator stacking (adds conceptual layers)
        decorator_depth = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if node.decorator_list:
                    decorator_depth = max(decorator_depth, len(node.decorator_list))
        
        max_depth = max(max_depth, decorator_depth)
        
        return max_depth
    except Exception:
        return 0


def count_cognitive_jumps(file_path: Path, workspace: Path) -> int:
    """Count how many other files you must read to understand this one."""
    try:
        content = file_path.read_text()
        
        # Extract local imports (from src.*)
        local_imports = re.findall(r'from\s+(src\.[^\s]+)\s+import', content)
        local_imports += re.findall(r'from\s+\.([\w.]+)\s+import', content)
        
        # Count unique local module references
        unique_local = set()
        for imp in local_imports:
            if not imp.startswith('src.'):
                # Relative import - try to resolve
                try:
                    rel_path = file_path.parent
                    parts = imp.split('.')
                    for part in parts:
                        if part:
                            rel_path = rel_path / part
                    unique_local.add(str(rel_path))
                except Exception:
                    pass
            else:
                unique_local.add(imp)
        
        return len(unique_local)
    except Exception:
        return 0


def detect_symbol_conflicts(file_path: Path) -> int:
    """Detect when same symbol name is used for different purposes."""
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
        
        # Track symbol names and their contexts
        symbols: Dict[str, List[str]] = defaultdict(list)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                symbols[node.name].append('function')
            elif isinstance(node, ast.ClassDef):
                symbols[node.name].append('class')
            elif isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    symbols[node.id].append('variable')
        
        # Count symbols used in multiple contexts
        conflicts = sum(1 for contexts in symbols.values() if len(set(contexts)) > 1)
        
        # Also check for parameter shadowing
        shadowing = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_names = {arg.arg for arg in node.args.args}
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Name) and isinstance(subnode.ctx, ast.Store):
                        if subnode.id in param_names:
                            shadowing += 1
        
        return conflicts + shadowing
    except Exception:
        return 0


def calculate_understanding_burden(
    concept_density: int,
    indirection: int,
    jumps: int,
    conflicts: int
) -> Tuple[str, int]:
    """
    Calculate cognitive burden score and categorize.
    
    Returns: (category, score)
    """
    # Weighted cognitive load formula
    score = (
        concept_density * 1.0 +
        indirection * 3.0 +  # Indirection is expensive
        jumps * 2.0 +  # Context switching is costly
        conflicts * 4.0  # Symbol confusion is dangerous
    )
    
    if score < 20:
        return ("gentle", int(score))
    elif score < 40:
        return ("moderate", int(score))
    elif score < 60:
        return ("demanding", int(score))
    elif score < 80:
        return ("severe", int(score))
    else:
        return ("hostile", int(score))


def analyze_cognitive_load(workspace: Path, target: str) -> List[Dict]:
    """Analyze cognitive load for Python files in target."""
    target_path = workspace / target
    
    if not target_path.exists():
        return []
    
    results = []
    
    # Analyze Python files
    python_files = list(target_path.rglob("*.py"))[:100]  # Limit for performance
    
    for py_file in python_files:
        if py_file.name.startswith('__'):
            continue
        
        concept_density = count_concepts(py_file)
        indirection = measure_indirection_depth(py_file)
        jumps = count_cognitive_jumps(py_file, workspace)
        conflicts = detect_symbol_conflicts(py_file)
        
        burden, score = calculate_understanding_burden(
            concept_density, indirection, jumps, conflicts
        )
        
        rel_path = py_file.relative_to(workspace)
        
        results.append({
            "file": str(rel_path),
            "concept_density": concept_density,
            "indirection_depth": indirection,
            "cognitive_jumps": jumps,
            "symbol_reuse_conflicts": conflicts,
            "understanding_burden": burden,
            "cognitive_score": score
        })
    
    return results


def generate_verdicts(results: List[Dict]) -> List[str]:
    """Generate poetic but precise verdicts about cognitive violence."""
    verdicts = []
    
    # Find most hostile file
    if results:
        hostile = [r for r in results if r['understanding_burden'] == 'hostile']
        severe = [r for r in results if r['understanding_burden'] == 'severe']
        
        if hostile:
            worst = max(hostile, key=lambda x: x['cognitive_score'])
            verdicts.append(
                f"{worst['file']}: This file is correct, but hostile to understanding. "
                f"Cognitive load: {worst['cognitive_score']}."
            )
        
        if severe:
            for file_info in severe[:2]:
                verdicts.append(
                    f"{file_info['file']}: Demands {file_info['concept_density']} concepts "
                    f"across {file_info['indirection_depth']} layers. Understanding requires violence."
                )
        
        # Check for excessive jumping
        high_jumpers = [r for r in results if r['cognitive_jumps'] > 10]
        if high_jumpers:
            worst_jumper = max(high_jumpers, key=lambda x: x['cognitive_jumps'])
            verdicts.append(
                f"{worst_jumper['file']}: Requires reading {worst_jumper['cognitive_jumps']} "
                f"other files to comprehend. Context collapse is inevitable."
            )
        
        # Check for symbol chaos
        conflicted = [r for r in results if r['symbol_reuse_conflicts'] > 3]
        if conflicted:
            verdicts.append(
                f"Symbol confusion detected in {len(conflicted)} files. "
                f"Names lie about their purpose."
            )
        
        # Overall assessment
        total_files = len(results)
        hostile_count = len([r for r in results if r['understanding_burden'] in ['hostile', 'severe']])
        
        if hostile_count == 0:
            verdicts.append(
                f"Cognitive peace maintained across {total_files} files. "
                f"The codebase respects human understanding."
            )
        elif hostile_count / total_files > 0.3:
            verdicts.append(
                f"Cognitive violence is systemic. {hostile_count}/{total_files} files "
                f"wage war on comprehension."
            )
        else:
            verdicts.append(
                f"Localized cognitive strain in {hostile_count}/{total_files} files. "
                f"Violence is contained but present."
            )
    
    return verdicts


def identify_hotspots(results: List[Dict]) -> List[str]:
    """Identify specific cognitive hotspots requiring attention."""
    hotspots = []
    
    # High concept density
    dense = [r for r in results if r['concept_density'] > 20]
    if dense:
        hotspots.append(
            f"Concept density crisis in {len(dense)} files "
            f"(max: {max(r['concept_density'] for r in dense)} concepts)"
        )
    
    # Deep indirection
    indirect = [r for r in results if r['indirection_depth'] > 4]
    if indirect:
        hotspots.append(
            f"Excessive indirection in {len(indirect)} files "
            f"(max depth: {max(r['indirection_depth'] for r in indirect)} layers)"
        )
    
    # Jump exhaustion
    jumpy = [r for r in results if r['cognitive_jumps'] > 8]
    if jumpy:
        hotspots.append(
            f"Context switching overload in {len(jumpy)} files "
            f"(max: {max(r['cognitive_jumps'] for r in jumpy)} file reads required)"
        )
    
    return hotspots


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    target = sys.argv[2]
    threshold = sys.argv[3] if len(sys.argv) > 3 else "medium"
    
    # Analyze cognitive load
    results = analyze_cognitive_load(workspace_root, target)
    
    if not results:
        print(json.dumps({
            "error": f"No Python files found in {target}"
        }))
        sys.exit(1)
    
    # Categorize by burden
    hostile = [r for r in results if r['understanding_burden'] == 'hostile']
    severe = [r for r in results if r['understanding_burden'] == 'severe']
    demanding = [r for r in results if r['understanding_burden'] == 'demanding']
    
    # Generate analysis
    verdicts = generate_verdicts(results)
    hotspots = identify_hotspots(results)
    
    result = {
        "target": target,
        "total_files_analyzed": len(results),
        "hostile_files": hostile,
        "severe_files": severe,
        "moderate_files": demanding,
        "cognitive_hotspots": hotspots,
        "verdicts": verdicts
    }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
