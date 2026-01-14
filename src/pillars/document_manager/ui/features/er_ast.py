"""
Entity-Relationship Diagram Abstract Syntax Tree (AST).

**Purpose**:
Represent Mermaid ER diagrams as structured data for visual editing.
Enables bidirectional conversion: Code ↔ AST ↔ Visual Editor.

**Supported Syntax**:
- Entities with attributes
- Attribute types and constraints (PK, FK, UK)
- Relationships with cardinality
- Identifying and non-identifying relationships

**Usage Example**:
```python
# Create AST programmatically
ast = ERDiagramAST()
ast.add_entity("CUSTOMER", [
    Attribute("id", "int", ["PK"]),
    Attribute("name", "string", []),
    Attribute("email", "string", ["UK"])
])
ast.add_relationship("CUSTOMER", "ORDER", Cardinality.ONE_TO_MANY, "places")

# Generate code
from er_generator_new import ERDiagramGenerator
code = ERDiagramGenerator.generate(ast)
```

**Thread Safety**: Not thread-safe. Use from Qt main thread only.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class AttributeType(Enum):
    """Available attribute types for ER diagrams."""
    INT = "int"
    BIGINT = "bigint"
    SMALLINT = "smallint"
    STRING = "string"
    TEXT = "text"
    VARCHAR = "varchar"
    BOOL = "bool"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    TIME = "time"
    TIMESTAMP = "timestamp"
    FLOAT = "float"
    DOUBLE = "double"
    DECIMAL = "decimal"
    NUMERIC = "numeric"
    UUID = "uuid"
    JSON = "json"
    JSONB = "jsonb"
    ENUM = "enum"
    BLOB = "blob"
    BINARY = "binary"


class Cardinality(Enum):
    """Relationship cardinality types."""
    # Syntax: Left ||--Right
    ZERO_OR_ONE_TO_EXACTLY_ONE = "|o--||"      # Zero or one to exactly one
    ZERO_OR_ONE_TO_ZERO_OR_ONE = "|o--o|"      # Zero or one to zero or one
    ZERO_OR_ONE_TO_ZERO_OR_MORE = "|o--o{"     # Zero or one to zero or more
    ZERO_OR_ONE_TO_ONE_OR_MORE = "|o--|{"      # Zero or one to one or more
    
    EXACTLY_ONE_TO_ZERO_OR_ONE = "||--o|"      # Exactly one to zero or one
    EXACTLY_ONE_TO_EXACTLY_ONE = "||--||"      # Exactly one to exactly one (one-to-one)
    EXACTLY_ONE_TO_ZERO_OR_MORE = "||--o{"     # Exactly one to zero or more (one-to-many)
    EXACTLY_ONE_TO_ONE_OR_MORE = "||--|{"      # Exactly one to one or more
    
    ZERO_OR_MORE_TO_ZERO_OR_ONE = "}o--o|"     # Zero or more to zero or one
    ZERO_OR_MORE_TO_EXACTLY_ONE = "}o--||"     # Zero or more to exactly one (many-to-one)
    ZERO_OR_MORE_TO_ZERO_OR_MORE = "}o--o{"    # Zero or more to zero or more (many-to-many)
    ZERO_OR_MORE_TO_ONE_OR_MORE = "}o--|{"     # Zero or more to one or more
    
    ONE_OR_MORE_TO_ZERO_OR_ONE = "}|--o|"      # One or more to zero or one
    ONE_OR_MORE_TO_EXACTLY_ONE = "}|--||"      # One or more to exactly one
    ONE_OR_MORE_TO_ZERO_OR_MORE = "}|--o{"     # One or more to zero or more
    ONE_OR_MORE_TO_ONE_OR_MORE = "}|--|{"      # One or more to one or more
    
    @property
    def display_name(self) -> str:
        """Human-readable name for the cardinality."""
        mapping = {
            Cardinality.EXACTLY_ONE_TO_EXACTLY_ONE: "One-to-One (1:1)",
            Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE: "One-to-Many (1:N)",
            Cardinality.ZERO_OR_MORE_TO_EXACTLY_ONE: "Many-to-One (N:1)",
            Cardinality.ZERO_OR_MORE_TO_ZERO_OR_MORE: "Many-to-Many (N:M)",
            Cardinality.ZERO_OR_ONE_TO_EXACTLY_ONE: "Optional-to-Required (0..1:1)",
            Cardinality.EXACTLY_ONE_TO_ZERO_OR_ONE: "Required-to-Optional (1:0..1)",
        }
        return mapping.get(self, self.value)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Attribute:
    """
    A single attribute (column) in an entity.
    
    **Attributes**:
        name: Column name (e.g., "user_id", "email")
        type: Data type (int, string, etc.)
        constraints: List of constraints (PK, FK, UK, etc.)
        comment: Optional comment for documentation
        metadata: Optional arbitrary data
    
    **Example**:
    ```python
    attr = Attribute(
        name="user_id",
        type="int",
        constraints=["PK"],
        comment="Primary identifier"
    )
    ```
    """
    name: str
    type: str  # Can be AttributeType enum or custom string
    constraints: List[str] = field(default_factory=list)
    comment: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_mermaid_syntax(self) -> str:
        """
        Generate Mermaid syntax for this attribute.
        
        Returns:
            str: Attribute line (e.g., "int user_id PK")
        """
        parts = [self.type, self.name]
        if self.constraints:
            parts.extend(self.constraints)
        
        line = " ".join(parts)
        
        if self.comment:
            line += f" \"{self.comment}\""
        
        return line


@dataclass
class Entity:
    """
    An entity (table) in the ER diagram.
    
    **Attributes**:
        name: Entity name (e.g., "USER", "PRODUCT")
        attributes: List of attributes (columns)
        comment: Optional comment
        metadata: Optional arbitrary data
    
    **Example**:
    ```python
    entity = Entity(
        name="USER",
        attributes=[
            Attribute("id", "int", ["PK"]),
            Attribute("email", "string", ["UK"]),
            Attribute("name", "string", [])
        ]
    )
    ```
    """
    name: str
    attributes: List[Attribute] = field(default_factory=list)
    comment: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_mermaid_syntax(self) -> str:
        """
        Generate Mermaid syntax for this entity.
        
        Returns:
            str: Entity definition block
        """
        lines = [f"{self.name} {{"]
        
        for attr in self.attributes:
            lines.append(f"    {attr.to_mermaid_syntax()}")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def add_attribute(self, name: str, type_: str, constraints: List[str] = None) -> Attribute:
        """Add an attribute to this entity."""
        attr = Attribute(name=name, type=type_, constraints=constraints or [])
        self.attributes.append(attr)
        return attr
    
    def get_attribute(self, name: str) -> Optional[Attribute]:
        """Find an attribute by name."""
        for attr in self.attributes:
            if attr.name == name:
                return attr
        return None
    
    def remove_attribute(self, name: str) -> bool:
        """Remove an attribute by name."""
        for i, attr in enumerate(self.attributes):
            if attr.name == name:
                self.attributes.pop(i)
                return True
        return False


@dataclass
class Relationship:
    """
    A relationship between two entities.
    
    **Attributes**:
        from_entity: Source entity name
        to_entity: Target entity name
        cardinality: Relationship cardinality
        label: Optional descriptive label
        metadata: Optional arbitrary data
    
    **Example**:
    ```python
    rel = Relationship(
        from_entity="USER",
        to_entity="ORDER",
        cardinality=Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE,
        label="places"
    )
    ```
    """
    from_entity: str
    to_entity: str
    cardinality: Cardinality
    label: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_mermaid_syntax(self) -> str:
        """
        Generate Mermaid syntax for this relationship.
        
        Returns:
            str: Relationship line (e.g., "USER ||--o{ ORDER : places")
        """
        line = f"{self.from_entity} {self.cardinality.value} {self.to_entity}"
        
        if self.label:
            line += f" : {self.label}"
        
        return line


# ============================================================================
# ER DIAGRAM AST
# ============================================================================

@dataclass
class ERDiagramAST:
    """
    Complete Abstract Syntax Tree for an ER diagram.
    
    **Attributes**:
        entities: Dictionary of entities (name → Entity)
        relationships: List of relationships
        title: Optional diagram title
        metadata: Optional arbitrary data
    
    **Methods**:
        - add_entity(): Add a new entity
        - add_relationship(): Add a new relationship
        - remove_entity(): Delete entity and its relationships
        - get_entity(): Find entity by name
        - validate(): Check for errors
    
    **Example**:
    ```python
    ast = ERDiagramAST()
    
    # Add entities
    user = ast.add_entity("USER")
    user.add_attribute("id", "int", ["PK"])
    user.add_attribute("email", "string", ["UK"])
    
    order = ast.add_entity("ORDER")
    order.add_attribute("id", "int", ["PK"])
    order.add_attribute("user_id", "int", ["FK"])
    
    # Add relationship
    ast.add_relationship("USER", "ORDER", Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE, "places")
    
    # Generate code
    from er_generator_new import ERDiagramGenerator
    code = ERDiagramGenerator.generate(ast)
    ```
    """
    entities: Dict[str, Entity] = field(default_factory=dict)
    relationships: List[Relationship] = field(default_factory=list)
    title: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # ========================================================================
    # ENTITY OPERATIONS
    # ========================================================================
    
    def add_entity(self, name: str, attributes: List[Attribute] = None) -> Entity:
        """
        Add a new entity to the diagram.
        
        **Args**:
            name: Entity name (will be uppercased)
            attributes: Optional list of initial attributes
        
        **Returns**:
            Entity: The created entity
        
        **Raises**:
            ValueError: If entity name already exists
        
        **Example**:
        ```python
        user = ast.add_entity("USER", [
            Attribute("id", "int", ["PK"]),
            Attribute("name", "string", [])
        ])
        ```
        """
        name = name.upper()
        
        if name in self.entities:
            raise ValueError(f"Entity '{name}' already exists")
        
        entity = Entity(name=name, attributes=attributes or [])
        self.entities[name] = entity
        return entity
    
    def get_entity(self, name: str) -> Optional[Entity]:
        """
        Find an entity by name.
        
        **Args**:
            name: Entity name (case-insensitive)
        
        **Returns**:
            Entity or None if not found
        """
        return self.entities.get(name.upper())
    
    def remove_entity(self, name: str) -> bool:
        """
        Remove an entity and all relationships involving it.
        
        **Args**:
            name: Entity name to remove
        
        **Returns**:
            bool: True if entity was found and removed
        """
        name = name.upper()
        
        if name not in self.entities:
            return False
        
        # Remove the entity
        del self.entities[name]
        
        # Remove all relationships involving this entity
        self.relationships = [
            rel for rel in self.relationships
            if rel.from_entity != name and rel.to_entity != name
        ]
        
        return True
    
    def update_entity(self, old_name: str, new_name: Optional[str] = None) -> bool:
        """
        Update an entity's name.
        
        **Args**:
            old_name: Current entity name
            new_name: New entity name (if provided)
        
        **Returns**:
            bool: True if updated successfully
        """
        old_name = old_name.upper()
        
        if old_name not in self.entities:
            return False
        
        if new_name:
            new_name = new_name.upper()
            if new_name != old_name and new_name in self.entities:
                raise ValueError(f"Entity '{new_name}' already exists")
            
            entity = self.entities[old_name]
            entity.name = new_name
            
            # Update dictionary
            del self.entities[old_name]
            self.entities[new_name] = entity
            
            # Update relationships
            for rel in self.relationships:
                if rel.from_entity == old_name:
                    rel.from_entity = new_name
                if rel.to_entity == old_name:
                    rel.to_entity = new_name
        
        return True
    
    # ========================================================================
    # RELATIONSHIP OPERATIONS
    # ========================================================================
    
    def add_relationship(
        self,
        from_entity: str,
        to_entity: str,
        cardinality: Cardinality,
        label: Optional[str] = None
    ) -> Relationship:
        """
        Add a relationship between two entities.
        
        **Args**:
            from_entity: Source entity name
            to_entity: Target entity name
            cardinality: Relationship cardinality
            label: Optional descriptive label
        
        **Returns**:
            Relationship: The created relationship
        
        **Raises**:
            ValueError: If either entity doesn't exist
        
        **Example**:
        ```python
        rel = ast.add_relationship(
            "USER", "ORDER",
            Cardinality.EXACTLY_ONE_TO_ZERO_OR_MORE,
            "places"
        )
        ```
        """
        from_entity = from_entity.upper()
        to_entity = to_entity.upper()
        
        if from_entity not in self.entities:
            raise ValueError(f"Entity '{from_entity}' does not exist")
        if to_entity not in self.entities:
            raise ValueError(f"Entity '{to_entity}' does not exist")
        
        rel = Relationship(
            from_entity=from_entity,
            to_entity=to_entity,
            cardinality=cardinality,
            label=label
        )
        self.relationships.append(rel)
        return rel
    
    def get_relationships_for(self, entity_name: str) -> List[Relationship]:
        """Get all relationships involving an entity."""
        entity_name = entity_name.upper()
        return [
            rel for rel in self.relationships
            if rel.from_entity == entity_name or rel.to_entity == entity_name
        ]
    
    def remove_relationship(self, from_entity: str, to_entity: str) -> bool:
        """
        Remove a specific relationship.
        
        **Args**:
            from_entity: Source entity name
            to_entity: Target entity name
        
        **Returns**:
            bool: True if relationship was found and removed
        """
        from_entity = from_entity.upper()
        to_entity = to_entity.upper()
        
        for i, rel in enumerate(self.relationships):
            if rel.from_entity == from_entity and rel.to_entity == to_entity:
                self.relationships.pop(i)
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
        - Entities have at least one attribute
        - Relationships reference existing entities
        - No duplicate entity names
        - Attribute names are valid
        
        **Example**:
        ```python
        errors = ast.validate()
        if errors:
            for error in errors:
                print(f"⚠️ {error}")
        ```
        """
        errors = []
        
        # Check for empty entities
        for name, entity in self.entities.items():
            if not entity.attributes:
                errors.append(f"Entity '{name}' has no attributes")
        
        # Check relationships reference valid entities
        for rel in self.relationships:
            if rel.from_entity not in self.entities:
                errors.append(f"Relationship references non-existent entity: {rel.from_entity}")
            if rel.to_entity not in self.entities:
                errors.append(f"Relationship references non-existent entity: {rel.to_entity}")
        
        # Check for invalid attribute names
        for name, entity in self.entities.items():
            for attr in entity.attributes:
                if not attr.name.strip():
                    errors.append(f"Entity '{name}' has attribute with empty name")
        
        return errors
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def clear(self):
        """Remove all entities and relationships."""
        self.entities.clear()
        self.relationships.clear()
        self.title = None
    
    def get_entity_count(self) -> int:
        """Get total number of entities."""
        return len(self.entities)
    
    def get_relationship_count(self) -> int:
        """Get total number of relationships."""
        return len(self.relationships)
