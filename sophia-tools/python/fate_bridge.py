#!/usr/bin/env python3
"""
Sophia Fate Bridge
Structural Inevitability Detection - sees what must come to pass.

This is not linting. Not profiling. This is structural thermodynamics.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter


def build_dependency_graph(workspace: Path, target: str) -> Dict[str, Set[str]]:
    """Build complete dependency graph."""
    target_path = workspace / target
    if not target_path.exists():
        return {}
    
    graph = defaultdict(set)
    files = list(target_path.rglob("*.py"))[:200]  # Limit for performance
    
    for filepath in files:
        try:
            content = filepath.read_text()
            rel_path = str(filepath.relative_to(workspace))
            
            # Extract all imports
            imports = re.findall(r'from\s+([\w\.]+)|import\s+([\w\.]+)', content)
            for imp in imports:
                dep = (imp[0] or imp[1]).split('.')[0]
                if dep and not dep.startswith('_'):
                    graph[rel_path].add(dep)
        except Exception:
            continue
    
    return dict(graph)


def calculate_fan_metrics(graph: Dict[str, Set[str]]) -> Dict[str, Tuple[int, int]]:
    """Calculate fan-in (how many depend on X) and fan-out (how many X depends on)."""
    fan_in = Counter()
    fan_out = {}
    
    for module, deps in graph.items():
        fan_out[module] = len(deps)
        for dep in deps:
            fan_in[dep] += 1
    
    metrics = {}
    all_modules = set(graph.keys()) | set(fan_in.keys())
    for module in all_modules:
        metrics[module] = (fan_in.get(module, 0), fan_out.get(module, 0))
    
    return metrics


def detect_ossification_risk(fan_metrics: Dict[str, Tuple[int, int]]) -> List[Dict]:
    """Detect modules that will ossify due to high fan-in."""
    warnings = []
    
    for module, (fan_in, fan_out) in fan_metrics.items():
        # High fan-in = many things depend on it = will ossify
        if fan_in >= 10:
            entropy_score = min(100, fan_in * 5)
            warnings.append({
                "type": "ossification",
                "target": module,
                "inevitability": f"This module will harden. {fan_in} modules depend on it. Any change becomes expensive.",
                "evidence": [
                    f"Fan-in: {fan_in} (high dependency concentration)",
                    f"Fan-out: {fan_out}",
                    "Future cost of change grows linearly with dependents"
                ],
                "entropy_score": entropy_score
            })
        
        # High fan-out = depends on many things = fragile
        if fan_out >= 15:
            entropy_score = min(100, fan_out * 3)
            warnings.append({
                "type": "fragility",
                "target": module,
                "inevitability": f"This module will become fragile. It depends on {fan_out} modules. Breakage is inevitable.",
                "evidence": [
                    f"Fan-out: {fan_out} (high dependency count)",
                    "Exposed to transitive changes",
                    "Probability of upstream breakage: high"
                ],
                "entropy_score": entropy_score
            })
    
    return warnings


def detect_cycles(graph: Dict[str, Set[str]]) -> List[Dict]:
    """Detect dependency cycles that are stable but non-composable."""
    warnings = []
    
    # Simple cycle detection using DFS
    def find_cycle(start, visited, path):
        if start in path:
            cycle_start = path.index(start)
            return path[cycle_start:]
        if start in visited:
            return None
        
        visited.add(start)
        path.append(start)
        
        for dep in graph.get(start, []):
            cycle = find_cycle(dep, visited, path[:])
            if cycle:
                return cycle
        
        return None
    
    seen_cycles = set()
    for module in graph.keys():
        cycle = find_cycle(module, set(), [])
        if cycle:
            cycle_sig = tuple(sorted(cycle))
            if cycle_sig not in seen_cycles and len(cycle) > 1:
                seen_cycles.add(cycle_sig)
                warnings.append({
                    "type": "non_composable_cycle",
                    "target": " → ".join(cycle[:3]) + ("..." if len(cycle) > 3 else ""),
                    "inevitability": "This cycle is stable now but prevents future decomposition.",
                    "evidence": [
                        f"Cycle length: {len(cycle)}",
                        "Cannot extract components independently",
                        "Will resist refactoring"
                    ],
                    "entropy_score": min(100, len(cycle) * 10)
                })
    
    return warnings


def detect_semantic_sprawl(workspace: Path, target: str) -> List[Dict]:
    """Detect concepts appearing in too many semantic domains."""
    target_path = workspace / target
    if not target_path.exists():
        return []
    
    warnings = []
    
    # Track which "domains" (pillars/top-level dirs) each concept appears in
    concept_domains = defaultdict(set)
    files = list(target_path.rglob("*.py"))[:150]
    
    # Common important concepts to track
    tracked_concepts = [
        'database', 'session', 'query', 'config', 'cache', 'signal',
        'window', 'widget', 'service', 'repository', 'model'
    ]
    
    for filepath in files:
        try:
            content = filepath.read_text().lower()
            rel_path = str(filepath.relative_to(workspace))
            
            # Determine domain (e.g., src/pillars/astrology -> astrology)
            parts = rel_path.split('/')
            domain = parts[2] if len(parts) > 2 and parts[1] == 'pillars' else parts[1] if len(parts) > 1 else 'root'
            
            for concept in tracked_concepts:
                if concept in content:
                    concept_domains[concept].add(domain)
        except Exception:
            continue
    
    # Warn about concepts in too many domains
    for concept, domains in concept_domains.items():
        if len(domains) >= 5:
            warnings.append({
                "type": "semantic_sprawl",
                "target": f"concept '{concept}'",
                "inevitability": f"This concept appears in {len(domains)} domains. It will force global coordination.",
                "evidence": [
                    f"Appears in: {', '.join(sorted(domains)[:5])}",
                    "Changes require cross-domain alignment",
                    "Will become a coordination bottleneck"
                ],
                "entropy_score": min(100, len(domains) * 8)
            })
    
    return warnings


def detect_scale_traps(graph: Dict[str, Set[str]], fan_metrics: Dict[str, Tuple[int, int]]) -> List[Dict]:
    """Detect design decisions neutral now but terminal at scale."""
    warnings = []
    
    # Detect "God modules" - high fan-in + high fan-out
    for module, (fan_in, fan_out) in fan_metrics.items():
        if fan_in >= 8 and fan_out >= 8:
            warnings.append({
                "type": "scale_trap",
                "target": module,
                "inevitability": "This module is neutral now but terminal at scale. It connects too many concerns.",
                "evidence": [
                    f"Fan-in: {fan_in}, Fan-out: {fan_out}",
                    "Bi-directional complexity hub",
                    "Will become unmaintainable before appearing broken"
                ],
                "entropy_score": min(100, (fan_in + fan_out) * 2)
            })
    
    # Detect deep dependency chains
    max_depths = {}
    
    def calc_depth(module, visited=None):
        if visited is None:
            visited = set()
        if module in visited:
            return 0
        if module in max_depths:
            return max_depths[module]
        
        visited.add(module)
        deps = graph.get(module, set())
        if not deps:
            return 0
        
        depth = 1 + max((calc_depth(dep, visited.copy()) for dep in deps), default=0)
        max_depths[module] = depth
        return depth
    
    for module in graph.keys():
        depth = calc_depth(module)
        if depth >= 6:
            warnings.append({
                "type": "scale_trap",
                "target": module,
                "inevitability": f"Dependency depth of {depth}. Changes propagate through {depth} layers. Testing becomes exponential.",
                "evidence": [
                    f"Chain depth: {depth} levels",
                    "Transitive breakage risk compounds",
                    "Debugging cost grows non-linearly"
                ],
                "entropy_score": min(100, depth * 12)
            })
    
    return warnings


def calculate_structural_health(warnings: List[Dict]) -> int:
    """Calculate overall structural health (0-100, lower is worse)."""
    if not warnings:
        return 100
    
    total_entropy = sum(w['entropy_score'] for w in warnings)
    avg_entropy = total_entropy / len(warnings)
    
    # Health inversely proportional to entropy
    health = max(0, 100 - int(avg_entropy))
    return health


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    target = sys.argv[2]
    horizon = sys.argv[3] if len(sys.argv) > 3 else "medium"
    
    # Build dependency graph
    graph = build_dependency_graph(workspace_root, target)
    
    if not graph:
        result = {
            "target": target,
            "horizon": horizon,
            "warnings": [],
            "structural_health": 100,
            "summary": "No code structure detected for analysis"
        }
        print(json.dumps(result, indent=2))
        return
    
    # Calculate metrics
    fan_metrics = calculate_fan_metrics(graph)
    
    # Detect inevitabilities
    warnings = []
    warnings.extend(detect_ossification_risk(fan_metrics))
    warnings.extend(detect_cycles(graph))
    warnings.extend(detect_semantic_sprawl(workspace_root, target))
    warnings.extend(detect_scale_traps(graph, fan_metrics))
    
    # Sort by entropy (highest risk first)
    warnings.sort(key=lambda w: w['entropy_score'], reverse=True)
    
    # Limit based on horizon
    limits = {"short": 5, "medium": 10, "long": 20}
    warnings = warnings[:limits.get(horizon, 10)]
    
    # Calculate health
    health = calculate_structural_health(warnings)
    
    # Generate summary
    if health >= 80:
        summary = f"Structure is healthy. {len(warnings)} minor inevitabilities detected."
    elif health >= 60:
        summary = f"Structure shows entropy. {len(warnings)} inevitabilities will manifest."
    elif health >= 40:
        summary = f"Structure degrading. {len(warnings)} critical paths to ossification."
    else:
        summary = f"Structure approaching terminal state. {len(warnings)} inevitabilities in motion."
    
    result = {
        "target": target,
        "horizon": horizon,
        "warnings": warnings,
        "structural_health": health,
        "summary": summary
    }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
