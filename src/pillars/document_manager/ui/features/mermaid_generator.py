"""
Mermaid Code Generator.

**Purpose**:
Convert structured AST back into Mermaid diagram code.
Enables "visual-first" workflow where users build diagrams visually
and the code is generated automatically.

**Features**:
- Clean, readable code generation
- Proper indentation and formatting
- Preserves styles and attributes
- Generates idiomatic Mermaid syntax

**Usage Example**:
```python
# Create AST programmatically
ast = FlowchartAST(direction="TD")
ast.add_node("A", "Start", NodeShape.STADIUM)
ast.add_node("B", "End", NodeShape.STADIUM)
ast.add_edge("A", "B", ArrowType.SOLID, "Flow")

# Generate code
code = FlowchartGenerator.generate(ast)
print(code)
# Output:
# flowchart TD
#     A([Start])
#     B([End])
#     A-->|Flow|B
```

**Thread Safety**: Not thread-safe. Use from Qt main thread only.
"""

from __future__ import annotations

import logging
from typing import List, Any
from .mermaid_ast import FlowchartAST

logger = logging.getLogger(__name__)


# ============================================================================
# FLOWCHART GENERATOR
# ============================================================================

class FlowchartGenerator:
    """
    Generate Mermaid flowchart code from AST.
    
    **Output Format**:
    - Clean indentation (4 spaces)
    - Logical grouping (nodes first, then edges, then styles)
    - Comments preserved (if stored in AST metadata)
    
    **Example**:
    ```python
    ast = FlowchartAST(direction="LR")
    ast.add_node("A", "Start", NodeShape.RECTANGLE)
    ast.add_node("B", "End", NodeShape.RECTANGLE)
    ast.add_edge("A", "B")
    
    code = FlowchartGenerator.generate(ast)
    # Output:
    # flowchart LR
    #     A[Start]
    #     B[End]
    #     A-->B
    ```
    """
    
    # Indentation for diagram elements
    INDENT = "    "
    
    @classmethod
    def generate(cls, ast: FlowchartAST, compact: bool = False) -> str:
        """
        Generate Mermaid flowchart code from AST.
        
        **Args**:
            ast: FlowchartAST structure to convert
            compact: If True, omit blank lines between sections (default: False)
        
        **Returns**:
            str: Complete Mermaid flowchart code
        
        **Example**:
        ```python
        code = FlowchartGenerator.generate(ast)
        
        # Save to file
        with open("diagram.mmd", "w") as f:
            f.write(code)
        
        # Or render directly
        image = WebViewMermaidRenderer.render_mermaid(code)
        ```
        """
        lines: List[str] = []
        
        # 1. Diagram type and direction
        lines.append(f"flowchart {ast.direction}")
        
        if not compact:
            lines.append("")  # Blank line after header
        
        # 2. Nodes (standalone definitions for clarity)
        if ast.nodes:
            for node in ast.nodes:
                lines.append(cls.INDENT + node.to_mermaid_syntax())
            
            if not compact:
                lines.append("")  # Blank line after nodes
        
        # 3. Edges
        if ast.edges:
            for edge in ast.edges:
                lines.append(cls.INDENT + edge.to_mermaid_syntax())
            
            if not compact and ast.styles:
                lines.append("")  # Blank line before styles
        
        # 4. Style definitions
        if ast.styles:
            for style in ast.styles.values():
                lines.append(cls.INDENT + style.to_mermaid_syntax())
        
        return "\n".join(lines)
    
    @classmethod
    def generate_compact(cls, ast: FlowchartAST) -> str:
        """
        Generate compact code (minimal whitespace).
        
        Useful for embedding in constrained spaces or testing.
        
        **Example**:
        ```python
        code = FlowchartGenerator.generate_compact(ast)
        # Shorter output, no blank lines
        ```
        """
        return cls.generate(ast, compact=True)
    
    @classmethod
    def generate_node_only(cls, node: FlowchartNode) -> str:
        """
        Generate code for a single node (for incremental updates).
        
        **Args**:
            node: The node to generate code for
        
        **Returns**:
            str: Mermaid node syntax (e.g., "A[Label]")
        
        **Example**:
        ```python
        node = FlowchartNode("A", "Start", NodeShape.STADIUM)
        code = FlowchartGenerator.generate_node_only(node)
        # Output: "A([Start])"
        ```
        """
        return node.to_mermaid_syntax()
    
    @classmethod
    def generate_edge_only(cls, edge: FlowchartEdge) -> str:
        """
        Generate code for a single edge (for incremental updates).
        
        **Args**:
            edge: The edge to generate code for
        
        **Returns**:
            str: Mermaid edge syntax (e.g., "A-->B")
        
        **Example**:
        ```python
        edge = FlowchartEdge("A", "B", ArrowType.SOLID, "Yes")
        code = FlowchartGenerator.generate_edge_only(edge)
        # Output: "A-->|Yes|B"
        ```
        """
        return edge.to_mermaid_syntax()
    
    @classmethod
    def generate_with_comments(cls, ast: FlowchartAST, header_comment: str = "") -> str:
        """
        Generate code with descriptive comments.
        
        **Args**:
            ast: FlowchartAST structure
            header_comment: Optional comment to add at the top
        
        **Returns**:
            str: Mermaid code with %% comment annotations
        
        **Example**:
        ```python
        code = FlowchartGenerator.generate_with_comments(
            ast,
            header_comment="Generated by IsopGem Mermaid Builder"
        )
        ```
        """
        lines: List[str] = []
        
        # Header comment
        if header_comment:
            lines.append(f"%% {header_comment}")
            lines.append("")
        
        # Diagram declaration
        lines.append(f"flowchart {ast.direction}")
        lines.append("")
        
        # Nodes section
        if ast.nodes:
            lines.append(f"%% Nodes ({len(ast.nodes)} total)")
            for node in ast.nodes:
                lines.append(cls.INDENT + node.to_mermaid_syntax())
            lines.append("")
        
        # Edges section
        if ast.edges:
            lines.append(f"%% Connections ({len(ast.edges)} total)")
            for edge in ast.edges:
                lines.append(cls.INDENT + edge.to_mermaid_syntax())
            lines.append("")
        
        # Styles section
        if ast.styles:
            lines.append(f"%% Style Definitions ({len(ast.styles)} classes)")
            for style in ast.styles.values():
                lines.append(cls.INDENT + style.to_mermaid_syntax())
        
        return "\n".join(lines)


