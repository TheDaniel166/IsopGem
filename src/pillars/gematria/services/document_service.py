"""Service for document operations - isolates UI from database layer."""
from typing import Optional
from sqlalchemy.orm import Session
from shared.repositories.document_manager.document_repository import DocumentRepository
from shared.database import get_db


class DocumentService:
    """Service for loading document content without exposing database layer to UI."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize document service with database session."""
        self.db = db_session if db_session else next(get_db())
        self.repo = DocumentRepository(self.db)
    
    def get_document_content(self, doc_id: int) -> Optional[str]:
        """
        Retrieve document content by ID.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Document content as string, or None if not found or empty
        """
        doc = self.repo.get(doc_id)
        if doc and doc.content:
            return doc.content
        return None
