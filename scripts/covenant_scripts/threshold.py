#!/usr/bin/env python3
"""
Sophia Threshold: Readiness assessment before major changes.

Purpose: Evaluate whether conditions are right for a proposed action.
         Checks recent churn, test coverage, and requirements completeness.

Usage:
    python scripts/covenant_scripts/threshold.py <workspace_root> "<proposed_action>"

Example:
    python scripts/covenant_scripts/threshold.py . "Refactor entire Gematria pillar"
"""
import sys
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List


def resolve_workspace(workspace_arg: str = None) -> Path:
    """Resolve workspace root."""
    if workspace_arg:
        path = Path(workspace_arg)
        if path.exists():
            return path.resolve()
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".git").exists() or (parent / "src").exists():
            return parent
    return cwd


def output_json(data: dict) -> None:
    """Output JSON to stdout."""
    print(json.dumps(data, indent=2, default=str))


def output_error(message: str, details: str = None) -> None:
    """Output error and exit."""
    error_data = {"error": message}
    if details:
        error_data["details"] = details
    output_json(error_data)
    sys.exit(1)


def get_recent_commits(workspace: Path, days: int = 7) -> int:
    """Count commits in the last N days."""
    try:
        result = subprocess.run(
            ["git", "log", f"--since={days} days ago", "--oneline"],
            cwd=workspace,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    except Exception:
        pass
    return -1  # Unable to determine


def check_test_coverage(workspace: Path, action_tokens: List[str]) -> dict:
    """Check if tests exist for relevant modules."""
    tests_dir = workspace / "tests"
    if not tests_dir.exists():
        return {"status": "no_tests_dir", "coverage": "unknown"}
    
    test_files = list(tests_dir.rglob("*.py"))
    test_count = len([f for f in test_files if f.name.startswith("test_")])
    
    # Check if relevant tests exist
    relevant_tests = []
    for token in action_tokens:
        for tf in test_files:
            if token in tf.name.lower():
                relevant_tests.append(str(tf.name))
    
    return {
        "total_test_files": test_count,
        "relevant_tests": relevant_tests[:5],
        "coverage": "partial" if relevant_tests else "missing",
    }


def check_known_distortions(workspace: Path) -> List[str]:
    """Check for known distortions that might block work."""
    distortions_file = workspace / "wiki" / "04_prophecies" / "KNOWN_DISTORTIONS.md"
    
    if not distortions_file.exists():
        return []
    
    try:
        content = distortions_file.read_text(encoding="utf-8")
        # Find open distortions
        open_pattern = r'\[OPEN\]\s*(.+?)(?:\n|$)'
        return re.findall(open_pattern, content)[:5]
    except Exception:
        return []


def assess_readiness(workspace: Path, action: str) -> dict:
    """Assess readiness for the proposed action."""
    tokens = re.findall(r'\b\w+\b', action.lower())
    blockers = []
    
    # Check 1: Recent churn
    commits = get_recent_commits(workspace)
    if commits > 10:
        blockers.append(f"High recent churn ({commits} commits this week)")
    
    # Check 2: Test coverage
    test_info = check_test_coverage(workspace, tokens)
    if test_info["coverage"] == "missing":
        blockers.append("Missing tests for relevant functionality")
    
    # Check 3: Known distortions
    distortions = check_known_distortions(workspace)
    if distortions:
        blockers.append(f"Open distortions exist: {len(distortions)} unresolved")
    
    # Determine readiness
    if len(blockers) == 0:
        readiness = "ready"
        recommendation = "Proceed with the action"
        confidence = 0.9
    elif len(blockers) == 1:
        readiness = "caution"
        recommendation = "Address blocker before proceeding"
        confidence = 0.7
    else:
        readiness = "too_early"
        recommendation = "Wait until blockers are resolved"
        confidence = 0.85
    
    return {
        "action": action,
        "readiness": readiness,
        "blockers": blockers,
        "test_info": test_info,
        "recent_commits": commits,
        "recommendation": recommendation,
        "confidence": confidence,
    }


def main():
    if len(sys.argv) < 3:
        output_error(
            "Missing arguments",
            "Usage: threshold.py <workspace_root> <proposed_action>"
        )
    
    workspace = resolve_workspace(sys.argv[1])
    action = sys.argv[2]
    
    if not workspace.exists():
        output_error("Workspace not found", str(workspace))
    
    result = assess_readiness(workspace, action)
    result["timestamp"] = datetime.now().isoformat()
    
    output_json(result)


if __name__ == "__main__":
    main()
