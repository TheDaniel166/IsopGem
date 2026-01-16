#!/usr/bin/env python3
"""
Generate comprehensive pillar documentation from source code.

This script creates 80% complete documentation by:
- Extracting classes, methods, and docstrings from source
- Generating structured markdown with citations
- Creating method signatures and parameter documentation
- Building skeleton sections for AI enhancement
- Maintaining consistent formatting across pillars

Usage:
    python scripts/generate_pillar_docs.py gematria
    python scripts/generate_pillar_docs.py geometry --api-only
    python scripts/generate_pillar_docs.py astrology --force
"""

import ast
import argparse
import inspect
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class ClassInfo:
    """Information about a class extracted from source."""
    name: str
    docstring: Optional[str]
    bases: List[str]
    methods: List['MethodInfo']
    file_path: str
    line_number: int
    decorators: List[str]


@dataclass
class MethodInfo:
    """Information about a method extracted from source."""
    name: str
    signature: str
    docstring: Optional[str]
    is_public: bool
    is_property: bool
    is_abstract: bool
    parameters: List[Dict[str, Any]]
    returns: Optional[str]
    line_number: int


@dataclass
class ServiceInfo:
    """High-level service information."""
    name: str
    class_info: ClassInfo
    purpose: str
    dependencies: List[str]
    consumers: List[str]


class CodeAnalyzer:
    """Analyzes Python source code to extract documentation info."""
    
    def __init__(self, pillar_path: Path):
        self.pillar_path = pillar_path
        self.project_root = pillar_path.parent.parent.parent
    
    def analyze_file(self, file_path: Path) -> List[ClassInfo]:
        """Extract all classes from a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node, file_path)
                    classes.append(class_info)
            
            return classes
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return []
    
    def _extract_class_info(self, node: ast.ClassDef, file_path: Path) -> ClassInfo:
        """Extract information from a class AST node."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_method_info(item)
                methods.append(method_info)
        
        return ClassInfo(
            name=node.name,
            docstring=ast.get_docstring(node),
            bases=[self._get_base_name(base) for base in node.bases],
            methods=methods,
            file_path=str(file_path.relative_to(self.project_root)),
            line_number=node.lineno,
            decorators=[self._get_decorator_name(dec) for dec in node.decorator_list]
        )
    
    def _extract_method_info(self, node: ast.FunctionDef) -> MethodInfo:
        """Extract information from a method AST node."""
        params = []
        for arg in node.args.args:
            param = {
                "name": arg.arg,
                "annotation": ast.unparse(arg.annotation) if arg.annotation else None
            }
            params.append(param)
        
        return_annotation = None
        if node.returns:
            return_annotation = ast.unparse(node.returns)
        
        is_property = any(
            self._get_decorator_name(dec) == "property" 
            for dec in node.decorator_list
        )
        is_abstract = any(
            self._get_decorator_name(dec) == "abstractmethod"
            for dec in node.decorator_list
        )
        
        return MethodInfo(
            name=node.name,
            signature=self._build_signature(node),
            docstring=ast.get_docstring(node),
            is_public=not node.name.startswith('_'),
            is_property=is_property,
            is_abstract=is_abstract,
            parameters=params,
            returns=return_annotation,
            line_number=node.lineno
        )
    
    def _build_signature(self, node: ast.FunctionDef) -> str:
        """Build method signature string."""
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        sig = f"{node.name}({', '.join(args)})"
        if node.returns:
            sig += f" -> {ast.unparse(node.returns)}"
        return sig
    
    def _get_base_name(self, base: ast.expr) -> str:
        """Get base class name."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return ast.unparse(base)
        return "Unknown"
    
    def _get_decorator_name(self, dec: ast.expr) -> str:
        """Get decorator name."""
        if isinstance(dec, ast.Name):
            return dec.id
        elif isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name):
                return dec.func.id
        return ast.unparse(dec)
    
    def find_dependencies(self, file_path: Path) -> List[str]:
        """Find import dependencies in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            return imports
        except Exception:
            return []


