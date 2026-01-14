"""
Mermaid Code Parser.

**Purpose**:
Convert Mermaid diagram code into structured AST for visual editing.
Enables "code-first" workflow where users can type or paste existing diagrams.

**Supported Diagrams**:
- Flowchart/Graph (Phase 1 MVP)
- Sequence Diagram (Phase 2 - TODO)
- ER Diagram (Phase 3 - TODO)

**Usage Example**:
```python
code = '''
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
'''

ast = FlowchartParser.parse(code)
print(f"Found {len(ast.nodes)} nodes and {len(ast.edges)} edges")
```

**Limitations**:
- Handles common syntax patterns (not 100% Mermaid spec compliant)
- Complex features (styling, subgraphs) may require refinement
- Best-effort parsing: invalid syntax may be skipped rather than error

**Thread Safety**: Not thread-safe. Use from Qt main thread only.
"""

import re
import logging
from typing import Optional, Tuple
from .mermaid_ast import (
    FlowchartAST, FlowchartNode, FlowchartEdge,
    NodeShape, ArrowType, StyleDefinition
)

logger = logging.getLogger(__name__)


# ============================================================================
# FLOWCHART PARSER
# ============================================================================

class FlowchartParser:
    """
    Parse Mermaid flowchart/graph code into AST.
    
    **Features**:
    - Extracts nodes with all shape types
    - Parses connections with arrow types and labels
    - Recognizes style class definitions and applications
    - Handles comments and whitespace
    
    **Example**:
    ```python
    code = "flowchart LR\\n    A[Start]-->B[End]"
    ast = FlowchartParser.parse(code)
    assert ast.direction == "LR"
    assert len(ast.nodes) == 2
    assert len(ast.edges) == 1
    ```
    """
    
    # Direction pattern: graph/flowchart followed by direction
    DIRECTION_PATTERN = re.compile(r'^(?:graph|flowchart)\s+(TD|TB|BT|RL|LR)', re.IGNORECASE)
    
    # Node patterns for each shape type
    NODE_PATTERNS = [
        # Stadium: A([Label])
        (re.compile(r'(\w+)\(\[([^\]]+)\]\)'), NodeShape.STADIUM),
        # Subroutine: A[[Label]]
        (re.compile(r'(\w+)\[\[([^\]]+)\]\]'), NodeShape.SUBROUTINE),
        # Cylindrical: A[(Label)]
        (re.compile(r'(\w+)\[\(([^\)]+)\)\]'), NodeShape.CYLINDRICAL),
        # Circle: A((Label))
        (re.compile(r'(\w+)\(\(([^\)]+)\)\)'), NodeShape.CIRCLE),
        # Hexagon: A{{Label}}
        (re.compile(r'(\w+)\{\{([^\}]+)\}\}'), NodeShape.HEXAGON),
        # Diamond: A{Label}
        (re.compile(r'(\w+)\{([^\}]+)\}'), NodeShape.DIAMOND),
        # Parallelogram: A[/Label/]
        (re.compile(r'(\w+)\[/([^\]]+)/\]'), NodeShape.PARALLELOGRAM),
        # Trapezoid: A[\Label/]
        (re.compile(r'(\w+)\[\\([^\]]+)/\]'), NodeShape.TRAPEZOID),
        # Rectangle: A[Label] (must be last - most generic)
        (re.compile(r'(\w+)\[([^\]]+)\]'), NodeShape.RECTANGLE),
        # Rounded: A(Label)
        (re.compile(r'(\w+)\(([^\)]+)\)'), NodeShape.ROUNDED),
    ]
    
    # Arrow patterns (order matters - check longer patterns first)
    ARROW_PATTERNS = [
        (r'===', ArrowType.THICK_LINE),
        (r'==>', ArrowType.THICK),
        (r'\.\.\.', ArrowType.DOTTED_LINE),
        (r'\.\.->', ArrowType.DOTTED),
        (r'~~~', ArrowType.INVISIBLE),
        (r'---', ArrowType.SOLID_LINE),
        (r'-->', ArrowType.SOLID),
    ]
    
    # Style class definition: classDef className fill:#f96,stroke:#333
    CLASSDEF_PATTERN = re.compile(r'classDef\s+(\w+)\s+(.+)')
    
    # Style class application: A:::className
    STYLECLASS_PATTERN = re.compile(r'(\w+):::(\w+)')
    
    @classmethod
    def parse(cls, code: str) -> FlowchartAST:
        """
        Parse Mermaid flowchart code into AST.
        
        **Args**:
            code: Mermaid flowchart source code
        
        **Returns**:
            FlowchartAST: Structured representation of the diagram
        
        **Example**:
        ```python
        code = '''
        flowchart TD
            A[Start] --> B{Decision}
            B -->|Yes| C[End]
        '''
        ast = FlowchartParser.parse(code)
        ```
        """
        ast = FlowchartAST()
        lines = code.strip().split('\n')
        
        # Track nodes we've seen (to avoid duplicates)
        seen_nodes = set()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('%%'):
                continue
            
            try:
                # Check for direction declaration
                direction_match = cls.DIRECTION_PATTERN.match(line)
                if direction_match:
                    ast.direction = direction_match.group(1).upper()
                    continue
                
                # Check for style class definition
                classdef_match = cls.CLASSDEF_PATTERN.match(line)
                if classdef_match:
                    class_name = classdef_match.group(1)
                    props_str = classdef_match.group(2)
                    style = cls._parse_style_definition(class_name, props_str)
                    if style:
                        ast.add_style(style)
                    continue
                
                # Check for edge/connection
                edge = cls._parse_edge(line, ast)
                if edge:
                    ast.edges.append(edge)
                    
                    # Extract any nodes mentioned in the edge
                    for node_id in [edge.from_id, edge.to_id]:
                        if node_id not in seen_nodes:
                            # Check if there's node syntax in the line
                            node = cls._extract_node_from_line(line, node_id)
                            if node:
                                ast.nodes.append(node)
                                seen_nodes.add(node_id)
                    continue
                
                # Check for standalone node definition
                node = cls._parse_node(line)
                if node and node.id not in seen_nodes:
                    ast.nodes.append(node)
                    seen_nodes.add(node.id)
                    continue
                
            except Exception as e:
                logger.warning(f"Failed to parse line {line_num}: {line[:50]}... Error: {e}")
                continue
        
        return ast
    
    @classmethod
    def _parse_node(cls, line: str) -> Optional[FlowchartNode]:
        """
        Parse a standalone node definition.
        
        Returns None if no valid node pattern found.
        """
        # Try each node pattern
        for pattern, shape in cls.NODE_PATTERNS:
            match = pattern.search(line)
            if match:
                node_id = match.group(1)
                label = match.group(2).strip()
                
                # Check for style class application
                style_class = None
                styleclass_match = cls.STYLECLASS_PATTERN.search(line)
                if styleclass_match and styleclass_match.group(1) == node_id:
                    style_class = styleclass_match.group(2)
                
                return FlowchartNode(
                    id=node_id,
                    label=label,
                    shape=shape,
                    style_class=style_class
                )
        
        return None
    
    @classmethod
    def _extract_node_from_line(cls, line: str, node_id: str) -> Optional[FlowchartNode]:
        """
        Extract node definition for a specific ID from a line.
        Used when parsing edges that define nodes inline.
        """
        # Try to find the node_id followed by shape syntax
        for pattern, shape in cls.NODE_PATTERNS:
            # Adjust pattern to match specific node_id
            specific_pattern = re.compile(pattern.pattern.replace(r'(\w+)', f'({node_id})'))
            match = specific_pattern.search(line)
            if match:
                label = match.group(2).strip()
                
                # Check for style class
                style_class = None
                styleclass_match = cls.STYLECLASS_PATTERN.search(line)
                if styleclass_match and styleclass_match.group(1) == node_id:
                    style_class = styleclass_match.group(2)
                
                return FlowchartNode(
                    id=node_id,
                    label=label,
                    shape=shape,
                    style_class=style_class
                )
        
        # If no shape syntax found, create a simple rectangle node
        return FlowchartNode(
            id=node_id,
            label=node_id,  # Use ID as label
            shape=NodeShape.RECTANGLE
        )
    
    @classmethod
    def _parse_edge(cls, line: str, ast: FlowchartAST) -> Optional[FlowchartEdge]:
        """
        Parse an edge/connection from a line.
        
        Format: A --> B
        Format: A -->|Label| B
        Format: A[Start] -->|Label| B[End]
        """
        # Try each arrow pattern (longest first)
        for arrow_str, arrow_type in cls.ARROW_PATTERNS:
            if arrow_str in line:
                # Split on the arrow
                parts = line.split(arrow_str)
                if len(parts) != 2:
                    continue
                
                left = parts[0].strip()
                right = parts[1].strip()
                
                # Extract source node ID (before arrow)
                from_id = cls._extract_node_id(left)
                if not from_id:
                    continue
                
                # Check for edge label: |Label|
                label = None
                label_match = re.search(r'\|([^\|]+)\|', right)
                if label_match:
                    label = label_match.group(1).strip()
                    # Remove label from right part to get target ID
                    right = re.sub(r'\|[^\|]+\|', '', right).strip()
                
                # Extract target node ID (after arrow)
                to_id = cls._extract_node_id(right)
                if not to_id:
                    continue
                
                return FlowchartEdge(
                    from_id=from_id,
                    to_id=to_id,
                    arrow_type=arrow_type,
                    label=label
                )
        
        return None
    
    @classmethod
    def _extract_node_id(cls, text: str) -> Optional[str]:
        """
        Extract node ID from text (may include shape syntax).
        
        Examples:
            "A" → "A"
            "A[Label]" → "A"
            "A([Label])" → "A"
            "  A  " → "A"
        """
        text = text.strip()
        
        # Try to match node ID followed by shape syntax
        for pattern, _ in cls.NODE_PATTERNS:
            match = pattern.match(text)
            if match:
                return match.group(1)
        
        # If no shape syntax, assume the whole text is the ID
        # Extract word characters only
        id_match = re.match(r'(\w+)', text)
        if id_match:
            return id_match.group(1)
        
        return None
    
    @classmethod
    def _parse_style_definition(cls, class_name: str, props_str: str) -> Optional[StyleDefinition]:
        """
        Parse style class definition properties.
        
        Example: "fill:#f96,stroke:#333,stroke-width:2px"
        """
        style = StyleDefinition(class_name=class_name)
        
        # Split by comma
        props = props_str.split(',')
        
        for prop in props:
            prop = prop.strip()
            if ':' not in prop:
                continue
            
            key, value = prop.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # Map to StyleDefinition attributes
            if key == 'fill':
                style.fill = value
            elif key == 'stroke':
                style.stroke = value
            elif key == 'stroke-width':
                style.stroke_width = value
            elif key == 'color':
                style.color = value
            elif key == 'font-size':
                style.font_size = value
        
        return style


