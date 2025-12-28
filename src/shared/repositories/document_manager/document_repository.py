"""Repository for Document model."""
from sqlalchemy.orm import Session, defer, load_only
from shared.models.document_manager.document import Document
from shared.models.document_manager.dtos import DocumentMetadataDTO
from typing import Any, List, Optional, cast
import time
import logging

logger = logging.getLogger(__name__)

class DocumentRepository:
    """
    Document Repository class definition.
    
    Attributes:
        db: Description of db.
    
    """
    def __init__(self, db: Session):
        """
          init   logic.
        
        Args:
            db: Description of db.
        
        """
        self.db = db

    def get(self, doc_id: int) -> Optional[Document]:
        """
        Retrieve logic.
        
        Args:
            doc_id: Description of doc_id.
        
        Returns:
            Result of get operation.
        """
        return self.db.query(Document).filter(Document.id == doc_id).first()

    def get_by_ids(self, doc_ids: List[int]) -> List[Document]:
        """
        Retrieve by ids logic.
        
        Args:
            doc_ids: Description of doc_ids.
        
        Returns:
            Result of get_by_ids operation.
        """
        return self.db.query(Document).filter(Document.id.in_(doc_ids)).all()

    def get_all(self) -> List[Document]:
        """
        Retrieve all logic.
        
        Returns:
            Result of get_all operation.
        """
        return self.db.query(Document).all()

    def get_all_metadata(self) -> List[DocumentMetadataDTO]:
        """Fetch all documents but only load lightweight metadata fields."""
        start = time.perf_counter()
        logger.debug("DocumentRepository: preparing metadata query")
        
        # Query specific columns to create lightweight DTOs
        # This avoids detached instance errors by not returning SQLAlchemy models
        results = self.db.query(
            Document.id,
            Document.title,
            Document.file_type,
            Document.collection,
            Document.author,
            Document.updated_at
        ).all()
        
        logger.debug("DocumentRepository: converting to DTOs ...")
        
        dtos = [
            DocumentMetadataDTO(
                id=row.id,
                title=row.title,
                file_type=row.file_type,
                collection=row.collection,
                author=row.author,
                updated_at=row.updated_at
            )
            for row in results
        ]
        
        logger.debug(
            "DocumentRepository: get_all_metadata fetched %s DTOs in %.1f ms",
            len(dtos),
            (time.perf_counter() - start) * 1000,
        )
        return dtos

    def search(self, query: str) -> List[Document]:
        # Basic SQL LIKE search. For advanced search, we'd use Whoosh or Full Text Search.
        """
        Search logic.
        
        Args:
            query: Description of query.
        
        Returns:
            Result of search operation.
        """
        return self.db.query(Document).filter(
            (Document.title.ilike(f"%{query}%")) | 
            (Document.content.ilike(f"%{query}%"))
        ).all()

    def get_by_collection_name(self, collection_query: str) -> List[Document]:
        """Find documents where the collection name contains the query string (case-insensitive)."""
        return self.db.query(Document).filter(
            Document.collection.ilike(f"%{collection_query}%")
        ).all()

    def create(
        self,
        title: str,
        content: str,
        file_type: str,
        file_path: Optional[str] = None,
        raw_content: Optional[str] = None,
        author: Optional[str] = None,
        collection: Optional[str] = None,
    ) -> Document:
        """
        Create logic.
        
        Args:
            title: Description of title.
            content: Description of content.
            file_type: Description of file_type.
            file_path: Description of file_path.
            raw_content: Description of raw_content.
            author: Description of author.
            collection: Description of collection.
        
        Returns:
            Result of create operation.
        """
        db_doc = Document(
            title=title,
            content=content,
            file_type=file_type,
            file_path=file_path,
            raw_content=raw_content,
            author=author,
            collection=collection
        )
        self.db.add(db_doc)
        self.db.commit()
        self.db.refresh(db_doc)
        return db_doc

    def update(self, doc_id: int, **kwargs) -> Optional[Document]:
        """
        Update logic.
        
        Args:
            doc_id: Description of doc_id.
        
        Returns:
            Result of update operation.
        """
        doc = self.get(doc_id)
        if doc:
            for key, value in kwargs.items():
                setattr(doc, key, value)
            self.db.commit()
            self.db.refresh(doc)
        return doc

    def delete(self, doc_id: int) -> bool:
        """
        Remove logic.
        
        Args:
            doc_id: Description of doc_id.
        
        Returns:
            Result of delete operation.
        """
        doc = self.get(doc_id)
        if doc:
            self.db.delete(doc)
            self.db.commit()
            return True
        return False

    def delete_all(self) -> int:
        """Delete all documents from the database."""
        count = self.db.query(Document).delete()
        self.db.commit()
        return count