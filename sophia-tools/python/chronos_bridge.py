#!/usr/bin/env python3
"""
Sophia Chronos Bridge
The Eye of Time.
Analyzes the temporal evolution of code artifacts (Git history).
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta


def run_git_command(cwd: Path, args: List[str]) -> str:
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ['git'] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return ""


def get_file_history(workspace: Path, target: str, days: int) -> List[Dict[str, Any]]:
    """Get the history of a specific file."""
    
    since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # Get log with patches
    # Format: Hash|Date|Author|Subject
    log_args = [
        'log',
        f'--since={since_date}',
        '--pretty=format:%H|%ad|%an|%s',
        '--date=iso',
        '--',
        target
    ]
    
    raw_log = run_git_command(workspace, log_args)
    if not raw_log:
        return []
        
    history = []
    
    for line in raw_log.split('\n'):
        if not line.strip():
            continue
            
        parts = line.split('|')
        if len(parts) < 4:
            continue
            
        commit_hash, date, author, subject = parts[0], parts[1], parts[2], parts[3]
        
        # Get the diff stat for this commit and file
        stat_args = ['show', '--format=', '--numstat', commit_hash, '--', target]
        stat_out = run_git_command(workspace, stat_args)
        
        added = 0
        deleted = 0
        if stat_out:
            # Output looks like: "10  5   path/to/file"
            try:
                stat_parts = stat_out.split()
                if len(stat_parts) >= 2:
                    added = int(stat_parts[0]) if stat_parts[0].isdigit() else 0
                    deleted = int(stat_parts[1]) if stat_parts[1].isdigit() else 0
            except:
                pass

        history.append({
            "hash": commit_hash,
            "date": date,
            "author": author,
            "message": subject,
            "changes": {
                "added": added,
                "deleted": deleted,
                "net": added - deleted
            }
        })
        
    return history


def analyze_function_evolution(workspace: Path, target_file: str, function_name: str, days: int) -> List[Dict[str, Any]]:
    """
    Experimental: Analyze how a specific function changed.
    Uses 'git log -L' (line log) if available.
    """
    # git log -L :funcname:file
    # This is powerful but requires the function to exist in the regex
    
    args = [
        'log',
        f'-L:{function_name}:{target_file}',
        '--no-merges',
        f'--since={days}.days.ago'
    ]
    
    # This allows us to see the diffs specifically for that function block
    raw_out = run_git_command(workspace, args)
    
    # Parsing -L output is complex, for now we return the raw raw text chunks
    # or we can structure it if we want to be fancy.
    # For MVP Chronos, returning a structured summary of the output is best.
    
    return [{"raw_trace": raw_out}]


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)
    
    workspace_root = Path(sys.argv[1])
    action = sys.argv[2] # 'file_history' or 'function_trace'
    
    # Default lookback
    days = 7
    
    result = {}
    
    if action == "file_history":
        target = sys.argv[3]
        if len(sys.argv) > 4:
            days = int(sys.argv[4])
        
        history = get_file_history(workspace_root, target, days)
        result = {
            "target": target,
            "days_back": days,
            "commit_count": len(history),
            "history": history
        }
        
    elif action == "function_trace":
        # python chronos_bridge.py root function_trace file.py func_name 7
        target = sys.argv[3]
        func_name = sys.argv[4]
        if len(sys.argv) > 5:
            days = int(sys.argv[5])
            
        trace = analyze_function_evolution(workspace_root, target, func_name, days)
        result = {
            "target": target,
            "function": func_name,
            "trace": trace
        }
        
    else:
        result = {"error": f"Unknown action: {action}"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
