"""
Mermaid Syntax Linter.
Detects common syntax errors in Mermaid diagrams and offers suggestions.
"""
import re
from dataclasses import dataclass
from enum import Enum


class LintSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LintIssue:
    """A single lint issue."""
    line: int
    message: str
    severity: LintSeverity
    suggestion: str | None = None


class MermaidLinter:
    """
    Lints Mermaid diagram code for common syntax errors.
    """
    
    # Valid diagram type declarations
    VALID_DIAGRAM_TYPES = [
        r'^graph\s+(TB|TD|BT|RL|LR)',
        r'^flowchart\s+(TB|TD|BT|RL|LR)',
        r'^sequenceDiagram',
        r'^classDiagram',
        r'^stateDiagram(-v2)?',
        r'^erDiagram',
        r'^pie(\s+title\s+.+)?',
        r'^gantt',
        r'^mindmap',
        r'^timeline',
        r'^gitGraph',
        r'^c4Context',
    ]
    
    # Arrow patterns
    VALID_ARROWS = [
        r'-->',
        r'---',
        r'-.->',
        r'==>',
        r'-->>',
        r'->>',
        r'->',
        r'<-->',
        r'~~~',
        r'\|\|--o\{',
        r'\|\|--\|\{',
        r'<\|--',
    ]
    
    @classmethod
    def lint(cls, code: str) -> list[LintIssue]:
        """
        Lint the given Mermaid code and return a list of issues.
        """
        issues = []
        lines = code.split('\n')
        
        # Skip empty content
        if not code.strip():
            return issues
        
        # Check 1: Missing diagram type declaration
        has_diagram_type = cls._check_diagram_type(lines)
        if not has_diagram_type:
            issues.append(LintIssue(
                line=1,
                message="Missing diagram type declaration",
                severity=LintSeverity.ERROR,
                suggestion="Start with 'graph TD', 'sequenceDiagram', 'erDiagram', etc."
            ))
        
        # Check 2: Unbalanced brackets
        bracket_issues = cls._check_brackets(lines)
        issues.extend(bracket_issues)
        
        # Check 3: Empty subgraphs
        subgraph_issues = cls._check_subgraphs(lines)
        issues.extend(subgraph_issues)
        
        # Check 4: Invalid node IDs (starting with numbers)
        node_issues = cls._check_node_ids(lines)
        issues.extend(node_issues)
        
        # Check 5: Sequence diagram issues
        if cls._is_sequence_diagram(lines):
            seq_issues = cls._check_sequence_diagram(lines)
            issues.extend(seq_issues)
        
        # Check 6: ER diagram issues
        if cls._is_er_diagram(lines):
            er_issues = cls._check_er_diagram(lines)
            issues.extend(er_issues)
        
        return issues
    
    @classmethod
    def _check_diagram_type(cls, lines: list[str]) -> bool:
        """Check if code starts with a valid diagram type."""
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('%%'):
                continue
            
            for pattern in cls.VALID_DIAGRAM_TYPES:
                if re.match(pattern, stripped, re.IGNORECASE):
                    return True
            return False
        return False
    
    @classmethod
    def _check_brackets(cls, lines: list[str]) -> list[LintIssue]:
        """Check for unbalanced brackets."""
        issues = []
        bracket_pairs = {'[': ']', '{': '}', '(': ')'}
        
        # Determine if this is an ER diagram to handle cardinality syntax
        is_er = cls._is_er_diagram(lines)
        
        for i, line in enumerate(lines, 1):
            # For ER diagrams, ignore cardinality markers like o{ |{ }| }o
            # by replacing them with spaces before checking brackets
            line_to_check = line
            if is_er:
                line_to_check = line_to_check.replace('o{', '  ') \
                                             .replace('|{', '  ') \
                                             .replace('}|', '  ') \
                                             .replace('}o', '  ')
            
            stack = []
            for char in line_to_check:
                if char in bracket_pairs:
                    stack.append((char, i))
                elif char in bracket_pairs.values():
                    if not stack:
                        issues.append(LintIssue(
                            line=i,
                            message=f"Unexpected closing bracket '{char}'",
                            severity=LintSeverity.ERROR,
                            suggestion=f"Remove the extra '{char}' or add matching opening bracket"
                        ))
                    else:
                        open_bracket, _ = stack.pop()
                        if bracket_pairs[open_bracket] != char:
                            issues.append(LintIssue(
                                line=i,
                                message=f"Mismatched brackets: expected '{bracket_pairs[open_bracket]}', found '{char}'",
                                severity=LintSeverity.ERROR,
                                suggestion=f"Replace '{char}' with '{bracket_pairs[open_bracket]}'"
                            ))
            
            # Check for unclosed brackets on this line
            for bracket, line_num in stack:
                issues.append(LintIssue(
                    line=line_num,
                    message=f"Unclosed bracket '{bracket}'",
                    severity=LintSeverity.ERROR,
                    suggestion=f"Add closing '{bracket_pairs[bracket]}'"
                ))
        
        return issues
    
    @classmethod
    def _check_subgraphs(cls, lines: list[str]) -> list[LintIssue]:
        """Check for subgraph issues."""
        issues = []
        subgraph_stack = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip().lower()
            
            if stripped.startswith('subgraph'):
                subgraph_stack.append(i)
            elif stripped == 'end':
                if subgraph_stack:
                    subgraph_stack.pop()
                else:
                    issues.append(LintIssue(
                        line=i,
                        message="'end' without matching 'subgraph'",
                        severity=LintSeverity.ERROR,
                        suggestion="Remove this 'end' or add a 'subgraph' declaration above"
                    ))
        
        for line_num in subgraph_stack:
            issues.append(LintIssue(
                line=line_num,
                message="'subgraph' without closing 'end'",
                severity=LintSeverity.ERROR,
                suggestion="Add 'end' to close the subgraph"
            ))
        
        return issues
    
    @classmethod
    def _check_node_ids(cls, lines: list[str]) -> list[LintIssue]:
        """Check for invalid node IDs."""
        issues = []
        
        # Pattern for node definitions that start with a number
        node_pattern = re.compile(r'^\s*(\d+\w*)\s*[\[\(\{]')
        
        for i, line in enumerate(lines, 1):
            match = node_pattern.match(line)
            if match:
                issues.append(LintIssue(
                    line=i,
                    message=f"Node ID '{match.group(1)}' starts with a number",
                    severity=LintSeverity.WARNING,
                    suggestion="Node IDs should start with a letter (e.g., 'node1' instead of '1node')"
                ))
        
        return issues
    
    @classmethod
    def _is_sequence_diagram(cls, lines: list[str]) -> bool:
        """Check if this is a sequence diagram."""
        for line in lines:
            if 'sequenceDiagram' in line:
                return True
        return False
    
    @classmethod
    def _is_er_diagram(cls, lines: list[str]) -> bool:
        """Check if this is an ER diagram."""
        for line in lines:
            if 'erDiagram' in line:
                return True
        return False
    
    @classmethod
    def _check_sequence_diagram(cls, lines: list[str]) -> list[LintIssue]:
        """Check sequence diagram-specific issues."""
        issues = []
        participants = set()
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Collect participants
            if stripped.startswith('participant ') or stripped.startswith('actor '):
                parts = stripped.split()
                if len(parts) >= 2:
                    # Handle "participant A as Alias" format
                    name = parts[1]
                    participants.add(name)
            
            # Check arrow syntax
            if '->' in stripped and '->>' not in stripped and '-->' not in stripped:
                # Could be invalid arrow
                if re.search(r'\-\>\s*\w+\s*:', stripped):
                    issues.append(LintIssue(
                        line=i,
                        message="Use '->' is informal in sequence diagrams",
                        severity=LintSeverity.INFO,
                        suggestion="Consider using '->>>' (async) or '->>' (sync) for clearer semantics"
                    ))
        
        return issues
    
    @classmethod
    def _check_er_diagram(cls, lines: list[str]) -> list[LintIssue]:
        """Check ER diagram-specific issues."""
        issues = []
        
        valid_cardinality = ['||', '|{', '}|', '}o', 'o{', 'o|', '|o']
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check relationship syntax
            if ':' in stripped and not stripped.startswith('%%'):
                # This might be a relationship line
                if not any(c in stripped for c in ['||', '|{', '}|', '}o', 'o{']):
                    if re.match(r'^\s*\w+.*:.*\w+', stripped):
                        # Looks like a relationship but missing cardinality
                        issues.append(LintIssue(
                            line=i,
                            message="ER relationship may be missing cardinality notation",
                            severity=LintSeverity.WARNING,
                            suggestion="Use cardinality like '||--o{' between entity names"
                        ))
        
        return issues
