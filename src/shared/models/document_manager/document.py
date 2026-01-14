"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: Contract (Document schemas) - GRANDFATHERED, may be infrastructure
- USED BY: Document_manager, Gematria, Tq_lexicon (59 references)
- CRITERION: 4 (Shared data contract) OR 2 (if docs are global infrastructure)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""Document database model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from shared.database import Base


class DocumentImage(Base):
    """Separate storage for document images to avoid bloating raw_content."""

    __tablename__ = "document_images"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    hash = Column(String(64), index=True)  # SHA256 for deduplication
    data = Column(LargeBinary)  # Compressed image binary
    mime_type = Column(String(50))  # image/png, image/jpeg, etc.
    original_filename = Column(String, nullable=True)  # Original filename if available
    width = Column(Integer, nullable=True)  # Image dimensions for layout
    height = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to document
    document = relationship("Document", back_populates="images")

    def __repr__(self):
        return f"<DocumentImage(id={self.id}, doc={self.document_id}, mime={self.mime_type})>"

class DocumentLink(Base):
    """Association table for linking documents (Zettelkasten/Wiki-links)."""
    __tablename__ = "document_links"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("documents.id"), index=True)
    target_id = Column(Integer, ForeignKey("documents.id"), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    """
    Document class definition.
    
    """
    __tablename__ = "documents"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    file_path = Column(String, unique=True, nullable=True)
    file_type = Column(String)  # 'txt', 'html', 'pdf', 'docx', 'rtf'
    content = Column(Text)  # Extracted text content for search
    raw_content = Column(Text, nullable=True) # HTML/RTF raw content if needed
    
    # Metadata
    author = Column(String, nullable=True)
    collection = Column(String, nullable=True) # Virtual folder/collection name
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # OneNote integration
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=True, index=True)

    # Relationships
    # This allows accessing linked documents via doc.outgoing_links
    outgoing_links = relationship(
        "Document",
        secondary="document_links",
        primaryjoin="Document.id==DocumentLink.source_id",
        secondaryjoin="Document.id==DocumentLink.target_id",
        backref="incoming_links",
        viewonly=True # We'll manage the links manually to avoid complexity for now
    )
    
    # Images stored separately
    images = relationship("DocumentImage", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"