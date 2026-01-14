"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: Contract (Document schemas) - GRANDFATHERED, may be infrastructure
- USED BY: Document_manager, Gematria (7 references)
- CRITERION: 4 (Shared data contract) OR 2 (if docs are global infrastructure)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""
Notebook Models - The Mindscape Structure.
SQLAlchemy models for Notebooks and Sections, providing hierarchical document organization.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from shared.database import Base
from datetime import datetime

class Notebook(Base):
    """
    Top-level container (e.g., 'Work', 'Personal').
    Analogous to a OneNote Notebook.
    """
    __tablename__ = "notebooks"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    sections = relationship("Section", back_populates="notebook", cascade="all, delete-orphan", order_by="Section.id")

class Section(Base):
    """
    Mid-level container (e.g., 'Project Alpha', 'Meeting Notes').
    Analogous to a OneNote Section / Tab.
    """
    __tablename__ = "sections"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    color = Column(String, default="#CCCCCC") # For tab color
    
    notebook_id = Column(Integer, ForeignKey("notebooks.id"), nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    notebook = relationship("Notebook", back_populates="sections")
    # Pages are Documents
    pages = relationship("Document", backref="section", order_by="Document.id") 
    # Note: 'backref' on 'pages' adds 'section' attribute to Document