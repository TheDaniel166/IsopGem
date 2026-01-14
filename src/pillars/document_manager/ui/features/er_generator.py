

"""
SQLAlchemy to Mermaid ER Diagram Generator.
Introspects SQLAlchemy models and generates Mermaid erDiagram code.
"""

import inspect
from typing import Any


class ERDiagramGenerator:
    """
    Generates Mermaid ER diagrams from SQLAlchemy models or database metadata.
    """
    
    @classmethod
    def from_sqlalchemy_models(cls, models: list[type]) -> str:
        """
        Generate Mermaid erDiagram code from a list of SQLAlchemy model classes.
        
        Args:
            models: List of SQLAlchemy model classes (declarative base subclasses)
        
        Returns:
            Mermaid erDiagram code as a string
        """
        lines = ["erDiagram"]
        entities = {}
        relationships = []
        
        for model in models:
            table_name = cls._get_table_name(model)
            columns = cls._get_columns(model)
            entities[table_name] = columns
            
            # Extract relationships
            rels = cls._get_relationships(model, models)
            relationships.extend(rels)
        
        # Generate entity definitions
        for table_name, columns in entities.items():
            lines.append(f"    {table_name} {{")
            for col_type, col_name, constraints in columns:
                constraint_str = " ".join(constraints) if constraints else ""
                lines.append(f"        {col_type} {col_name} {constraint_str}".rstrip())
            lines.append("    }")
        
        # Generate relationships
        for rel in relationships:
            lines.append(f"    {rel}")
        
        return "\n".join(lines)
    
    @classmethod
    def _get_table_name(cls, model: type) -> str:
        """Get the table name from a SQLAlchemy model."""
        if hasattr(model, '__tablename__'):
            return model.__tablename__.upper()
        return model.__name__.upper()
    
    @classmethod
    def _get_columns(cls, model: type) -> list[tuple[str, str, list[str]]]:
        """
        Extract columns from a SQLAlchemy model.
        Returns list of (type, name, [constraints]) tuples.
        """
        columns = []
        
        # Try to get __table__ for mapped columns
        if hasattr(model, '__table__'):
            for col in model.__table__.columns:
                col_type = cls._sqlalchemy_type_to_string(col.type)
                col_name = col.name
                constraints = []
                
                if col.primary_key:
                    constraints.append("PK")
                if col.unique:
                    constraints.append("UK")
                if col.foreign_keys:
                    constraints.append("FK")
                
                columns.append((col_type, col_name, constraints))
        
        return columns
    
    @classmethod
    def _sqlalchemy_type_to_string(cls, sa_type: Any) -> str:
        """Convert SQLAlchemy type to a simple string representation."""
        type_name = type(sa_type).__name__.lower()
        
        type_mapping = {
            'integer': 'int',
            'biginteger': 'bigint',
            'smallinteger': 'smallint',
            'string': 'string',
            'text': 'text',
            'boolean': 'bool',
            'datetime': 'datetime',
            'date': 'date',
            'time': 'time',
            'float': 'float',
            'numeric': 'decimal',
            'uuid': 'uuid',
            'json': 'json',
            'enum': 'enum',
        }
        
        return type_mapping.get(type_name, 'string')
    
    @classmethod
    def _get_relationships(cls, model: type, all_models: list[type]) -> list[str]:
        """
        Extract relationships from a SQLAlchemy model.
        Returns list of Mermaid relationship strings.
        """
        relationships = []
        model_table = cls._get_table_name(model)
        
        # Check foreign keys
        if hasattr(model, '__table__'):
            for col in model.__table__.columns:
                for fk in col.foreign_keys:
                    # Parse the foreign key target
                    target_table = fk.column.table.name.upper()
                    # Default to many-to-one (most common)
                    rel = f"{model_table} }}o--|| {target_table} : references"
                    if rel not in relationships:
                        relationships.append(rel)
        
        return relationships
    
    @classmethod
    def generate_example(cls) -> str:
        """
        Generate an example ER diagram showing the syntax.
        Useful when no SQLAlchemy models are available.
        """
        return """erDiagram
    %% Example ER Diagram (no SQLAlchemy models detected)
    %% To use the ER Generator, provide SQLAlchemy model classes
    
    USER {
        int id PK
        string email UK
        string name
        datetime created_at
    }
    
    PROJECT {
        int id PK
        int owner_id FK
        string name
        text description
        datetime created_at
    }
    
    TASK {
        int id PK
        int project_id FK
        int assignee_id FK
        string title
        text description
        enum status
        datetime due_date
    }
    
    USER ||--o{ PROJECT : owns
    USER ||--o{ TASK : assigned
    PROJECT ||--|{ TASK : contains"""