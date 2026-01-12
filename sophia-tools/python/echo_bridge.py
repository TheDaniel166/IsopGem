#!/usr/bin/env python3
"""
Sophia Echo Bridge
Meaning Drift & Semantic Corrosion Detection

"Most systems fail not because code breaks, but because words lie."

This tool guards the truth of names.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter


# Core concepts from the Covenant with their canonical meanings
CANONICAL_CONCEPTS = {
    "pillar": {
        "definition": "Sovereign architectural domain with complete independence",
        "must_have": ["models", "services", "repositories"],
        "must_not": ["import from other pillars directly"],
        "keywords": ["sovereign", "independent", "self-contained"]
    },
    "sovereignty": {
        "definition": "Architectural independence - no direct inter-pillar dependencies",
        "must_have": ["signal bus", "shared substrate"],
        "must_not": ["direct imports", "tight coupling"],
        "keywords": ["independence", "decoupling", "autonomy"]
    },
    "ui_purity": {
        "definition": "UI layer must not contain heavy computation or blocking I/O",
        "must_have": ["QThread for heavy work", "signals for communication"],
        "must_not": ["database queries", "network calls", "pandas/numpy"],
        "keywords": ["responsive", "non-blocking", "lightweight"]
    },
    "seal": {
        "definition": "Verification ritual that must pass before work is complete",
        "must_have": ["automated check", "pass/fail result"],
        "must_not": ["manual verification only"],
        "keywords": ["verification", "validation", "ritual"]
    },
    "grimoire": {
        "definition": "Documentation of a pillar's architecture and purpose",
        "must_have": ["purpose", "architecture", "sovereignty"],
        "must_not": ["implementation details only"],
        "keywords": ["documentation", "architecture", "intent"]
    }
}


def extract_concept_definitions(workspace: Path) -> Dict[str, str]:
    """Extract concept definitions from covenant and wiki."""
    definitions = {}
    
    # Check covenant scrolls
    covenant_dir = workspace / "wiki" / "00_foundations" / "covenant"
    if covenant_dir.exists():
        for scroll in covenant_dir.glob("*.md"):
            try:
                content = scroll.read_text()
                # Find definition patterns: **X**: definition
                patterns = re.findall(r'\*\*([^*]+)\*\*:\s*(.+?)(?:\n|$)', content)
                for name, definition in patterns:
                    name_clean = name.lower().strip()
                    if len(definition) > 20:  # Meaningful definitions
                        definitions[name_clean] = definition[:200]
            except Exception:
                continue
    
    return definitions


def scan_concept_usage(workspace: Path, concept: str) -> List[Dict]:
    """Scan how a concept is actually used in code."""
    usages = []
    src_root = workspace / "src"
    
    if not src_root.exists():
        return usages
    
    # Search for the concept in code
    concept_pattern = re.compile(r'\b' + re.escape(concept) + r'\b', re.IGNORECASE)
    
    for py_file in list(src_root.rglob("*.py"))[:100]:
        try:
            content = py_file.read_text()
            
            # Find usages with context
            for match in concept_pattern.finditer(content):
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end]
                
                # Extract the line containing the match
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                if line_end == -1:
                    line_end = len(content)
                line = content[line_start:line_end].strip()
                
                rel_path = py_file.relative_to(workspace)
                usages.append({
                    "file": str(rel_path),
                    "line": line,
                    "context": context
                })
        except Exception:
            continue
    
    return usages[:20]  # Limit results


def detect_semantic_drift(concept: str, canonical: Dict, usages: List[Dict]) -> List[Dict]:
    """Detect if actual usage drifts from canonical meaning."""
    drifts = []
    
    if not usages:
        return drifts
    
    # Check for contradictory usage patterns
    usage_contexts = [u['context'].lower() for u in usages]
    
    # Type 1: Forbidden patterns detected
    must_not = canonical.get('must_not', [])
    for forbidden in must_not:
        forbidden_lower = forbidden.lower()
        violations = [u for u in usages if forbidden_lower in u['context'].lower()]
        
        if violations:
            drifts.append({
                "concept": concept,
                "original_meaning": canonical['definition'],
                "current_usage": [v['line'] for v in violations[:3]],
                "drift_type": "violation",
                "severity": "high",
                "evidence": [f"{v['file']}: {v['line'][:60]}" for v in violations[:2]]
            })
    
    # Type 2: Required patterns missing
    must_have = canonical.get('must_have', [])
    for required in must_have:
        required_lower = required.lower()
        found = any(required_lower in ctx for ctx in usage_contexts)
        
        if not found and len(usages) > 3:
            drifts.append({
                "concept": concept,
                "original_meaning": canonical['definition'],
                "current_usage": ["Pattern not found in implementation"],
                "drift_type": "missing_essence",
                "severity": "medium",
                "evidence": [f"Expected '{required}' but not found in {len(usages)} usages"]
            })
    
    # Type 3: Semantic expansion (concept used in too many different contexts)
    if len(set(u['file'].split('/')[2] if len(u['file'].split('/')) > 2 else 'root' for u in usages)) > 5:
        drifts.append({
            "concept": concept,
            "original_meaning": canonical['definition'],
            "current_usage": ["Used across many domains"],
            "drift_type": "semantic_diffusion",
            "severity": "low",
            "evidence": [f"Concept appears in {len(set(u['file'] for u in usages))} different files"]
        })
    
    return drifts


def detect_naming_contradictions(workspace: Path) -> List[str]:
    """Find names that have contradictory meanings in different contexts."""
    fractures = []
    src_root = workspace / "src"
    
    if not src_root.exists():
        return fractures
    
    # Common semantic fracture patterns
    patterns = [
        (r'class\s+(\w+)Manager', "Manager class (god object risk)"),
        (r'class\s+(\w+)Helper', "Helper class (unclear responsibility)"),
        (r'class\s+(\w+)Util', "Util class (dumping ground risk)"),
        (r'def\s+handle_(\w+)', "Handle method (vague intent)"),
        (r'def\s+process_(\w+)', "Process method (unclear transformation)"),
        (r'def\s+do_(\w+)', "Do method (weak naming)")
    ]
    
    for py_file in list(src_root.rglob("*.py"))[:50]:
        try:
            content = py_file.read_text()
            
            for pattern, description in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    rel_path = py_file.relative_to(workspace)
                    for match in matches[:2]:
                        fractures.append(f"{rel_path}: {description} - '{match}'")
        except Exception:
            continue
    
    return fractures[:10]


def check_metaphor_vs_mechanism(workspace: Path, concept: str) -> bool:
    """Determine if a concept is still a mechanism or has become just a metaphor."""
    src_root = workspace / "src"
    
    if not src_root.exists():
        return False
    
    # If a concept appears in comments/docstrings more than in actual code, it's metaphor
    comment_count = 0
    code_count = 0
    
    concept_pattern = re.compile(r'\b' + re.escape(concept) + r'\b', re.IGNORECASE)
    
    for py_file in list(src_root.rglob("*.py"))[:30]:
        try:
            content = py_file.read_text()
            
            # Count in comments/docstrings
            comments = re.findall(r'#.*', content)
            docstrings = re.findall(r'""".*?"""', content, re.DOTALL)
            
            for comment in comments + docstrings:
                comment_count += len(concept_pattern.findall(comment))
            
            # Count in actual code (rough heuristic: not in strings or comments)
            code_lines = [line for line in content.split('\n') 
                         if not line.strip().startswith('#') 
                         and '"""' not in line]
            code_text = '\n'.join(code_lines)
            code_count += len(concept_pattern.findall(code_text))
        except Exception:
            continue
    
    # If 70%+ of mentions are in comments, it's become metaphor
    total = comment_count + code_count
    return total > 0 and (comment_count / total) > 0.7


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    concept = sys.argv[2]
    scope = sys.argv[3] if len(sys.argv) > 3 else "code"
    
    # Get canonical definitions
    extracted_defs = extract_concept_definitions(workspace_root)
    
    # Determine which concepts to check
    if concept == "all":
        concepts_to_check = list(CANONICAL_CONCEPTS.keys())
    else:
        concepts_to_check = [concept.lower()]
    
    all_drifts = []
    
    # Check each concept
    for check_concept in concepts_to_check:
        if check_concept in CANONICAL_CONCEPTS:
            canonical = CANONICAL_CONCEPTS[check_concept]
            usages = scan_concept_usage(workspace_root, check_concept)
            drifts = detect_semantic_drift(check_concept, canonical, usages)
            all_drifts.extend(drifts)
            
            # Check if concept is becoming metaphor
            if usages and check_metaphor_vs_mechanism(workspace_root, check_concept):
                all_drifts.append({
                    "concept": check_concept,
                    "original_meaning": canonical['definition'],
                    "current_usage": ["Primarily metaphorical"],
                    "drift_type": "metaphor_drift",
                    "severity": "medium",
                    "evidence": ["Concept appears more in comments than implementation"]
                })
    
    # Detect naming contradictions
    fractures = detect_naming_contradictions(workspace_root)
    
    # Assess semantic health
    if not all_drifts:
        semantic_health = "aligned"
    elif sum(1 for d in all_drifts if d['severity'] == 'high') > 0:
        semantic_health = "corrupted"
    elif len(all_drifts) > 3:
        semantic_health = "drifting"
    else:
        semantic_health = "minor_drift"
    
    # Generate recommendations
    recommendations = []
    if any(d['drift_type'] == 'violation' for d in all_drifts):
        recommendations.append("Rename violating implementations or fix covenant definition")
    if any(d['drift_type'] == 'missing_essence' for d in all_drifts):
        recommendations.append("Restore missing architectural essence or update documentation")
    if any(d['drift_type'] == 'metaphor_drift' for d in all_drifts):
        recommendations.append("Concept has become abstract - either implement or retire the term")
    if fractures:
        recommendations.append(f"Found {len(fractures)} weak naming patterns - consider more specific names")
    
    if not recommendations:
        recommendations.append("Semantic integrity maintained. Names tell the truth.")
    
    result = {
        "concept": concept,
        "semantic_health": semantic_health,
        "drifts_detected": all_drifts,
        "fractures": fractures,
        "recommendations": recommendations
    }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
