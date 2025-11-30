"""Service layer for Document Manager."""
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Optional
import re
from pillars.document_manager.repositories.document_repository import DocumentRepository
from pillars.document_manager.repositories.search_repository import DocumentSearchRepository
from pillars.document_manager.utils.parsers import DocumentParser
from pillars.document_manager.models.document import Document

class DocumentService:
    def __init__(self, db: Session):
        self.repo = DocumentRepository(db)
        self.search_repo = DocumentSearchRepository()

    def _update_links(self, doc: Document):
        """Parse content for [[WikiLinks]] and update relationships."""
        # Check for None explicitly to avoid Pylance errors with SQLAlchemy columns
        if doc.content is None:
            return
            
        content_str = str(doc.content)
        if not content_str:
            return

        # Find all [[Title]] patterns
        links = re.findall(r"\[\[(.*?)\]\]", content_str)
        
        # Always update, even if empty (to clear links if they were removed)
        unique_titles = list(set(links))
        
        if not unique_titles:
            doc.outgoing_links = []
        else:
            # Find target documents
            # We access the DB session directly from the repo for this query
            targets = self.repo.db.query(Document).filter(Document.title.in_(unique_titles)).all()
            doc.outgoing_links = targets
            
        self.repo.db.commit()

    def import_document(self, file_path: str, tags: Optional[str] = None, collection: Optional[str] = None) -> Document:
        """
        Import a document from a file path.
        Parses content and saves to database.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Parse file
        content, raw_content, file_type = DocumentParser.parse_file(str(path))

        # Create document record
        doc = self.repo.create(
            title=path.stem,
            content=content,
            file_type=file_type,
            file_path=str(path),
            raw_content=raw_content,
            tags=tags or "",
            collection=collection or ""
        )
        
        # Update links
        self._update_links(doc)
        
        # Index document
        self.search_repo.index_document(doc)
        
        return doc

    def search_documents(self, query: str, limit: Optional[int] = None):
        # Search using Whoosh
        results = self.search_repo.search(query, limit=limit)
        ids = [r['id'] for r in results]
        
        if not ids:
            return []
            
        # Fetch full objects from DB
        docs = self.repo.get_by_ids(ids)
        
        # Re-order to match search result relevance
        doc_map = {d.id: d for d in docs}
        ordered_docs = []
        for doc_id in ids:
            if doc_id in doc_map:
                ordered_docs.append(doc_map[doc_id])
                
        return ordered_docs

    def search_documents_with_highlights(self, query: str, limit: Optional[int] = None):
        """Search documents and return results with highlights."""
        return self.search_repo.search(query, limit=limit)

    def get_all_documents(self):
        return self.repo.get_all()
    
    def get_all_documents_metadata(self):
        """Get all documents without loading heavy content fields."""
        return self.repo.get_all_metadata()
    
    def get_document(self, doc_id: int):
        return self.repo.get(doc_id)
    
    def update_document(self, doc_id: int, **kwargs):
        """
        Update document fields.
        Args:
            doc_id: Document ID
            **kwargs: Fields to update (content, raw_content, title, tags, author, collection)
        """
        doc = self.repo.update(doc_id, **kwargs)
        if doc:
            # If content was updated, re-parse links
            if 'content' in kwargs:
                self._update_links(doc)
            self.search_repo.index_document(doc)
        return doc

    def update_documents(self, doc_ids: list[int], **kwargs):
        """
        Update multiple documents efficiently.
        Args:
            doc_ids: List of Document IDs
            **kwargs: Fields to update
        """
        updated_docs = []
        for doc_id in doc_ids:
            doc = self.repo.update(doc_id, **kwargs)
            if doc:
                # If content was updated (unlikely in batch, but possible), re-parse links
                if 'content' in kwargs:
                    self._update_links(doc)
                updated_docs.append(doc)
        
        if updated_docs:
            self.search_repo.index_documents(updated_docs)
        
        return updated_docs

    def delete_document(self, doc_id: int):
        success = self.repo.delete(doc_id)
        if success:
            self.search_repo.delete_document(doc_id)
        return success
    
    def delete_all_documents(self):
        """Delete all documents from database and search index."""
        count = self.repo.delete_all()
        self.search_repo.clear_index()
        return count

    def rebuild_search_index(self):
        """Rebuild the search index from the database."""
        docs = self.repo.get_all()
        self.search_repo.rebuild_index(docs)
