#!/usr/bin/env python3
"""
The Scribe of Thoth - Automated Inscription Tool.

Scans Python files for missing docstrings and mechanically inscribes
structural skeletons to satisfy the Rite of Inscription.

"I am the pen, and the Code is the paper. I fill the void with intent."
"""
import ast
import sys
import re
from pathlib import Path
from typing import List, Tuple, Optional

# Configuration
SKIP_UNDERSCORES = True  # Skip private methods _foo
MIN_DOCSTRING_LENGTH = 15

def camel_to_spaces(name: str) -> str:
    """Convert CamelCase to 'Camel Case'."""
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', name)

def snake_to_sentence(name: str) -> str:
    """Convert snake_case to 'Sentence case'."""
    words = name.split('_')
    # Heuristic verb replacement
    verb_map = {
        'get': 'Retrieve',
        'set': 'Configure',
        'is': 'Determine if',
        'has': 'Check if',
        'calc': 'Compute',
        'calculate': 'Compute',
        'init': 'Initialize',
        'update': 'Update',
        'create': 'Create',
        'delete': 'Remove',
        'add': 'Add',
        'remove': 'Remove',
        'load': 'Load',
        'save': 'Save',
        'parse': 'Parse',
        'render': 'Render',
        'show': 'Display',
        'hide': 'Hide',
        'run': 'Execute',
        'process': 'Process',
        'on': 'Handle',
        'to': 'Convert to'
    }
    
    if words[0] in verb_map:
        words[0] = verb_map[words[0]]
    else:
        words[0] = words[0].capitalize()
        
    return ' '.join(words)

def generate_docstring(node: ast.AST, indentation: str) -> str:
    """Generate a skeleton docstring for a node."""
    lines = []
    
    if isinstance(node, ast.ClassDef):
        name_human = camel_to_spaces(node.name)
        lines.append(f'{indentation}"""')
        lines.append(f'{indentation}{name_human} class definition.')
        lines.append(f'{indentation}')
        
        # Scan for __init__ and attributes
        attributes = []
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and child.name == '__init__':
                for stmt in child.body:
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                attributes.append(target.attr)
                    elif isinstance(stmt, ast.AnnAssign):
                         if isinstance(stmt.target, ast.Attribute) and isinstance(stmt.target.value, ast.Name) and stmt.target.value.id == 'self':
                                attributes.append(stmt.target.attr)
        
        if attributes:
            lines.append(f'{indentation}Attributes:')
            for attr in attributes:
                lines.append(f'{indentation}    {attr}: Description of {attr}.')
            lines.append(f'{indentation}')
        
        lines.append(f'{indentation}"""')
        
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        name_human = snake_to_sentence(node.name)
        lines.append(f'{indentation}"""')
        lines.append(f'{indentation}{name_human} logic.')
        lines.append(f'{indentation}')
        
        # Args
        args = [a.arg for a in node.args.args if a.arg != 'self' and a.arg != 'cls']
        if args:
            lines.append(f'{indentation}Args:')
            for arg in args:
                lines.append(f'{indentation}    {arg}: Description of {arg}.')
            lines.append(f'{indentation}')
        
        # Returns - check for return annotation or yield
        has_return = node.returns is not None
        # Heuristic check for yield
        is_generator = False
        for child in ast.walk(node):
            if isinstance(child, (ast.Yield, ast.YieldFrom)):
                is_generator = True
                break
                
        if is_generator:
            lines.append(f'{indentation}Yields:')
            lines.append(f'{indentation}    Yielded values.')
        elif has_return or node.name.startswith('get') or node.name.startswith('calc'):
            # Assume return for getters even if no annotation
            lines.append(f'{indentation}Returns:')
            lines.append(f'{indentation}    Result of {node.name} operation.')
            
        lines.append(f'{indentation}"""')
        
    return '\n'.join(lines)

def process_file(filepath: Path, dry_run: bool = False) -> int:
    """Inject or update docstrings into a file. Returns count of inscriptions."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return 0
        
    try:
        tree = ast.parse(content)
    except SyntaxError:
        print(f"Syntax Error parsing {filepath}")
        return 0

    lines = content.splitlines()
    modifications = [] # List of (start_line_0idx, end_line_0idx, text)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            # Skip private
            if SKIP_UNDERSCORES and node.name.startswith('_') and not node.name.startswith('__init__'):
                continue
            
            # Check existing
            doc = ast.get_docstring(node)
            replacement_target = None
            
            if doc:
                if "todo: Add public attributes" in doc:
                    # Found a banal placeholder! We must replace it.
                    if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, (ast.Str, ast.Constant)):
                        doc_node = node.body[0]
                        if hasattr(doc_node, 'end_lineno'):
                            replacement_target = (doc_node.lineno - 1, doc_node.end_lineno)
                        else:
                            # Fallback for older python without end_lineno? 
                            # Just skip replacement if we can't be sure of range
                            continue
                else:
                    continue # Valid existing docstring, skip
            
            # We need to insert or replace. 
            # Calculate indentation
            if not node.body:
                continue 
                
            first_stmt = node.body[0]
            
            # Indentation
            indent_level = first_stmt.col_offset
            indent_str = " " * indent_level
            
            doc_text = generate_docstring(node, indent_str)
            
            if replacement_target:
                # Replacement
                modifications.append((replacement_target[0], replacement_target[1], doc_text))
            else:
                # Insertion
                # Insert before first_stmt
                insert_idx = first_stmt.lineno - 1
                modifications.append((insert_idx, insert_idx, doc_text))

    if not modifications:
        return 0
        
    # Sort descending by start line to keep indices valid
    modifications.sort(key=lambda x: x[0], reverse=True)
    
    if dry_run:
        print(f"Would apply {len(modifications)} inscriptions in {filepath}")
        return len(modifications)
        
    for start, end, text in modifications:
        if start == end:
            # Insertion
            lines.insert(start, text)
        else:
            # Replacement: Remove old lines, insert new text
            # We replace the slice with the new text (which is a single string with newlines)
            # lines is a list of strings. text is a string with \n.
            # We need to split text into lines to insert properly into the list slice
            new_lines = text.splitlines()
            lines[start:end] = new_lines
        
    try:
        filepath.write_text('\n'.join(lines), encoding='utf-8')
        print(f"Inscribed {len(modifications)} docstrings in {filepath.name}")
        return len(modifications)
    except Exception as e:
        print(f"Failed to write {filepath}: {e}")
        return 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scribe_of_thoth.py [file|dir|--all] [--dry-run]")
        sys.exit(1)
        
    target_arg = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    
    targets = []
    if target_arg == "--all":
        root = Path("src")
        targets = list(root.rglob("*.py"))
    else:
        p = Path(target_arg)
        if p.is_dir():
            targets = list(p.rglob("*.py"))
        else:
            targets = [p]
            
    total_inscribed = 0
    for t in targets:
        total_inscribed += process_file(t, dry_run=dry_run)
        
    print(f"\nTotal Inscriptions: {total_inscribed}")

if __name__ == "__main__":
    main()
