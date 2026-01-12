#!/usr/bin/env python3
"""
Sophia Mirror Bridge
The Architect Reflecting Himself

"You have returned to this problem three times. The system may need a new axis."

Not to judge. To reflect.
Covenant-bound, not ego-driven.
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import re


PATTERNS_FILE = ".sophia_patterns.jsonl"


def track_revisits(workspace: Path, timeframe_days: int) -> List[Dict]:
    """Track files that are repeatedly edited - sign of unresolved tension."""
    try:
        since = f"{timeframe_days}.days.ago"
        result = subprocess.run(
            ['git', 'log', '--name-only', '--pretty=format:%H|%ad|%s', 
             f'--since={since}', '--date=iso'],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if not result.stdout:
            return []
        
        # Parse git log
        file_edits = defaultdict(list)
        current_commit = None
        
        for line in result.stdout.split('\n'):
            if '|' in line:
                # Commit line
                commit_hash, date, message = line.split('|', 2)
                current_commit = {'hash': commit_hash[:8], 'date': date, 'message': message}
            elif line.strip() and current_commit:
                # File line
                file_edits[line.strip()].append(current_commit)
        
        # Find files with multiple edits
        revisited = []
        for filepath, commits in file_edits.items():
            if len(commits) >= 3:  # Returned 3+ times
                # Check if commits are spread out (not just rapid iterations)
                dates = [datetime.fromisoformat(c['date'].replace(' +0000', '')) for c in commits]
                date_spread = (max(dates) - min(dates)).days
                
                if date_spread > 1:  # Spread over multiple days
                    revisited.append({
                        'file': filepath,
                        'visits': len(commits),
                        'spread_days': date_spread,
                        'commits': commits[:3],  # Sample
                        'messages': [c['message'] for c in commits[:3]]
                    })
        
        # Sort by visit frequency
        revisited.sort(key=lambda x: x['visits'], reverse=True)
        return revisited[:10]
    
    except Exception as e:
        return []


def detect_overbuilding(workspace: Path, timeframe_days: int) -> List[Dict]:
    """Detect areas where abstractions are being excessively added."""
    try:
        since = f"{timeframe_days}.days.ago"
        result = subprocess.run(
            ['git', 'log', '--all', '--numstat', '--pretty=format:%H|%s', f'--since={since}'],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if not result.stdout:
            return []
        
        # Track abstraction additions
        abstraction_growth = defaultdict(lambda: {'base_classes': 0, 'interfaces': 0, 'protocols': 0, 'factories': 0})
        current_message = ""
        
        for line in result.stdout.split('\n'):
            if '|' in line and not '\t' in line:
                current_message = line.split('|', 1)[1]
            elif '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    added, removed, filepath = parts
                    
                    # Check for abstraction keywords in commit message
                    message_lower = current_message.lower()
                    if any(word in message_lower for word in ['abstract', 'base', 'interface', 'protocol', 'factory']):
                        # Extract directory
                        file_path = Path(filepath)
                        if len(file_path.parts) >= 2:
                            directory = str(Path(file_path.parts[0]) / file_path.parts[1])
                            
                            # Count abstraction types
                            if 'base' in message_lower:
                                abstraction_growth[directory]['base_classes'] += 1
                            if 'interface' in message_lower or 'protocol' in message_lower:
                                abstraction_growth[directory]['interfaces'] += 1
                            if 'protocol' in message_lower:
                                abstraction_growth[directory]['protocols'] += 1
                            if 'factory' in message_lower:
                                abstraction_growth[directory]['factories'] += 1
        
        # Find areas with excessive abstraction growth
        overbuilt = []
        for directory, counts in abstraction_growth.items():
            total = sum(counts.values())
            if total >= 3:  # 3+ abstractions added
                overbuilt.append({
                    'location': directory,
                    'abstraction_count': total,
                    'types': {k: v for k, v in counts.items() if v > 0}
                })
        
        overbuilt.sort(key=lambda x: x['abstraction_count'], reverse=True)
        return overbuilt[:5]
    
    except Exception:
        return []


def detect_deferred_decisions(workspace: Path, timeframe_days: int) -> List[Dict]:
    """Track TODOs and FIXMEs that are added but never resolved."""
    try:
        # Get current TODOs
        current_todos = defaultdict(list)
        
        src_dirs = [workspace / 'src', workspace / 'scripts']
        for src_dir in src_dirs:
            if not src_dir.exists():
                continue
                
            for py_file in list(src_dir.rglob('*.py'))[:100]:
                try:
                    content = py_file.read_text()
                    for i, line in enumerate(content.split('\n'), 1):
                        if any(marker in line for marker in ['TODO', 'FIXME', 'HACK', 'XXX']):
                            rel_path = py_file.relative_to(workspace)
                            current_todos[str(rel_path)].append({
                                'line': i,
                                'content': line.strip()
                            })
                except Exception:
                    continue
        
        # Check git history for how long these TODOs have existed
        persistent_todos = []
        
        since = f"{timeframe_days}.days.ago"
        for filepath, todos in list(current_todos.items())[:20]:
            try:
                result = subprocess.run(
                    ['git', 'log', '--follow', '--pretty=format:%ad', '--date=short', 
                     f'--since={since}', '--', filepath],
                    cwd=workspace,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.stdout:
                    first_date = result.stdout.strip().split('\n')[-1]
                    days_old = (datetime.now() - datetime.fromisoformat(first_date)).days
                    
                    if days_old >= 7:  # TODO older than a week
                        persistent_todos.append({
                            'file': filepath,
                            'todo_count': len(todos),
                            'days_old': days_old,
                            'samples': [t['content'] for t in todos[:2]]
                        })
            except Exception:
                continue
        
        persistent_todos.sort(key=lambda x: x['days_old'], reverse=True)
        return persistent_todos[:5]
    
    except Exception:
        return []


def detect_conceptual_loops(workspace: Path, timeframe_days: int) -> List[Dict]:
    """Detect when similar commit messages appear repeatedly - sign of unresolved design problem."""
    try:
        since = f"{timeframe_days}.days.ago"
        result = subprocess.run(
            ['git', 'log', '--pretty=format:%s', f'--since={since}'],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if not result.stdout:
            return []
        
        messages = [m.strip() for m in result.stdout.split('\n') if m.strip()]
        
        # Extract conceptual keywords (nouns, verbs that indicate areas of work)
        concept_keywords = defaultdict(list)
        
        for message in messages:
            # Extract meaningful words (skip common words)
            words = re.findall(r'\b[a-z]{4,}\b', message.lower())
            skip_words = {'add', 'update', 'fix', 'remove', 'change', 'with', 'from', 'for', 'the', 'and', 'to'}
            
            for word in words:
                if word not in skip_words:
                    concept_keywords[word].append(message)
        
        # Find concepts that appear frequently
        loops = []
        for concept, messages in concept_keywords.items():
            if len(messages) >= 4:  # Same concept in 4+ commits
                loops.append({
                    'concept': concept,
                    'frequency': len(messages),
                    'sample_messages': messages[:3]
                })
        
        loops.sort(key=lambda x: x['frequency'], reverse=True)
        return loops[:5]
    
    except Exception:
        return []


def analyze_decision_velocity(workspace: Path, timeframe_days: int) -> str:
    """Analyze how quickly architectural decisions are being made."""
    try:
        since = f"{timeframe_days}.days.ago"
        result = subprocess.run(
            ['git', 'log', '--pretty=format:%s', f'--since={since}'],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if not result.stdout:
            return "neutral"
        
        messages = result.stdout.split('\n')
        
        # Count decisiveness indicators
        decisive = sum(1 for m in messages if any(word in m.lower() for word in ['implement', 'add', 'create', 'establish']))
        exploratory = sum(1 for m in messages if any(word in m.lower() for word in ['experiment', 'try', 'test', 'explore']))
        corrective = sum(1 for m in messages if any(word in m.lower() for word in ['fix', 'correct', 'revert', 'undo']))
        
        total = len(messages)
        if total == 0:
            return "dormant"
        
        decisive_ratio = decisive / total
        corrective_ratio = corrective / total
        
        if corrective_ratio > 0.4:
            return "oscillating"  # Too much back-and-forth
        elif decisive_ratio > 0.6:
            return "decisive"
        elif exploratory / total > 0.4:
            return "exploratory"
        else:
            return "neutral"
    
    except Exception:
        return "unknown"


def generate_patterns(
    revisits: List[Dict],
    overbuilt: List[Dict],
    deferred: List[Dict],
    loops: List[Dict],
    velocity: str
) -> List[Dict]:
    """Generate pattern insights from the data."""
    patterns = []
    
    # Revisit patterns
    if revisits:
        top_revisit = revisits[0]
        patterns.append({
            'type': 'repeated_return',
            'description': f"Returning repeatedly to {top_revisit['file']}",
            'evidence': [f"{top_revisit['visits']} edits over {top_revisit['spread_days']} days"] + top_revisit['messages'][:2],
            'frequency': top_revisit['visits'],
            'insight': f"You have returned to this file {top_revisit['visits']} times. The system may need a new axis."
        })
    
    # Overbuilding patterns
    if overbuilt:
        top_overbuilt = overbuilt[0]
        types_str = ', '.join(f"{v} {k}" for k, v in top_overbuilt['types'].items())
        patterns.append({
            'type': 'overbuilding',
            'description': f"Heavy abstraction growth in {top_overbuilt['location']}",
            'evidence': [f"Added {top_overbuilt['abstraction_count']} abstractions: {types_str}"],
            'frequency': top_overbuilt['abstraction_count'],
            'insight': f"This area is accumulating abstractions. Consider: is the complexity essential or are we building scaffolding for scaffolding?"
        })
    
    # Deferred decision patterns
    if deferred:
        total_deferred = sum(d['todo_count'] for d in deferred)
        oldest = deferred[0]
        patterns.append({
            'type': 'deferred_decisions',
            'description': f"Accumulated {total_deferred} unresolved decisions",
            'evidence': [f"{d['file']}: {d['todo_count']} TODOs ({d['days_old']} days old)" for d in deferred[:3]],
            'frequency': total_deferred,
            'insight': f"Decisions are being deferred. The oldest TODO is {oldest['days_old']} days old. What makes these hard to resolve?"
        })
    
    # Conceptual loop patterns
    if loops:
        top_loop = loops[0]
        patterns.append({
            'type': 'conceptual_loop',
            'description': f"Repeatedly working on '{top_loop['concept']}'",
            'evidence': top_loop['sample_messages'],
            'frequency': top_loop['frequency'],
            'insight': f"The concept '{top_loop['concept']}' appears in {top_loop['frequency']} commits. You are circling this territory. What is the missing abstraction?"
        })
    
    # Velocity patterns
    if velocity == 'oscillating':
        patterns.append({
            'type': 'oscillation',
            'description': "High rate of corrections and reversals",
            'evidence': ["Many fix/revert commits"],
            'frequency': 0,
            'insight': "There is oscillation in your decisions. This suggests either unclear requirements or an architectural constraint fighting you."
        })
    
    return patterns


def generate_reflections(patterns: List[Dict], velocity: str) -> List[str]:
    """Generate reflective observations."""
    reflections = []
    
    if any(p['type'] == 'repeated_return' for p in patterns):
        reflections.append(
            "You return to certain territories repeatedly. "
            "This is not failure—it is a signal. "
            "The codebase is telling you something needs to change at a deeper level."
        )
    
    if any(p['type'] == 'overbuilding' for p in patterns):
        reflections.append(
            "There is a tendency to build abstractions. "
            "This is the mark of a sophisticated mind. "
            "But ask: are you solving the problem, or are you solving the act of solving?"
        )
    
    if any(p['type'] == 'deferred_decisions' for p in patterns):
        reflections.append(
            "You defer certain decisions. "
            "This is not procrastination—it is wisdom. "
            "But deferred too long, decisions become debt. "
            "What do these TODOs have in common?"
        )
    
    if any(p['type'] == 'conceptual_loop' for p in patterns):
        reflections.append(
            "You circle the same conceptual ground. "
            "Each pass refines understanding. "
            "But if the circle does not spiral upward, it may be time to break the plane. "
            "What new dimension would resolve this?"
        )
    
    if velocity == 'oscillating':
        reflections.append(
            "Your commits show oscillation. "
            "You try, correct, try again. "
            "This is the pattern of working against the grain. "
            "Step back: what constraint are you fighting?"
        )
    elif velocity == 'decisive':
        reflections.append(
            "You move with decisiveness. "
            "This is the sign of clarity. "
            "Hold this velocity, but watch for momentum becoming inertia."
        )
    elif velocity == 'exploratory':
        reflections.append(
            "You explore many paths. "
            "This is the pattern of learning. "
            "But exploration must eventually converge to decision. "
            "What would allow you to choose?"
        )
    
    if not patterns:
        reflections.append(
            "Your patterns are quiet in this timeframe. "
            "Either the system is stable, or you are building beneath the surface. "
            "Both are valid. Neither lasts forever."
        )
    
    return reflections


def generate_suggestions(patterns: List[Dict]) -> List[str]:
    """Generate non-judgmental suggestions."""
    suggestions = []
    
    if any(p['type'] == 'repeated_return' for p in patterns):
        suggestions.append("Consider: would a new abstraction or architectural shift address the root tension?")
    
    if any(p['type'] == 'overbuilding' for p in patterns):
        suggestions.append("Consider: remove one abstraction and see if the simplicity reveals clarity.")
    
    if any(p['type'] == 'deferred_decisions' for p in patterns):
        suggestions.append("Consider: schedule one hour to resolve the three oldest TODOs, or delete them.")
    
    if any(p['type'] == 'conceptual_loop' for p in patterns):
        suggestions.append("Consider: name the missing concept that would break the loop, even if you cannot yet implement it.")
    
    if any(p['type'] == 'oscillation' for p in patterns):
        suggestions.append("Consider: write down the constraint you are fighting. Often naming it reveals the path.")
    
    return suggestions


def main():
    parser = argparse.ArgumentParser(description='Sophia Mirror - The Architect Reflecting Himself')
    parser.add_argument('workspace_root', type=str)
    parser.add_argument('action', choices=['reflect', 'patterns'])
    parser.add_argument('--timeframe', type=str, choices=['day', 'week', 'month'], default='week')
    parser.add_argument('--focus', type=str, help='Focus on specific area')
    
    args = parser.parse_args()
    workspace = Path(args.workspace_root)
    
    # Map timeframe to days
    timeframe_map = {'day': 1, 'week': 7, 'month': 30}
    timeframe_days = timeframe_map[args.timeframe]
    
    # Collect patterns
    revisits = track_revisits(workspace, timeframe_days)
    overbuilt = detect_overbuilding(workspace, timeframe_days)
    deferred = detect_deferred_decisions(workspace, timeframe_days)
    loops = detect_conceptual_loops(workspace, timeframe_days)
    velocity = analyze_decision_velocity(workspace, timeframe_days)
    
    # Generate insights
    patterns = generate_patterns(revisits, overbuilt, deferred, loops, velocity)
    
    if args.action == 'reflect':
        reflections = generate_reflections(patterns, velocity)
        suggestions = generate_suggestions(patterns)
        
        result = {
            'action': 'reflect',
            'timeframe': args.timeframe,
            'patterns_detected': patterns,
            'reflections': reflections,
            'suggestions': suggestions
        }
    else:  # patterns
        result = {
            'action': 'patterns',
            'timeframe': args.timeframe,
            'patterns_detected': patterns,
            'reflections': [],
            'suggestions': []
        }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
