"""Document database model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from shared.database import Base

class DocumentLink(Base):
    """Association table for linking documents (Zettelkasten/Wiki-links)."""
    __tablename__ = "document_links"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("documents.id"), index=True)
    target_id = Column(Integer, ForeignKey("documents.id"), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    file_path = Column(String, unique=True, nullable=True)
    file_type = Column(String)  # 'txt', 'html', 'pdf', 'docx', 'rtf'
    content = Column(Text)  # Extracted text content for search
    raw_content = Column(Text, nullable=True) # HTML/RTF raw content if needed
    
    # Metadata
    tags = Column(String, nullable=True) # Comma-separated tags
    author = Column(String, nullable=True)
    collection = Column(String, nullable=True) # Virtual folder/collection name
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

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
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"
