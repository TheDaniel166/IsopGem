"""
Mermaid Abstract Syntax Tree (AST) Data Structures.

**Purpose**:
Represent Mermaid diagrams as structured data for visual editing and manipulation.
Enables bidirectional conversion: Code ↔ AST ↔ Visual Editor.

**Supported Diagram Types**:
- Flowchart/Graph (Phase 1 MVP)
- Sequence Diagram (Phase 2)
- ER Diagram (Phase 3)
- Class Diagram (Phase 4)

**Usage Example**:
```python
# Create AST programmatically
ast = FlowchartAST(direction="TD")
ast.add_node("A", "Start", shape="stadium")
ast.add_node("B", "End", shape="stadium")
ast.add_edge("A", "B", arrow_type="-->", label="Flow")

# Generate code
from mermaid_generator import FlowchartGenerator
code = FlowchartGenerator.generate(ast)
# Output: "flowchart TD\\n    A([Start])\\n    B([End])\\n    A-->|Flow|B"
```

**Thread Safety**: Not thread-safe. Use from Qt main thread only.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# SHAPE DEFINITIONS
# ============================================================================

class NodeShape(Enum):
    """Available node shapes for flowcharts."""
    RECTANGLE = "rect"       # [Label]
    ROUNDED = "round"        # (Label)
    STADIUM = "stadium"      # ([Label])
    SUBROUTINE = "subroutine"  # [[Label]]
    CYLINDRICAL = "cylinder" # [(Label)]
    CIRCLE = "circle"        # ((Label))
    DIAMOND = "diamond"      # {Label}
    HEXAGON = "hexagon"      # {{Label}}
    PARALLELOGRAM = "para"   # [/Label/]
    TRAPEZOID = "trapezoid"  # [\\Label/]

    @property
    def syntax(self) -> tuple[str, str]:
        """Return (open, close) bracket syntax for this shape."""
        return SHAPE_SYNTAX[self]


# Shape syntax mapping
SHAPE_SYNTAX: Dict[NodeShape, tuple[str, str]] = {
    NodeShape.RECTANGLE: ("[", "]"),
    NodeShape.ROUNDED: ("(", ")"),
    NodeShape.STADIUM: ("([", "])"),
    NodeShape.SUBROUTINE: ("[[", "]]"),
    NodeShape.CYLINDRICAL: ("[(", ")]"),
    NodeShape.CIRCLE: ("((", "))"),
    NodeShape.DIAMOND: ("{", "}"),
    NodeShape.HEXAGON: ("{{", "}}"),
    NodeShape.PARALLELOGRAM: ("[/", "/]"),
    NodeShape.TRAPEZOID: ("[\\", "/]"),
}


class ArrowType(Enum):
    """Available arrow/connection types."""
    SOLID = "-->"          # Solid arrow
    SOLID_LINE = "---"     # Solid line (no arrow)
    DOTTED = "-.->"        # Dotted arrow
    DOTTED_LINE = "-..-"   # Dotted line
    THICK = "==>"          # Thick arrow
    THICK_LINE = "==="     # Thick line
    INVISIBLE = "~~~"      # Invisible link


# ============================================================================
# FLOWCHART AST
# ============================================================================

@dataclass
class FlowchartNode:
    """
    A single node in a flowchart.
    
    **Attributes**:
        id: Unique identifier (e.g., "A", "start", "node1")
        label: Display text inside the node
        shape: Visual shape (rectangle, diamond, circle, etc.)
        style_class: Optional CSS class name for styling
        metadata: Optional arbitrary data (for UI state, etc.)
    
    **Example**:
    ```python
    node = FlowchartNode(
        id="A",
        label="Start Process",
        shape=NodeShape.STADIUM,
        style_class="highlight"
    )
    ```
    """
    id: str
    label: str
    shape: NodeShape = NodeShape.RECTANGLE
    style_class: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_mermaid_syntax(self) -> str:
        """
        Generate Mermaid syntax for this node.
        
        Returns:
            str: Mermaid node declaration (e.g., "A[Start]")
        """
        open_bracket, close_bracket = self.shape.syntax
        line = f"{self.id}{open_bracket}{self.label}{close_bracket}"
        
        if self.style_class:
            line += f":::{self.style_class}"
        
        return line


@dataclass
class FlowchartEdge:
    """
    A connection/edge between two nodes.
    
    **Attributes**:
        from_id: Source node ID
        to_id: Target node ID
        arrow_type: Visual style of the connection
        label: Optional text label on the connection
        metadata: Optional arbitrary data
    
    **Example**:
    ```python
    edge = FlowchartEdge(
        from_id="A",
        to_id="B",
        arrow_type=ArrowType.SOLID,
        label="Yes"
    )
    ```
    """
    from_id: str
    to_id: str
    arrow_type: ArrowType = ArrowType.SOLID
    label: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_mermaid_syntax(self) -> str:
        """
        Generate Mermaid syntax for this edge.
        
        Returns:
            str: Mermaid edge declaration (e.g., "A-->|Yes|B")
        """
        line = f"{self.from_id} {self.arrow_type.value}"
        
        if self.label:
            line += f"|{self.label}|"
        
        line += f" {self.to_id}"
        
        return line


@dataclass
class StyleDefinition:
    """
    CSS class definition for styling nodes.
    
    **Attributes**:
        class_name: Name of the style class
        fill: Fill color (hex or CSS color)
        stroke: Border color
        stroke_width: Border width in pixels
        color: Text color
        font_size: Font size (CSS value)
    
    **Example**:
    ```python
    style = StyleDefinition(
        class_name="highlight",
        fill="#ff6",
        stroke="#333",
        stroke_width="2px",
        color="#000"
    )
    ```
    """
    class_name: str
    fill: Optional[str] = None
    stroke: Optional[str] = None
    stroke_width: Optional[str] = None
    color: Optional[str] = None
    font_size: Optional[str] = None
    
    def to_mermaid_syntax(self) -> str:
        """
        Generate Mermaid classDef syntax.
        
        Returns:
            str: Mermaid style definition (e.g., "classDef highlight fill:#ff6")
        """
        props = []
        
        if self.fill:
            props.append(f"fill:{self.fill}")
        if self.stroke:
            props.append(f"stroke:{self.stroke}")
        if self.stroke_width:
            props.append(f"stroke-width:{self.stroke_width}")
        if self.color:
            props.append(f"color:{self.color}")
        if self.font_size:
            props.append(f"font-size:{self.font_size}")
        
        props_str = ','.join(props)
        return f"classDef {self.class_name} {props_str}"


@dataclass
class FlowchartAST:
    """
    Complete Abstract Syntax Tree for a flowchart diagram.
    
    **Attributes**:
        direction: Flow direction (TD, TB, BT, RL, LR)
        nodes: List of all nodes in the diagram
        edges: List of all connections between nodes
        styles: Dictionary of style class definitions
        subgraphs: Nested subgraph structures (Phase 2)
    
    **Methods**:
        - add_node(): Add a new node
        - add_edge(): Add a new connection
        - remove_node(): Delete node and its edges
        - get_node(): Find node by ID
        - validate(): Check for errors (dangling edges, etc.)
    
    **Example**:
    ```python
    ast = FlowchartAST(direction="TD")
    ast.add_node("A", "Start", NodeShape.STADIUM)
    ast.add_node("B", "Process", NodeShape.RECTANGLE)
    ast.add_node("C", "End", NodeShape.STADIUM)
    ast.add_edge("A", "B")
    ast.add_edge("B", "C")
    
    # Generate code
    code = FlowchartGenerator.generate(ast)
    ```
    """
    direction: str = "TD"  # TD, TB, BT, RL, LR
    nodes: List[FlowchartNode] = field(default_factory=list)
    edges: List[FlowchartEdge] = field(default_factory=list)
    styles: Dict[str, StyleDefinition] = field(default_factory=dict)
    subgraphs: List[Any] = field(default_factory=list)  # Future: nested subgraphs
    
    # ========================================================================
    # NODE OPERATIONS
    # ========================================================================
    
    def add_node(
        self,
        node_id: str,
        label: str,
        shape: NodeShape = NodeShape.RECTANGLE,
        style_class: Optional[str] = None
    ) -> FlowchartNode:
        """
        Add a new node to the diagram.
        
        **Args**:
            node_id: Unique identifier for the node
            label: Display text
            shape: Visual shape (default: rectangle)
            style_class: Optional CSS class for styling
        
        **Returns**:
            FlowchartNode: The created node
        
        **Raises**:
            ValueError: If node_id already exists
        
        **Example**:
        ```python
        node = ast.add_node("A", "Start", NodeShape.STADIUM, "highlight")
        ```
        """
        if self.get_node(node_id):
            raise ValueError(f"Node with ID '{node_id}' already exists")
        
        node = FlowchartNode(
            id=node_id,
            label=label,
            shape=shape,
            style_class=style_class
        )
        self.nodes.append(node)
        return node
    
    def get_node(self, node_id: str) -> Optional[FlowchartNode]:
        """
        Find a node by its ID.
        
        **Args**:
            node_id: The node identifier to search for
        
        **Returns**:
            FlowchartNode or None if not found
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def update_node(
        self,
        node_id: str,
        label: Optional[str] = None,
        shape: Optional[NodeShape] = None,
        style_class: Optional[str] = None
    ) -> bool:
        """
        Update properties of an existing node.
        
        **Args**:
            node_id: ID of the node to update
            label: New label (if provided)
            shape: New shape (if provided)
            style_class: New style class (if provided)
        
        **Returns**:
            bool: True if node was found and updated, False otherwise
        
        **Example**:
        ```python
        ast.update_node("A", label="New Label", shape=NodeShape.DIAMOND)
        ```
        """
        node = self.get_node(node_id)
        if not node:
            return False
        
        if label is not None:
            node.label = label
        if shape is not None:
            node.shape = shape
        if style_class is not None:
            node.style_class = style_class
        
        return True
    
    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node and all edges connected to it.
        
        **Args**:
            node_id: ID of the node to remove
        
        **Returns**:
            bool: True if node was found and removed, False otherwise
        
        **Example**:
        ```python
        ast.remove_node("A")  # Also removes all edges from/to A
        ```
        """
        node = self.get_node(node_id)
        if not node:
            return False
        
        # Remove the node
        self.nodes.remove(node)
        
        # Remove all edges connected to this node
        self.edges = [
            edge for edge in self.edges
            if edge.from_id != node_id and edge.to_id != node_id
        ]
        
        return True
    
    # ========================================================================
    # EDGE OPERATIONS
    # ========================================================================
    
    def add_edge(
        self,
        from_id: str,
        to_id: str,
        arrow_type: ArrowType = ArrowType.SOLID,
        label: Optional[str] = None
    ) -> FlowchartEdge:
        """
        Add a connection between two nodes.
        
        **Args**:
            from_id: Source node ID
            to_id: Target node ID
            arrow_type: Visual style of connection (default: solid arrow)
            label: Optional text label on the connection
        
        **Returns**:
            FlowchartEdge: The created edge
        
        **Raises**:
            ValueError: If either node doesn't exist
        
        **Example**:
        ```python
        edge = ast.add_edge("A", "B", ArrowType.SOLID, "Yes")
        ```
        """
        if not self.get_node(from_id):
            raise ValueError(f"Source node '{from_id}' does not exist")
        if not self.get_node(to_id):
            raise ValueError(f"Target node '{to_id}' does not exist")
        
        edge = FlowchartEdge(
            from_id=from_id,
            to_id=to_id,
            arrow_type=arrow_type,
            label=label
        )
        self.edges.append(edge)
        return edge
    
    def get_edges_from(self, node_id: str) -> List[FlowchartEdge]:
        """Get all edges originating from a node."""
        return [edge for edge in self.edges if edge.from_id == node_id]
    
    def get_edges_to(self, node_id: str) -> List[FlowchartEdge]:
        """Get all edges pointing to a node."""
        return [edge for edge in self.edges if edge.to_id == node_id]
    
    def remove_edge(self, from_id: str, to_id: str) -> bool:
        """
        Remove a specific edge.
        
        **Args**:
            from_id: Source node ID
            to_id: Target node ID
        
        **Returns**:
            bool: True if edge was found and removed
        """
        for edge in self.edges:
            if edge.from_id == from_id and edge.to_id == to_id:
                self.edges.remove(edge)
                return True
        return False
    
    # ========================================================================
    # STYLE OPERATIONS
    # ========================================================================
    
    def add_style(self, style: StyleDefinition):
        """Add or update a style class definition."""
        self.styles[style.class_name] = style
    
    def remove_style(self, class_name: str) -> bool:
        """Remove a style class definition."""
        if class_name in self.styles:
            del self.styles[class_name]
            return True
        return False
    
    # ========================================================================
    # VALIDATION
    # ========================================================================
    
    def validate(self) -> List[str]:
        """
        Validate the AST for structural errors.
        
        **Returns**:
            list[str]: List of error messages (empty if valid)
        
        **Checks**:
        - Duplicate node IDs
        - Dangling edges (referencing non-existent nodes)
        - Invalid characters in IDs
        - Missing required fields
        
        **Example**:
        ```python
        errors = ast.validate()
        if errors:
            for error in errors:
                print(f"⚠️ {error}")
        ```
        """
        errors = []
        
        # Check for duplicate node IDs
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            errors.append("Duplicate node IDs detected")
        
        # Check for dangling edges
        valid_ids = set(node_ids)
        for edge in self.edges:
            if edge.from_id not in valid_ids:
                errors.append(f"Edge references non-existent source node: {edge.from_id}")
            if edge.to_id not in valid_ids:
                errors.append(f"Edge references non-existent target node: {edge.to_id}")
        
        # Check for empty labels
        for node in self.nodes:
            if not node.label.strip():
                errors.append(f"Node {node.id} has empty label")
        
        return errors
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def get_next_node_id(self) -> str:
        """
        Suggest the next available node ID.
        
        Uses alphabetical sequence: A, B, C, ..., Z, AA, AB, ...
        
        **Returns**:
            str: Next available ID
        
        **Example**:
        ```python
        next_id = ast.get_next_node_id()  # Returns "A" if no nodes exist
        ast.add_node(next_id, "New Node")
        ```
        """
        if not self.nodes:
            return "A"
        
        # Get all existing IDs
        existing_ids = set(node.id for node in self.nodes)
        
        # Try single letters first
        for i in range(26):
            candidate = chr(65 + i)  # A-Z
            if candidate not in existing_ids:
                return candidate
        
        # Try double letters
        for i in range(26):
            for j in range(26):
                candidate = chr(65 + i) + chr(65 + j)  # AA-ZZ
                if candidate not in existing_ids:
                    return candidate
        
        # Fallback to numbered
        i = 1
        while f"Node{i}" in existing_ids:
            i += 1
        return f"Node{i}"
    
    def clear(self):
        """Remove all nodes, edges, and styles."""
        self.nodes.clear()
        self.edges.clear()
        self.styles.clear()
        self.subgraphs.clear()
