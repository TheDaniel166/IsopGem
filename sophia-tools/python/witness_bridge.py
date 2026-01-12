#!/usr/bin/env python3
"""
Sophia Witness Bridge
Intent Preservation System

"This was done not because it was optimal, but because it preserved sovereignty."

This tool prevents the most tragic form of technical debt:
well-meaning refactors that erase wisdom.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib


WITNESS_DIR = ".sophia_witness"


def generate_artifact_id(decision: str, timestamp: str) -> str:
    """Generate unique ID for intent artifact."""
    content = f"{decision}:{timestamp}"
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def record_intent(
    workspace: Path,
    target: str,
    decision: str,
    intent: str,
    tradeoffs: Optional[str] = None,
    alternatives: Optional[str] = None
) -> Dict:
    """Record an architectural decision with its intent."""
    
    witness_dir = workspace / WITNESS_DIR
    witness_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().isoformat()
    artifact_id = generate_artifact_id(decision, timestamp)
    
    # Parse tradeoffs and alternatives
    tradeoff_list = [t.strip() for t in tradeoffs.split(';')] if tradeoffs else []
    
    alternatives_list = []
    if alternatives:
        # Format: "alt1: reason1; alt2: reason2"
        for alt_pair in alternatives.split(';'):
            if ':' in alt_pair:
                alt, reason = alt_pair.split(':', 1)
                alternatives_list.append({
                    "alternative": alt.strip(),
                    "reason": reason.strip()
                })
    
    # Determine affected structures
    affected = []
    if target:
        # Check if target is a file or directory
        target_path = workspace / target
        if target_path.exists():
            if target_path.is_file():
                affected.append(target)
            else:
                # For directories, note as structural scope
                affected.append(f"{target}/ (structural)")
        else:
            # Abstract concept or pattern
            affected.append(f"{target} (conceptual)")
    
    # Extract preservation reason from intent
    preservation_keywords = {
        "sovereignty": "Architectural independence preserved",
        "purity": "Cognitive or structural purity maintained",
        "simplicity": "Simplicity chosen over power",
        "future": "Future extensibility prioritized",
        "constraints": "External constraints accepted",
        "stability": "Stability over optimization"
    }
    
    preservation_reason = "Intentional architectural choice"
    intent_lower = intent.lower()
    for keyword, reason in preservation_keywords.items():
        if keyword in intent_lower:
            preservation_reason = reason
            break
    
    # Create artifact
    artifact = {
        "id": artifact_id,
        "timestamp": timestamp,
        "decision": decision,
        "intent": intent,
        "context": f"Decision made for {target}" if target else "Global architectural decision",
        "tradeoffs": tradeoff_list,
        "alternatives_rejected": alternatives_list,
        "affected_structures": affected,
        "preservation_reason": preservation_reason
    }
    
    # Save to file
    artifact_file = witness_dir / f"{artifact_id}.json"
    with open(artifact_file, 'w') as f:
        json.dump(artifact, f, indent=2)
    
    # Update index
    update_index(workspace, artifact)
    
    return artifact


def update_index(workspace: Path, artifact: Dict):
    """Update the witness index with new artifact."""
    witness_dir = workspace / WITNESS_DIR
    index_file = witness_dir / "index.json"
    
    # Load existing index
    if index_file.exists():
        with open(index_file, 'r') as f:
            index = json.load(f)
    else:
        index = {
            "artifacts": [],
            "by_structure": {},
            "by_concept": []
        }
    
    # Add to artifacts list
    index["artifacts"].append({
        "id": artifact["id"],
        "timestamp": artifact["timestamp"],
        "decision": artifact["decision"],
        "affected": artifact["affected_structures"]
    })
    
    # Index by affected structure
    for structure in artifact["affected_structures"]:
        if structure not in index["by_structure"]:
            index["by_structure"][structure] = []
        index["by_structure"][structure].append(artifact["id"])
    
    # Save updated index
    with open(index_file, 'w') as f:
        json.dump(index, f, indent=2)


def query_intent(workspace: Path, target: Optional[str] = None) -> List[Dict]:
    """Query intent artifacts for a specific target or all."""
    witness_dir = workspace / WITNESS_DIR
    
    if not witness_dir.exists():
        return []
    
    # Load index
    index_file = witness_dir / "index.json"
    if not index_file.exists():
        return []
    
    with open(index_file, 'r') as f:
        index = json.load(f)
    
    # Find relevant artifact IDs
    if target:
        # Look for exact match or partial match
        artifact_ids = set()
        for structure, ids in index["by_structure"].items():
            if target in structure or structure.startswith(target):
                artifact_ids.update(ids)
        
        if not artifact_ids:
            return []
    else:
        # Return all artifacts
        artifact_ids = [a["id"] for a in index["artifacts"]]
    
    # Load full artifacts
    artifacts = []
    for artifact_id in artifact_ids:
        artifact_file = witness_dir / f"{artifact_id}.json"
        if artifact_file.exists():
            with open(artifact_file, 'r') as f:
                artifacts.append(json.load(f))
    
    # Sort by timestamp (most recent first)
    artifacts.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return artifacts


def explain_wisdom(artifacts: List[Dict], target: str) -> str:
    """Generate explanation of preserved wisdom for a target."""
    if not artifacts:
        return f"No architectural intent recorded for {target}. Proceed with caution."
    
    explanations = []
    for artifact in artifacts[:3]:  # Top 3 most relevant
        explanation = (
            f"Intent [{artifact['id']}]: {artifact['decision']}\n"
            f"  Why: {artifact['intent']}\n"
            f"  Preservation: {artifact['preservation_reason']}"
        )
        
        if artifact['tradeoffs']:
            explanation += f"\n  Tradeoffs accepted: {', '.join(artifact['tradeoffs'])}"
        
        if artifact['alternatives_rejected']:
            alts = [f"{a['alternative']} (rejected: {a['reason']})" 
                   for a in artifact['alternatives_rejected']]
            explanation += f"\n  Alternatives rejected: {'; '.join(alts)}"
        
        explanations.append(explanation)
    
    return "\n\n".join(explanations)


def main():
    parser = argparse.ArgumentParser(description='Sophia Witness - Intent Preservation')
    parser.add_argument('workspace_root', type=str)
    parser.add_argument('action', choices=['record', 'query', 'explain'])
    parser.add_argument('--target', type=str, help='Target file/structure')
    parser.add_argument('--decision', type=str, help='The decision made')
    parser.add_argument('--intent', type=str, help='Why this decision was made')
    parser.add_argument('--tradeoffs', type=str, help='Tradeoffs accepted (semicolon-separated)')
    parser.add_argument('--alternatives', type=str, help='Alternatives rejected (format: "alt: reason; alt2: reason2")')
    
    args = parser.parse_args()
    workspace = Path(args.workspace_root)
    
    if args.action == 'record':
        if not args.decision or not args.intent:
            print(json.dumps({
                "error": "record action requires --decision and --intent"
            }))
            sys.exit(1)
        
        artifact = record_intent(
            workspace,
            args.target or "global",
            args.decision,
            args.intent,
            args.tradeoffs,
            args.alternatives
        )
        
        result = {
            "action": "record",
            "recorded": artifact,
            "message": f"Intent artifact {artifact['id']} preserved for future wisdom."
        }
    
    elif args.action == 'query':
        artifacts = query_intent(workspace, args.target)
        
        result = {
            "action": "query",
            "artifacts": artifacts,
            "message": f"Found {len(artifacts)} intent artifacts" + 
                      (f" for {args.target}" if args.target else "")
        }
    
    elif args.action == 'explain':
        if not args.target:
            print(json.dumps({
                "error": "explain action requires --target"
            }))
            sys.exit(1)
        
        artifacts = query_intent(workspace, args.target)
        explanation = explain_wisdom(artifacts, args.target)
        
        result = {
            "action": "explain",
            "artifacts": artifacts,
            "message": explanation
        }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