class DocGenerator:
    """Generates markdown documentation from code analysis."""
    
    def __init__(self, pillar_name: str, output_dir: Path):
        self.pillar_name = pillar_name
        self.output_dir = output_dir
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def generate_api_doc(self, service_info: ServiceInfo) -> str:
        """Generate API reference documentation for a service."""
        class_info = service_info.class_info
        
        doc = f"""# {class_info.name} API Reference

<!-- Last Verified: {self.today} -->

<cite>
**Referenced Files in This Document**
- [{class_info.file_path}](file://{class_info.file_path})
"""
        
        # Add dependencies to cite block
        if service_info.dependencies:
            for dep in service_info.dependencies[:5]:  # Limit to 5
                doc += f"- [{dep}](file://{dep})\n"
        
        doc += """</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Class Overview](#class-overview)
3. [Core Methods](#core-methods)
4. [Usage Examples](#usage-examples)
5. [Error Handling](#error-handling)
6. [Dependencies](#dependencies)
7. [Performance Considerations](#performance-considerations)

## Introduction

"""
        
        # Use docstring if available
        if class_info.docstring:
            doc += f"{class_info.docstring}\n\n"
        else:
            doc += f"**`{class_info.name}`** is <!-- AI_ENHANCE: Add service description -->\n\n"
        
        doc += f"**Architectural Role**: <!-- AI_ENHANCE: Define role (Service/Model/View/Repository) -->\n"
        doc += f"- **Layer**: <!-- AI_ENHANCE: Which architectural layer -->\n"
        doc += f"- **Responsibilities**: <!-- AI_ENHANCE: List key responsibilities -->\n"
        doc += f"- **Dependencies**: {', '.join(service_info.dependencies[:3]) if service_info.dependencies else 'None'}\n"
        doc += f"- **Consumers**: {', '.join(service_info.consumers[:3]) if service_info.consumers else 'Unknown'}\n\n"
        
        doc += "## Class Overview\n\n"
        doc += f"```python\nclass {class_info.name}"
        if class_info.bases:
            doc += f"({', '.join(class_info.bases)})"
        doc += ":\n"
        if class_info.docstring:
            doc += f'    """{class_info.docstring}"""\n'
        doc += "```\n\n"
        
        # Add class diagram placeholder
        doc += "<!-- AI_ENHANCE: Add class diagram showing relationships -->\n\n"
        
        doc += "## Core Methods\n\n"
        
        # Document public methods
        public_methods = [m for m in class_info.methods if m.is_public and not m.name.startswith('__')]
        
        for method in public_methods:
            doc += f"### {method.name}\n\n"
            doc += f"```python\ndef {method.signature}:\n```\n\n"
            
            if method.docstring:
                doc += f"**Purpose**: {method.docstring.split('.')[0]}.\n\n"
            else:
                doc += "**Purpose**: <!-- AI_ENHANCE: Describe method purpose -->\n\n"
            
            # Parameters
            if method.parameters:
                doc += "**Parameters:**\n"
                for param in method.parameters:
                    param_type = param.get('annotation', 'Any')
                    doc += f"- `{param['name']}` ({param_type}): <!-- AI_ENHANCE: Describe parameter -->\n"
                doc += "\n"
            
            # Returns
            if method.returns:
                doc += f"**Returns**: `{method.returns}` - <!-- AI_ENHANCE: Describe return value -->\n\n"
            
            # Example placeholder
            doc += "**Example:**\n```python\n# <!-- AI_ENHANCE: Add usage example -->\n```\n\n"
        
        doc += "## Usage Examples\n\n"
        doc += "<!-- AI_ENHANCE: Add comprehensive usage examples -->\n\n"
        
        doc += "## Error Handling\n\n"
        doc += "<!-- AI_ENHANCE: Document error types and handling strategies -->\n\n"
        
        doc += "## Dependencies\n\n"
        if service_info.dependencies:
            doc += "```mermaid\ngraph LR\n"
            doc += f"    {class_info.name}"
            for dep in service_info.dependencies[:5]:
                dep_name = Path(dep).stem
                doc += f" --> {dep_name}\n"
            doc += "```\n\n"
        
        doc += "## Performance Considerations\n\n"
        doc += "<!-- AI_ENHANCE: Add complexity analysis and optimization notes -->\n\n"
        
        doc += "---\n\n"
        doc += "**See Also:**\n"
        doc += "- [../REFERENCE.md](../REFERENCE.md) - Pillar reference\n"
        doc += "- <!-- AI_ENHANCE: Add related documentation links -->\n\n"
        
        doc += "**Revision History:**\n"
        doc += f"- {self.today}: Initial auto-generated documentation\n"
        
        return doc
    
    def generate_feature_doc(self, feature_name: str, ui_files: List[Path], service_files: List[Path]) -> str:
        """Generate feature documentation."""
        
        doc = f"""# {feature_name.replace('_', ' ').title()}: Feature Documentation

<!-- Last Verified: {self.today} -->

<cite>
**Referenced Files in This Document**
"""
        for file in ui_files[:3]:
            rel_path = file.relative_to(Path.cwd())
            doc += f"- [{rel_path.name}](file://{rel_path})\n"
        for file in service_files[:3]:
            rel_path = file.relative_to(Path.cwd())
            doc += f"- [{rel_path.name}](file://{rel_path})\n"
        
        doc += """</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Feature Overview](#feature-overview)
3. [Architecture](#architecture)
4. [User Workflow](#user-workflow)
5. [Integration Points](#integration-points)
6. [Usage Examples](#usage-examples)
7. [Extension Points](#extension-points)

## Introduction

<!-- AI_ENHANCE: Describe the feature's purpose and primary use cases -->

**Primary Use Cases:**
- <!-- AI_ENHANCE: List use cases -->

## Feature Overview

### Core Capabilities

<!-- AI_ENHANCE: List and describe core capabilities -->

### UI Components

<!-- AI_ENHANCE: Add component diagram -->

## Architecture

### Component Interaction

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Service
    participant Data
    
    Note over User,Data: <!-- AI_ENHANCE: Add sequence diagram -->
```

## User Workflow

<!-- AI_ENHANCE: Add user journey flowchart and description -->

## Integration Points

<!-- AI_ENHANCE: Describe how feature integrates with other components -->

## Usage Examples

<!-- AI_ENHANCE: Add practical usage examples -->

## Extension Points

<!-- AI_ENHANCE: Document how to extend or customize the feature -->

---

**See Also:**
- [../GUIDES.md](../GUIDES.md) - User guides
- <!-- AI_ENHANCE: Add related links -->

**Revision History:**
- {self.today}: Initial auto-generated documentation
"""
        return doc
    
    def generate_index(self, pillar_name: str, doc_structure: Dict[str, List[str]]) -> str:
        """Generate comprehensive index document."""
        
        doc = f"""# {pillar_name.title()} Pillar Documentation Index

<!-- Last Verified: {self.today} -->

**"<!-- AI_ENHANCE: Add pillar motto/quote -->"**

This index provides a comprehensive map of the {pillar_name.title()} Pillar documentation.

---

## Quick Navigation

### Core Documents (Covenant Style)

- **[REFERENCE.md](REFERENCE.md)** - Technical anatomy
- **[EXPLANATION.md](EXPLANATION.md)** - Theoretical foundations  
- **[GUIDES.md](GUIDES.md)** - Practical how-to

---

## Deep Documentation Structure

### Architecture

"""
        
        if 'architecture' in doc_structure:
            for doc in doc_structure['architecture']:
                doc += f"- **[{doc}](architecture/{doc})**\n"
        else:
            doc += "<!-- AI_ENHANCE: Add architecture documentation -->\n"
        
        doc += "\n### API Reference\n\n"
        
        if 'api' in doc_structure:
            for doc_file in doc_structure['api']:
                doc += f"- **[{doc_file}](api/{doc_file})**\n"
        else:
            doc += "<!-- AI_ENHANCE: Add API documentation -->\n"
        
        doc += "\n### Features\n\n"
        
        if 'features' in doc_structure:
            for doc_file in doc_structure['features']:
                doc += f"- **[{doc_file}](features/{doc_file})**\n"
        else:
            doc += "<!-- AI_ENHANCE: Add feature documentation -->\n"
        
        doc += "\n### UI Components\n\n"
        
        if 'ui_components' in doc_structure:
            for doc_file in doc_structure['ui_components']:
                doc += f"- **[{doc_file}](ui_components/{doc_file})**\n"
        else:
            doc += "<!-- AI_ENHANCE: Add UI component documentation -->\n"
        
        doc += f"""

---

## Documentation Status

### Complete ✓
<!-- AI_ENHANCE: List completed documentation -->

### In Progress 🔄
<!-- AI_ENHANCE: List in-progress documentation -->

### Planned 📋
<!-- AI_ENHANCE: List planned documentation -->

---

## Reading Paths

### For New Developers
1. [EXPLANATION.md](EXPLANATION.md) - Understand the "why"
2. <!-- AI_ENHANCE: Add recommended reading path -->

### For Feature Implementation
1. [REFERENCE.md](REFERENCE.md) - Quick component lookup
2. <!-- AI_ENHANCE: Add implementation path -->

---

**Last Updated**: {self.today}
**Documentation Version**: 1.0.0 (auto-generated)

---

**Navigation:**
- [← Back to Grimoires Index](../README.md)
- [↑ Foundations](../../00_foundations/README.md)
"""
        return doc


