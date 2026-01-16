#!/usr/bin/env python3
"""
Enhance auto-generated pillar documentation by filling AI_ENHANCE markers.

This script:
1. Reads skeleton documentation files
2. Finds <!-- AI_ENHANCE: --> markers
3. Analyzes referenced source files
4. Generates real content to replace markers
5. Writes enhanced documentation

Usage:
    python scripts/enhance_pillar_docs.py geometry
    python scripts/enhance_pillar_docs.py geometry --section architecture
    python scripts/enhance_pillar_docs.py geometry --file service_layer.md
"""

import ast
import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


@dataclass
class EnhanceMarker:
    """Represents an AI_ENHANCE marker to be filled."""
    file_path: Path
    line_number: int
    marker_text: str
    context: str  # Surrounding section (e.g., "### Purpose", "### Key Methods")
    replacement_text: str = ""


class SourceAnalyzer:
    """Analyzes Python source files to extract documentation content."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def extract_class_purpose(self, file_path: Path, class_name: str) -> str:
        """Extract purpose from class docstring."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    docstring = ast.get_docstring(node)
                    if docstring:
                        # Take first paragraph
                        return docstring.split('\n\n')[0].strip()
            
            return f"Handles {class_name} operations"
        except Exception as e:
            logger.debug(f"Could not extract purpose from {file_path}: {e}")
            return ""
    
    def extract_key_methods(self, file_path: Path, class_name: str) -> List[Tuple[str, str]]:
        """Extract public methods and their docstrings."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            methods = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Only public methods
                            if not item.name.startswith('_') or item.name.startswith('__init'):
                                docstring = ast.get_docstring(item) or ""
                                # Take first sentence
                                doc_summary = docstring.split('.')[0] if docstring else f"{item.name} method"
                                methods.append((item.name, doc_summary.strip()))
            
            return methods[:5]  # Top 5
        except Exception as e:
            logger.debug(f"Could not extract methods from {file_path}: {e}")
            return []
    
    def extract_signals(self, file_path: Path, class_name: str) -> List[Tuple[str, str]]:
        """Extract PyQt signals from a class."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            signals = []
            # Look for pyqtSignal assignments
            signal_pattern = r'(\w+)\s*=\s*pyqtSignal\((.*?)\)'
            for match in re.finditer(signal_pattern, source):
                signal_name = match.group(1)
                signal_args = match.group(2)
                signals.append((signal_name, signal_args))
            
            return signals
        except Exception as e:
            logger.debug(f"Could not extract signals from {file_path}: {e}")
            return []
    
    def extract_dependencies(self, file_path: Path) -> List[str]:
        """Extract import dependencies from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
            
            # Filter for project imports
            project_imports = [imp for imp in imports if 'pillars' in imp or 'shared' in imp]
            return sorted(project_imports)[:5]
        except Exception as e:
            logger.debug(f"Could not extract dependencies from {file_path}: {e}")
            return []
    
    def find_usage_examples(self, file_path: Path, class_name: str) -> str:
        """Find real usage examples in the codebase."""
        try:
            # Search for usage in ui/ directory
            ui_dir = file_path.parent.parent / "ui"
            if not ui_dir.exists():
                return ""
            
            examples = []
            for py_file in ui_dir.rglob("*.py"):
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                # Look for instantiation patterns
                if class_name in source:
                    # Extract context around class usage
                    lines = source.split('\n')
                    for i, line in enumerate(lines):
                        if class_name in line and ('=' in line or '(' in line):
                            # Get 3 lines of context
                            start = max(0, i - 1)
                            end = min(len(lines), i + 3)
                            example = '\n'.join(lines[start:end])
                            examples.append(example.strip())
                            break
                
                if examples:
                    break
            
            if examples:
                return f"```python\n{examples[0]}\n```"
            return ""
        except Exception as e:
            logger.debug(f"Could not find usage examples: {e}")
            return ""


class DocEnhancer:
    """Enhances documentation by filling AI_ENHANCE markers."""
    
    def __init__(self, pillar_name: str, project_root: Path):
        self.pillar_name = pillar_name
        self.project_root = project_root
        self.pillar_src = project_root / "src" / "pillars" / pillar_name
        self.doc_root = project_root / "wiki" / "02_pillars" / pillar_name
        self.analyzer = SourceAnalyzer(project_root)
    
    def find_all_markers(self, section: Optional[str] = None, file_name: Optional[str] = None) -> List[EnhanceMarker]:
        """Find all AI_ENHANCE markers in documentation."""
        markers = []
        
        if file_name:
            # Single file
            search_paths = [self.doc_root / section / file_name] if section else [self.doc_root / file_name]
        elif section:
            # All files in section
            search_paths = list((self.doc_root / section).glob("*.md"))
        else:
            # All markdown files
            search_paths = list(self.doc_root.rglob("*.md"))
        
        for md_file in search_paths:
            if not md_file.exists():
                continue
            
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if '<!-- AI_ENHANCE:' in line:
                    # Extract marker text
                    match = re.search(r'<!-- AI_ENHANCE: (.*?) -->', line)
                    if match:
                        marker_text = match.group(1)
                        
                        # Find context (previous heading)
                        context = self._find_context(lines, i)
                        
                        marker = EnhanceMarker(
                            file_path=md_file,
                            line_number=i,
                            marker_text=marker_text,
                            context=context
                        )
                        markers.append(marker)
        
        return markers
    
    def _find_context(self, lines: List[str], marker_line: int) -> str:
        """Find the nearest heading above the marker."""
        for i in range(marker_line - 1, -1, -1):
            line = lines[i].strip()
            if line.startswith('#'):
                return line
        return ""
    
    def enhance_marker(self, marker: EnhanceMarker) -> str:
        """Generate replacement content for a marker."""
        # Parse file path from doc to find source file
        file_rel_path = self._extract_file_path(marker.file_path)
        
        if not file_rel_path:
            return self._generic_enhancement(marker)
        
        source_file = self.project_root / file_rel_path
        if not source_file.exists():
            return self._generic_enhancement(marker)
        
        # Determine enhancement type from context and marker text
        if "purpose" in marker.context.lower() or "describe" in marker.marker_text.lower():
            return self._enhance_purpose(source_file, marker)
        elif "methods" in marker.context.lower() or "key methods" in marker.marker_text.lower():
            return self._enhance_methods(source_file, marker)
        elif "example" in marker.marker_text.lower() or "usage" in marker.marker_text.lower():
            return self._enhance_usage(source_file, marker)
        elif "responsibilities" in marker.marker_text.lower():
            return self._enhance_responsibilities(source_file, marker)
        elif "signal" in marker.marker_text.lower():
            return self._enhance_signals(source_file, marker)
        elif "dependencies" in marker.marker_text.lower():
            return self._enhance_dependencies(source_file, marker)
        else:
            return self._generic_enhancement(marker)
    
    def _extract_file_path(self, doc_path: Path) -> Optional[str]:
        """Extract source file path from documentation file."""
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look in <cite> block for file references
            cite_match = re.search(r'<cite>.*?\[([^\]]+)\]\(file://([^\)]+)\)', content, re.DOTALL)
            if cite_match:
                return cite_match.group(2)
            
            return None
        except Exception:
            return None
    
    def _enhance_purpose(self, source_file: Path, marker: EnhanceMarker) -> str:
        """Enhance purpose/description section."""
        class_name = self._guess_class_name(source_file)
        purpose = self.analyzer.extract_class_purpose(source_file, class_name)
        
        if purpose:
            return purpose
        return f"Provides {class_name} functionality for the {self.pillar_name.title()} pillar"
    
    def _enhance_methods(self, source_file: Path, marker: EnhanceMarker) -> str:
        """Enhance key methods section."""
        class_name = self._guess_class_name(source_file)
        methods = self.analyzer.extract_key_methods(source_file, class_name)
        
        if methods:
            lines = []
            for method_name, description in methods:
                lines.append(f"- **`{method_name}()`**: {description}")
            return '\n'.join(lines)
        return "- No public methods documented"
    
    def _enhance_usage(self, source_file: Path, marker: EnhanceMarker) -> str:
        """Enhance usage example section."""
        class_name = self._guess_class_name(source_file)
        example = self.analyzer.find_usage_examples(source_file, class_name)
        
        if example:
            return example
        
        # Generate generic example
        return f"""```python
from {self._get_import_path(source_file)} import {class_name}

# Create instance
instance = {class_name}()

# Use methods
# instance.some_method()
```"""
    
    def _enhance_responsibilities(self, source_file: Path, marker: EnhanceMarker) -> str:
        """Enhance responsibilities section."""
        class_name = self._guess_class_name(source_file)
        methods = self.analyzer.extract_key_methods(source_file, class_name)
        
        if methods:
            responsibilities = []
            for method_name, description in methods[:3]:
                responsibilities.append(f"- {description.capitalize()}")
            return '\n'.join(responsibilities)
        return "- Core functionality for the component"
    
    def _enhance_signals(self, source_file: Path, marker: EnhanceMarker) -> str:
        """Enhance signals section."""
        class_name = self._guess_class_name(source_file)
        signals = self.analyzer.extract_signals(source_file, class_name)
        
        if signals:
            lines = []
            for signal_name, signal_args in signals:
                lines.append(f"- **`{signal_name}`**: Emitted with arguments: `{signal_args}`")
            return '\n'.join(lines)
        return "- No signals emitted"
    
    def _enhance_dependencies(self, source_file: Path, marker: EnhanceMarker) -> str:
        """Enhance dependencies section."""
        deps = self.analyzer.extract_dependencies(source_file)
        
        if deps:
            return '\n'.join(f"- `{dep}`" for dep in deps)
        return "- No external dependencies"
    
    def _generic_enhancement(self, marker: EnhanceMarker) -> str:
        """Generic fallback enhancement."""
        return f"[Documentation needed: {marker.marker_text}]"
    
    def _guess_class_name(self, source_file: Path) -> str:
        """Guess class name from file name."""
        stem = source_file.stem
        # Convert snake_case to PascalCase
        parts = stem.split('_')
        return ''.join(word.capitalize() for word in parts)
    
    def _get_import_path(self, source_file: Path) -> str:
        """Get Python import path for a source file."""
        try:
            rel_path = source_file.relative_to(self.project_root / "src")
            parts = list(rel_path.parts[:-1])  # Remove .py file
            return '.'.join(parts)
        except ValueError:
            return "module"
    
    def apply_enhancements(self, markers: List[EnhanceMarker], dry_run: bool = False):
        """Apply all enhancements to files."""
        # Group by file
        by_file: Dict[Path, List[EnhanceMarker]] = {}
        for marker in markers:
            if marker.file_path not in by_file:
                by_file[marker.file_path] = []
            by_file[marker.file_path].append(marker)
        
        for file_path, file_markers in by_file.items():
            self._enhance_file(file_path, file_markers, dry_run)
    
    def _enhance_file(self, file_path: Path, markers: List[EnhanceMarker], dry_run: bool):
        """Enhance a single file."""
        logger.info(f"\n📝 Enhancing {file_path.relative_to(self.doc_root)}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Sort markers by line number (reverse to avoid index shifting)
        markers.sort(key=lambda m: m.line_number, reverse=True)
        
        enhanced_count = 0
        for marker in markers:
            # Generate replacement
            replacement = self.enhance_marker(marker)
            marker.replacement_text = replacement
            
            # Find the marker line
            line = lines[marker.line_number]
            
            # Replace marker with content
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            
            # Check if marker is on its own line or inline
            if line.strip().startswith('<!--'):
                # Replace entire line
                new_lines = [indent_str + line + '\n' for line in replacement.split('\n')]
                lines[marker.line_number:marker.line_number+1] = new_lines
            else:
                # Inline replacement
                lines[marker.line_number] = line.replace(
                    f'<!-- AI_ENHANCE: {marker.marker_text} -->',
                    replacement
                )
            
            enhanced_count += 1
            logger.info(f"  ✓ Enhanced: {marker.marker_text[:50]}...")
        
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            logger.info(f"  💾 Saved {enhanced_count} enhancements")
        else:
            logger.info(f"  🔍 [DRY RUN] Would enhance {enhanced_count} markers")


def main():
    parser = argparse.ArgumentParser(description="Enhance pillar documentation")
    parser.add_argument("pillar", help="Pillar name (e.g., geometry)")
    parser.add_argument("--section", help="Section to enhance (architecture/features/ui_components/api)")
    parser.add_argument("--file", help="Specific file to enhance")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be enhanced without modifying files")
    parser.add_argument("--verbose", action="store_true", help="Show detailed logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    project_root = Path.cwd()
    enhancer = DocEnhancer(args.pillar, project_root)
    
    logger.info(f"🔮 Enhancing {args.pillar} pillar documentation...")
    if args.section:
        logger.info(f"   Section: {args.section}")
    if args.file:
        logger.info(f"   File: {args.file}")
    
    # Find all markers
    markers = enhancer.find_all_markers(args.section, args.file)
    
    if not markers:
        logger.info("✅ No AI_ENHANCE markers found - documentation is complete!")
        return
    
    logger.info(f"\n📊 Found {len(markers)} markers to enhance")
    
    # Apply enhancements
    enhancer.apply_enhancements(markers, args.dry_run)
    
    logger.info(f"\n✨ Enhancement complete!")
    if args.dry_run:
        logger.info("   Run without --dry-run to apply changes")


if __name__ == "__main__":
    main()
