#!/usr/bin/env python3
"""
Sophia Research Bridge
Deep autonomous investigation - comprehensive analysis without bothering the user.
"""

import sys
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any


def trace_imports(workspace: Path, target: str) -> Dict[str, List[str]]:
    """Trace import relationships."""
    target_path = workspace / target
    if not target_path.exists():
        return {}
    
    import_graph = {}
    files = list(target_path.rglob("*.py"))[:50] if target_path.is_dir() else [target_path]
    
    for filepath in files:
        try:
            content = filepath.read_text()
            imports = re.findall(r'from\s+([\w\.]+)|import\s+([\w\.]+)', content)
            rel_path = str(filepath.relative_to(workspace))
            import_graph[rel_path] = [imp[0] or imp[1] for imp in imports][:10]
        except Exception:
            continue
    
    return import_graph


def scan_for_patterns(workspace: Path, target: str, pattern_type: str) -> List[str]:
    """Scan for specific code patterns."""
    findings = []
    target_path = workspace / target
    
    if not target_path.exists():
        return findings
    
    patterns = {
        'performance': [
            (r'for\s+\w+\s+in.*for\s+\w+\s+in', 'Nested loop (O(n²) risk)'),
            (r'\.append\(.*for.*\)', 'List comprehension in loop'),
            (r'time\.sleep\(', 'Blocking sleep detected')
        ],
        'threading': [
            (r'QThread|threading\.Thread', 'Threading usage found'),
            (r'\.emit\(', 'Signal emission'),
            (r'QTimer', 'Timer usage')
        ],
        'database': [
            (r'session\.query|db\.query', 'Database query'),
            (r'session\.commit', 'Database commit'),
            (r'SELECT\s+\*', 'SELECT * query (potential performance issue)')
        ]
    }
    
    if pattern_type not in patterns:
        return findings
    
    files = list(target_path.rglob("*.py"))[:30]
    
    for filepath in files:
        try:
            content = filepath.read_text()
            for pattern, description in patterns[pattern_type]:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    rel_path = filepath.relative_to(workspace)
                    findings.append(f"{rel_path}:{line_num} - {description}")
        except Exception:
            continue
    
    return findings[:20]


def check_covenant_rules(workspace: Path, target: str) -> List[str]:
    """Check specific covenant rules against target."""
    violations = []
    target_path = workspace / target
    
    if not target_path.exists():
        return violations
    
    # Check UI purity
    if 'ui' in str(target_path):
        forbidden = ['sqlalchemy', 'pandas', 'requests', 'httpx']
        files = list(target_path.rglob("*.py"))
        
        for filepath in files:
            try:
                content = filepath.read_text()
                for lib in forbidden:
                    if f"import {lib}" in content or f"from {lib}" in content:
                        rel_path = filepath.relative_to(workspace)
                        violations.append(f"UI Purity: {rel_path} imports {lib}")
            except Exception:
                continue
    
    return violations


def analyze_complexity(workspace: Path, target: str) -> Dict[str, Any]:
    """Analyze code complexity metrics."""
    target_path = workspace / target
    
    if not target_path.exists():
        return {}
    
    stats = {
        "total_files": 0,
        "total_lines": 0,
        "function_count": 0,
        "class_count": 0,
        "avg_file_size": 0
    }
    
    files = list(target_path.rglob("*.py"))
    stats["total_files"] = len(files)
    
    for filepath in files[:100]:
        try:
            content = filepath.read_text()
            lines = content.split('\n')
            stats["total_lines"] += len(lines)
            stats["function_count"] += len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE))
            stats["class_count"] += len(re.findall(r'^\s*class\s+\w+', content, re.MULTILINE))
        except Exception:
            continue
    
    if stats["total_files"] > 0:
        stats["avg_file_size"] = stats["total_lines"] // stats["total_files"]
    
    return stats


def synthesize_root_cause(question: str, findings: Dict[str, Any]) -> str:
    """Synthesize findings into root cause analysis."""
    question_lower = question.lower()
    
    if 'slow' in question_lower or 'performance' in question_lower:
        perf_issues = findings.get('performance_patterns', [])
        if perf_issues:
            return f"Performance issues detected: {len(perf_issues)} potential bottlenecks found including nested loops and blocking operations."
        return "No obvious performance anti-patterns detected in static analysis."
    
    if 'error' in question_lower or 'fail' in question_lower:
        violations = findings.get('covenant_violations', [])
        if violations:
            return f"Covenant violations detected: {', '.join(violations[:2])}"
        return "No covenant violations found. Issue may be runtime-specific."
    
    if 'dependency' in question_lower or 'import' in question_lower:
        import_count = len(findings.get('import_graph', {}))
        return f"Analyzed {import_count} files. Check import_graph for circular dependencies."
    
    return "Investigation complete. Review findings for detailed analysis."


def generate_recommendations(question: str, findings: Dict[str, Any]) -> List[str]:
    """Generate actionable recommendations."""
    recommendations = []
    question_lower = question.lower()
    
    perf_issues = findings.get('performance_patterns', [])
    if perf_issues:
        recommendations.append(f"Refactor {len(perf_issues)} identified performance hotspots")
        recommendations.append("Consider profiling with cProfile for runtime analysis")
    
    violations = findings.get('covenant_violations', [])
    if violations:
        recommendations.append("Fix covenant violations before proceeding")
        recommendations.append("Run sophia_seal to verify corrections")
    
    complexity = findings.get('complexity', {})
    if complexity.get('avg_file_size', 0) > 500:
        recommendations.append("High file complexity: consider splitting large files")
    
    if 'ui' in question_lower:
        recommendations.append("Verify all long operations are off UI thread")
        recommendations.append("Check signal/slot connections for proper thread affinity")
    
    if not recommendations:
        recommendations.append("No critical issues found. Proceed with planned changes.")
    
    return recommendations


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    question = sys.argv[2]
    depth = sys.argv[3] if len(sys.argv) > 3 else "standard"
    
    # Extract target from question
    question_lower = question.lower()
    target = "src"
    
    # Try to identify target from question
    for word in question_lower.split():
        potential_path = workspace_root / word
        if potential_path.exists():
            target = word
            break
        
        # Check pillars
        pillar_path = workspace_root / "src" / "pillars" / word
        if pillar_path.exists():
            target = f"src/pillars/{word}"
            break
    
    # Investigation steps
    investigation_steps = [
        "Tracing import relationships",
        "Scanning for code patterns",
        "Checking covenant compliance",
        "Analyzing complexity metrics",
        "Synthesizing findings"
    ]
    
    # Perform investigation
    findings = {
        "import_graph": trace_imports(workspace_root, target),
        "performance_patterns": scan_for_patterns(workspace_root, target, "performance"),
        "threading_patterns": scan_for_patterns(workspace_root, target, "threading"),
        "database_patterns": scan_for_patterns(workspace_root, target, "database"),
        "covenant_violations": check_covenant_rules(workspace_root, target),
        "complexity": analyze_complexity(workspace_root, target)
    }
    
    root_cause = synthesize_root_cause(question, findings)
    recommendations = generate_recommendations(question, findings)
    
    # Determine confidence
    total_findings = sum(len(v) if isinstance(v, list) else 1 for v in findings.values())
    confidence = "high" if total_findings > 10 else "medium" if total_findings > 5 else "low"
    
    result = {
        "question": question,
        "investigation_steps": investigation_steps,
        "findings": findings,
        "root_cause": root_cause,
        "recommendations": recommendations,
        "confidence": confidence
    }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