# ============================================================================
# GENERATOR REGISTRY (For future diagram types)
# ============================================================================

GENERATOR_REGISTRY = {
    FlowchartAST: FlowchartGenerator,
    # Future:
    # SequenceAST: SequenceGenerator,
    # ERD_AST: ERGenerator,
    # ClassAST: ClassGenerator,
}


def auto_generate(ast: Any) -> str:
    """
    Automatically detect AST type and generate appropriate code.
    
    **Args**:
        ast: Any supported AST type
    
    **Returns**:
        str: Generated Mermaid code
    
    **Raises**:
        TypeError: If AST type is not recognized
    
    **Example**:
    ```python
    # Works with any AST type
    code = auto_generate(flowchart_ast)
    code = auto_generate(sequence_ast)  # Future
    ```
    """
    ast_type = type(ast)
    
    if ast_type in GENERATOR_REGISTRY:
        generator_class = GENERATOR_REGISTRY[ast_type]
        return generator_class.generate(ast)
    
    raise TypeError(f"No generator registered for AST type: {ast_type.__name__}")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_and_generate(ast: FlowchartAST) -> tuple[str, list[str]]:
    """
    Validate AST and generate code, returning both code and any errors.
    
    **Args**:
        ast: FlowchartAST to validate and convert
    
    **Returns**:
        tuple[str, list[str]]: (generated_code, validation_errors)
    
    **Example**:
    ```python
    code, errors = validate_and_generate(ast)
    
    if errors:
        print("⚠️ Validation warnings:")
        for error in errors:
            print(f"  - {error}")
    
    # Still returns code even if there are warnings
    print(code)
    ```
    """
    errors = ast.validate()
    code = FlowchartGenerator.generate(ast)
    return code, errors


def quick_flowchart(
    nodes: list[tuple[str, str]],
    edges: list[tuple[str, str]],
    direction: str = "TD"
) -> str:
    """
    Quick flowchart generation from simple lists.
    
    **Args**:
        nodes: List of (id, label) tuples
        edges: List of (from_id, to_id) tuples
        direction: Flow direction (default: "TD")
    
    **Returns**:
        str: Generated Mermaid code
    
    **Example**:
    ```python
    # Create a simple flowchart in one call
    code = quick_flowchart(
        nodes=[("A", "Start"), ("B", "Process"), ("C", "End")],
        edges=[("A", "B"), ("B", "C")],
        direction="LR"
    )
    
    # Output:
    # flowchart LR
    #     A[Start]
    #     B[Process]
    #     C[End]
    #     A-->B
    #     B-->C
    ```
    """
    from .mermaid_ast import NodeShape, ArrowType
    
    ast = FlowchartAST(direction=direction)
    
    # Add nodes
    for node_id, label in nodes:
        ast.add_node(node_id, label, NodeShape.RECTANGLE)
    
    # Add edges
    for from_id, to_id in edges:
        ast.add_edge(from_id, to_id, ArrowType.SOLID)
    
    return FlowchartGenerator.generate(ast)