# ============================================================================
# PARSER REGISTRY (For future diagram types)
# ============================================================================

PARSER_REGISTRY = {
    'flowchart': FlowchartParser,
    'graph': FlowchartParser,
    # Future:
    # 'sequenceDiagram': SequenceParser,
    # 'erDiagram': ERParser,
    # 'classDiagram': ClassParser,
}


def auto_parse(code: str) -> Optional[FlowchartAST]:
    """
    Automatically detect diagram type and parse accordingly.
    
    **Args**:
        code: Mermaid diagram code (any supported type)
    
    **Returns**:
        AST object (type depends on diagram type), or None if unrecognized
    
    **Example**:
    ```python
    code = load_diagram_from_file()
    ast = auto_parse(code)
    
    if isinstance(ast, FlowchartAST):
        print("This is a flowchart")
    ```
    """
    # Check first non-empty, non-comment line for diagram type
    for line in code.split('\n'):
        line = line.strip()
        if not line or line.startswith('%%'):
            continue
        
        # Check for diagram type keyword
        for keyword, parser_class in PARSER_REGISTRY.items():
            if line.lower().startswith(keyword):
                return parser_class.parse(code)
        
        # If we hit a non-diagram-declaration line, stop
        break
    
    # Default to flowchart parser (most common)
    logger.warning("Could not detect diagram type, defaulting to flowchart parser")
    return FlowchartParser.parse(code)