def main():
    parser = argparse.ArgumentParser(description="Generate pillar documentation")
    parser.add_argument("pillar", help="Pillar name (e.g., gematria, geometry)")
    parser.add_argument("--api-only", action="store_true", help="Generate only API docs")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--output", help="Output directory (default: wiki/02_pillars/PILLAR)")
    
    args = parser.parse_args()
    
    # Setup paths
    project_root = Path.cwd()
    pillar_src = project_root / "src" / "pillars" / args.pillar
    
    if not pillar_src.exists():
        print(f"Error: Pillar source not found: {pillar_src}")
        sys.exit(1)
    
    output_dir = Path(args.output) if args.output else project_root / "wiki" / "02_pillars" / args.pillar
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating documentation for {args.pillar} pillar...")
    print(f"Source: {pillar_src}")
    print(f"Output: {output_dir}")
    
    # Create subdirectories
    (output_dir / "api").mkdir(exist_ok=True)
    (output_dir / "architecture").mkdir(exist_ok=True)
    (output_dir / "features").mkdir(exist_ok=True)
    (output_dir / "ui_components").mkdir(exist_ok=True)
    
    # Initialize analyzers
    analyzer = CodeAnalyzer(pillar_src)
    generator = DocGenerator(args.pillar, output_dir)
    
    # Analyze services
    services_dir = pillar_src / "services"
    if services_dir.exists():
        print("\nAnalyzing services...")
        for py_file in services_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            classes = analyzer.analyze_file(py_file)
            deps = analyzer.find_dependencies(py_file)
            
            for class_info in classes:
                service_info = ServiceInfo(
                    name=class_info.name,
                    class_info=class_info,
                    purpose="",  # Will be enhanced by AI
                    dependencies=deps,
                    consumers=[]  # Will be enhanced by AI
                )
                
                doc_content = generator.generate_api_doc(service_info)
                
                output_file = output_dir / "api" / f"{py_file.stem}.md"
                if output_file.exists() and not args.force:
                    print(f"  Skipping {output_file.name} (exists)")
                else:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(doc_content)
                    print(f"  ✓ Generated {output_file.name}")
    
    # Generate INDEX
    doc_structure = {
        'api': [f.name for f in (output_dir / "api").glob("*.md")],
        'architecture': [f.name for f in (output_dir / "architecture").glob("*.md")],
        'features': [f.name for f in (output_dir / "features").glob("*.md")],
        'ui_components': [f.name for f in (output_dir / "ui_components").glob("*.md")],
    }
    
    index_content = generator.generate_index(args.pillar, doc_structure)
    index_file = output_dir / "INDEX.md"
    
    if not index_file.exists() or args.force:
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        print(f"\n✓ Generated INDEX.md")
    
    print(f"\n✅ Documentation generation complete!")
    print(f"\nNext steps:")
    print(f"1. Review generated files in {output_dir}")
    print(f"2. Search for '<!-- AI_ENHANCE:' markers")
    print(f"3. Use AI assistant to fill in detailed sections")
    print(f"4. Add Mermaid diagrams where indicated")
    print(f"5. Add usage examples and best practices")


if __name__ == "__main__":
    main()
