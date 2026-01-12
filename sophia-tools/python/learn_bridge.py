#!/usr/bin/env python3
"""
Sophia Learn Bridge
Pattern recognition and self-improvement - track patterns and propose optimizations.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import Counter


LEARNING_LOG = ".sophia_learning.jsonl"


def load_learning_history(workspace: Path) -> List[Dict]:
    """Load historical learning events."""
    log_file = workspace / LEARNING_LOG
    if not log_file.exists():
        return []
    
    events = []
    try:
        for line in log_file.read_text().split('\n'):
            if line.strip():
                events.append(json.loads(line))
    except Exception:
        return []
    
    return events


def record_event(workspace: Path, event_type: str, event_data: str) -> bool:
    """Record a learning event."""
    log_file = workspace / LEARNING_LOG
    
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "data": event_data
    }
    
    try:
        with log_file.open('a') as f:
            f.write(json.dumps(event) + '\n')
        return True
    except Exception:
        return False


def detect_patterns(history: List[Dict], new_event_type: str) -> List[str]:
    """Detect recurring patterns in learning history."""
    patterns = []
    
    # Count event types
    type_counts = Counter(e['type'] for e in history)
    
    if new_event_type in type_counts:
        count = type_counts[new_event_type] + 1
        if count >= 3:
            patterns.append(f"{new_event_type} has occurred {count} times - consider systematic fix")
    
    # Check for seal failures
    seal_failures = [e for e in history if e['type'] == 'seal_failure']
    if len(seal_failures) >= 3:
        seal_types = Counter(json.loads(e['data']).get('seal', 'unknown') for e in seal_failures)
        for seal, count in seal_types.most_common(1):
            if count >= 2:
                patterns.append(f"Seal '{seal}' fails frequently ({count}x) - review process")
    
    # Check for repeated consultations
    consultations = [e for e in history if e['type'] == 'consultation']
    if len(consultations) >= 5:
        topics = Counter(json.loads(e['data']).get('topic', 'unknown') for e in consultations)
        for topic, count in topics.most_common(1):
            if count >= 3:
                patterns.append(f"Frequently consult '{topic}' ({count}x) - consider adding quick-ref")
    
    # Check for efficiency trends
    completions = [e for e in history if e['type'] == 'task_completion']
    if len(completions) >= 10:
        recent = completions[-10:]
        avg_recent = sum(json.loads(e['data']).get('duration', 0) for e in recent) / len(recent)
        older = completions[-20:-10] if len(completions) >= 20 else []
        if older:
            avg_older = sum(json.loads(e['data']).get('duration', 0) for e in older) / len(older)
            if avg_recent < avg_older * 0.8:
                patterns.append(f"Efficiency improving: {int((1 - avg_recent/avg_older) * 100)}% faster")
    
    return patterns


def generate_recommendations(patterns: List[str], event_type: str, event_data: str) -> List[str]:
    """Generate recommendations based on patterns."""
    recommendations = []
    
    try:
        data = json.loads(event_data) if event_data.startswith('{') else {}
    except:
        data = {}
    
    # Recommendations based on event type
    if event_type == 'seal_failure':
        seal = data.get('seal', '')
        if seal == 'sovereignty':
            recommendations.append("Consider running sophia_trace before refactoring to prevent import violations")
        elif seal == 'ui_purity':
            recommendations.append("Add UI purity check to pre-commit workflow")
        elif seal == 'dual_inscription':
            recommendations.append("Run sync_covenant.py script after covenant edits")
    
    if event_type == 'performance_issue':
        recommendations.append("Profile with sophia_research to identify bottlenecks")
        recommendations.append("Check for O(n²) patterns and database N+1 queries")
    
    if event_type == 'consultation' and 'sovereignty' in event_data.lower():
        recommendations.append("Consider adding pillar sovereignty rules to persona scroll quick-ref")
    
    # Pattern-based recommendations
    for pattern in patterns:
        if 'fails frequently' in pattern:
            recommendations.append("Propose adding automated pre-check to relevant workflow")
        elif 'Frequently consult' in pattern:
            recommendations.append("Consider adding frequently-consulted info to AI_QUICK_REFERENCE")
    
    if not recommendations:
        recommendations.append("Pattern recorded for future analysis")
    
    return recommendations


def generate_summary(patterns: List[str], history: List[Dict]) -> str:
    """Generate learning summary."""
    total_events = len(history) + 1
    unique_types = len(set(e['type'] for e in history))
    
    if patterns:
        return f"Recorded. {total_events} events tracked, {unique_types} types. {len(patterns)} pattern(s) detected."
    else:
        return f"Recorded. {total_events} events tracked. Monitoring for patterns."


def main():
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    event_type = sys.argv[2]
    event_data = sys.argv[3]
    
    # Load history
    history = load_learning_history(workspace_root)
    
    # Record event
    recorded = record_event(workspace_root, event_type, event_data)
    
    # Detect patterns
    patterns = detect_patterns(history, event_type)
    
    # Generate recommendations
    recommendations = generate_recommendations(patterns, event_type, event_data)
    
    # Generate summary
    summary = generate_summary(patterns, history)
    
    result = {
        "event_type": event_type,
        "recorded": recorded,
        "patterns_detected": patterns,
        "recommendations": recommendations,
        "learning_summary": summary
    }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
