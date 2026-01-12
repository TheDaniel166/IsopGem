#!/usr/bin/env python3
"""
Sophia Threshold Bridge
The Guardian of Restraint

"Now is too early."

This tool exists to prevent premature intelligence.
Most AI systems fail because they act the moment they can.
Sophia knows when restraint is the higher intelligence.
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import re


def check_system_stability(workspace: Path, target: str) -> Tuple[str, str, float]:
    """Assess if the system is stable enough for major change."""
    try:
        target_path = workspace / target if target else workspace / "src"
        
        # Check git history for recent churn
        result = subprocess.run(
            ['git', 'log', '--oneline', '--since=1.week.ago', '--', str(target_path)],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        recent_commits = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        if recent_commits > 20:
            return "unstable", f"High churn: {recent_commits} commits in last week", 0.2
        elif recent_commits > 10:
            return "volatile", f"Moderate churn: {recent_commits} commits in last week", 0.5
        elif recent_commits > 0:
            return "stable", f"Low churn: {recent_commits} commits in last week", 0.9
        else:
            return "dormant", "No recent changes - may indicate abandonment or completion", 0.7
    except Exception:
        return "unknown", "Cannot assess git history", 0.5


def check_test_coverage(workspace: Path, target: str) -> Tuple[str, str, float]:
    """Assess if test coverage supports major refactoring."""
    try:
        target_path = workspace / target if target else workspace / "src"
        tests_dir = workspace / "tests"
        
        if not tests_dir.exists():
            return "absent", "No test directory found", 0.1
        
        # Count test files
        test_files = list(tests_dir.rglob("test_*.py"))
        src_files = list(target_path.rglob("*.py")) if target_path.exists() else []
        
        if not src_files:
            return "unknown", "Target has no Python files", 0.5
        
        # Rough coverage ratio
        coverage_ratio = len(test_files) / max(len(src_files), 1)
        
        if coverage_ratio > 0.8:
            return "comprehensive", f"{len(test_files)} tests for {len(src_files)} source files", 1.0
        elif coverage_ratio > 0.4:
            return "moderate", f"{len(test_files)} tests for {len(src_files)} source files", 0.6
        elif coverage_ratio > 0.1:
            return "sparse", f"{len(test_files)} tests for {len(src_files)} source files", 0.3
        else:
            return "minimal", f"Only {len(test_files)} tests for {len(src_files)} source files", 0.1
    except Exception:
        return "unknown", "Cannot assess test coverage", 0.5


def check_abstraction_readiness(workspace: Path, target: str, change_type: str) -> Tuple[str, str, float]:
    """Assess if system is ready for new abstraction layer."""
    try:
        target_path = workspace / target if target else workspace / "src"
        
        if not target_path.exists():
            return "unknown", "Target does not exist", 0.5
        
        py_files = list(target_path.rglob("*.py"))[:50]
        
        # Count existing abstraction patterns
        pattern_counts = {
            'base_classes': 0,
            'interfaces': 0,
            'factories': 0,
            'decorators': 0,
            'protocols': 0
        }
        
        for py_file in py_files:
            try:
                content = py_file.read_text()
                
                if re.search(r'class\s+\w+Base', content):
                    pattern_counts['base_classes'] += 1
                if re.search(r'class\s+\w+Interface', content) or re.search(r'from\s+abc\s+import', content):
                    pattern_counts['interfaces'] += 1
                if re.search(r'class\s+\w+Factory', content):
                    pattern_counts['factories'] += 1
                if re.search(r'@\w+', content):
                    pattern_counts['decorators'] += 1
                if re.search(r'from\s+typing\s+import.*Protocol', content):
                    pattern_counts['protocols'] += 1
            except Exception:
                continue
        
        total_patterns = sum(pattern_counts.values())
        
        # If proposing new abstraction but few exist, might be premature
        if 'abstract' in change_type.lower() or 'interface' in change_type.lower():
            if total_patterns < 3:
                return "premature", f"Only {total_patterns} abstraction patterns exist - too early", 0.2
            elif total_patterns < 8:
                return "emerging", f"{total_patterns} abstraction patterns - system maturing", 0.6
            else:
                return "ready", f"{total_patterns} abstraction patterns - system can support more", 0.9
        
        # For other changes, existing abstractions are good
        if total_patterns > 15:
            return "saturated", f"{total_patterns} abstraction patterns - risk of over-engineering", 0.4
        
        return "balanced", f"{total_patterns} abstraction patterns present", 0.8
    except Exception:
        return "unknown", "Cannot assess abstraction readiness", 0.5


def check_dependency_maturity(workspace: Path, target: str) -> Tuple[str, str, float]:
    """Check if dependencies are stable."""
    try:
        # Check for recent changes to requirements or dependencies
        req_files = [
            workspace / "requirements.txt",
            workspace / "pyproject.toml",
            workspace / "setup.py"
        ]
        
        for req_file in req_files:
            if req_file.exists():
                result = subprocess.run(
                    ['git', 'log', '--oneline', '--since=2.weeks.ago', '--', str(req_file)],
                    cwd=workspace,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.stdout.strip():
                    return "volatile", "Dependencies changed recently", 0.4
        
        return "stable", "No recent dependency changes", 0.9
    except Exception:
        return "unknown", "Cannot assess dependency maturity", 0.5


def check_technical_debt(workspace: Path, target: str) -> Tuple[str, str, float]:
    """Assess technical debt load."""
    try:
        target_path = workspace / target if target else workspace / "src"
        
        if not target_path.exists():
            return "unknown", "Target does not exist", 0.5
        
        py_files = list(target_path.rglob("*.py"))[:50]
        
        # Look for debt indicators
        debt_markers = {
            'TODO': 0,
            'FIXME': 0,
            'HACK': 0,
            'XXX': 0,
            'DEBT': 0
        }
        
        for py_file in py_files:
            try:
                content = py_file.read_text()
                for marker in debt_markers:
                    debt_markers[marker] += len(re.findall(rf'#.*{marker}', content))
            except Exception:
                continue
        
        total_debt = sum(debt_markers.values())
        debt_per_file = total_debt / max(len(py_files), 1)
        
        if debt_per_file > 3:
            return "heavy", f"{total_debt} debt markers across {len(py_files)} files", 0.2
        elif debt_per_file > 1:
            return "moderate", f"{total_debt} debt markers across {len(py_files)} files", 0.5
        elif debt_per_file > 0.2:
            return "light", f"{total_debt} debt markers across {len(py_files)} files", 0.8
        else:
            return "clean", f"Only {total_debt} debt markers across {len(py_files)} files", 1.0
    except Exception:
        return "unknown", "Cannot assess technical debt", 0.5


def check_pattern_consistency(workspace: Path, target: str) -> Tuple[str, str, float]:
    """Check if existing patterns are consistent - prerequisite for new patterns."""
    try:
        target_path = workspace / target if target else workspace / "src"
        
        if not target_path.exists():
            return "unknown", "Target does not exist", 0.5
        
        py_files = list(target_path.rglob("*.py"))[:30]
        
        # Check for consistent naming patterns
        class_names = []
        function_patterns = {
            'snake_case': 0,
            'camelCase': 0,
            'inconsistent': 0
        }
        
        for py_file in py_files:
            try:
                content = py_file.read_text()
                
                # Extract class names
                classes = re.findall(r'class\s+(\w+)', content)
                class_names.extend(classes)
                
                # Check function naming
                functions = re.findall(r'def\s+(\w+)', content)
                for func in functions:
                    if '_' in func and func.islower():
                        function_patterns['snake_case'] += 1
                    elif func[0].islower() and any(c.isupper() for c in func):
                        function_patterns['camelCase'] += 1
                    else:
                        function_patterns['inconsistent'] += 1
            except Exception:
                continue
        
        # Check consistency
        total_funcs = sum(function_patterns.values())
        if total_funcs == 0:
            return "unknown", "No functions found", 0.5
        
        dominant_pattern = max(function_patterns, key=function_patterns.get)
        consistency = function_patterns[dominant_pattern] / total_funcs
        
        if consistency > 0.9:
            return "consistent", f"{consistency*100:.0f}% pattern consistency", 0.9
        elif consistency > 0.7:
            return "mostly_consistent", f"{consistency*100:.0f}% pattern consistency", 0.7
        else:
            return "inconsistent", f"Only {consistency*100:.0f}% pattern consistency", 0.3
    except Exception:
        return "unknown", "Cannot assess pattern consistency", 0.5


def calculate_readiness(signals: List[Dict]) -> Tuple[float, str]:
    """Calculate overall readiness score and verdict."""
    weighted_sum = sum(s['weight'] * s['score'] for s in signals)
    total_weight = sum(s['weight'] for s in signals)
    
    score = weighted_sum / total_weight if total_weight > 0 else 0.5
    
    if score < 0.3:
        verdict = "too_early"
    elif score < 0.5:
        verdict = "risky"
    elif score < 0.7:
        verdict = "cautious_proceed"
    elif score < 0.85:
        verdict = "ready"
    else:
        verdict = "optimal"
    
    return score, verdict


def generate_recommendation(verdict: str, score: float, proposed_change: str) -> str:
    """Generate actionable recommendation."""
    if verdict == "too_early":
        return (
            f"Now is too early. The system is not ready for: {proposed_change}\n"
            f"Acting now increases entropy more than value.\n"
            f"Restraint is the higher intelligence."
        )
    elif verdict == "risky":
        return (
            f"High risk of premature action. Consider:\n"
            f"1. Stabilize current patterns first\n"
            f"2. Reduce technical debt\n"
            f"3. Establish test coverage\n"
            f"Then revisit: {proposed_change}"
        )
    elif verdict == "cautious_proceed":
        return (
            f"The system can support this change, but with caution.\n"
            f"Proceed incrementally. Watch for increased entropy.\n"
            f"Change: {proposed_change}"
        )
    elif verdict == "ready":
        return (
            f"The system is ready. Prerequisites are in place.\n"
            f"Proceed with confidence: {proposed_change}"
        )
    else:  # optimal
        return (
            f"This is the right time. The system invites this evolution.\n"
            f"All signals align: {proposed_change}"
        )


def assess_timing(signals: List[Dict]) -> str:
    """Assess whether timing is premature, optimal, or late."""
    stability = next((s for s in signals if s['factor'] == 'System Stability'), None)
    patterns = next((s for s in signals if s['factor'] == 'Pattern Consistency'), None)
    
    if stability and stability['status'] == 'unstable':
        return "Premature - system in flux"
    elif patterns and patterns['status'] == 'inconsistent':
        return "Premature - patterns not established"
    elif stability and stability['status'] == 'dormant':
        return "Possibly late - system may be complete or abandoned"
    else:
        return "Timing appropriate"


def project_entropy(verdict: str, signals: List[Dict]) -> str:
    """Project entropy impact of the change."""
    debt = next((s for s in signals if s['factor'] == 'Technical Debt'), None)
    abstractions = next((s for s in signals if s['factor'] == 'Abstraction Readiness'), None)
    
    if verdict in ["too_early", "risky"]:
        return "High entropy risk - change would increase chaos more than order"
    elif debt and debt['status'] in ['heavy', 'moderate']:
        return "Medium entropy risk - existing debt will compound"
    elif abstractions and abstractions['status'] == 'saturated':
        return "Medium entropy risk - additional abstraction may over-complicate"
    else:
        return "Low entropy risk - change aligns with system readiness"


def main():
    parser = argparse.ArgumentParser(description='Sophia Threshold - Guardian of Restraint')
    parser.add_argument('workspace_root', type=str)
    parser.add_argument('proposed_change', type=str)
    parser.add_argument('--target', type=str, default='src')
    parser.add_argument('--scope', type=str, choices=['minor', 'major', 'architectural'], default='major')
    
    args = parser.parse_args()
    workspace = Path(args.workspace_root)
    
    # Collect readiness signals
    signals = []
    
    # Weighted factors (architectural changes need higher bars)
    weights = {
        'stability': 2.0 if args.scope == 'architectural' else 1.5,
        'tests': 1.5 if args.scope == 'architectural' else 1.0,
        'abstractions': 2.0 if 'abstract' in args.proposed_change.lower() else 1.0,
        'dependencies': 1.0,
        'debt': 1.5,
        'patterns': 2.0 if args.scope == 'architectural' else 1.0
    }
    
    # Assess each factor
    status, reason, score = check_system_stability(workspace, args.target)
    signals.append({
        'factor': 'System Stability',
        'status': status,
        'reason': reason,
        'score': score,
        'weight': weights['stability']
    })
    
    status, reason, score = check_test_coverage(workspace, args.target)
    signals.append({
        'factor': 'Test Coverage',
        'status': status,
        'reason': reason,
        'score': score,
        'weight': weights['tests']
    })
    
    status, reason, score = check_abstraction_readiness(workspace, args.target, args.proposed_change)
    signals.append({
        'factor': 'Abstraction Readiness',
        'status': status,
        'reason': reason,
        'score': score,
        'weight': weights['abstractions']
    })
    
    status, reason, score = check_dependency_maturity(workspace, args.target)
    signals.append({
        'factor': 'Dependency Maturity',
        'status': status,
        'reason': reason,
        'score': score,
        'weight': weights['dependencies']
    })
    
    status, reason, score = check_technical_debt(workspace, args.target)
    signals.append({
        'factor': 'Technical Debt',
        'status': status,
        'reason': reason,
        'score': score,
        'weight': weights['debt']
    })
    
    status, reason, score = check_pattern_consistency(workspace, args.target)
    signals.append({
        'factor': 'Pattern Consistency',
        'status': status,
        'reason': reason,
        'score': score,
        'weight': weights['patterns']
    })
    
    # Calculate readiness
    readiness_score, verdict = calculate_readiness(signals)
    
    # Generate outputs
    recommendation = generate_recommendation(verdict, readiness_score, args.proposed_change)
    timing = assess_timing(signals)
    entropy = project_entropy(verdict, signals)
    
    # Format signals for output
    output_signals = [
        {
            'factor': s['factor'],
            'status': s['status'],
            'reason': s['reason'],
            'weight': s['weight']
        }
        for s in signals
    ]
    
    result = {
        'proposed_change': args.proposed_change,
        'verdict': verdict,
        'readiness_score': round(readiness_score, 2),
        'recommendation': recommendation,
        'signals': output_signals,
        'timing_assessment': timing,
        'entropy_projection': entropy
    }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
