"""Whoosh-based repository for searching documents."""
import os
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME, KEYWORD
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.query import Term
from whoosh.analysis import StemmingAnalyzer

from pillars.document_manager.models.document import Document

class DocumentSearchRepository:
    """Repository for managing document search index using Whoosh."""
    
    def __init__(self, index_dir: Optional[str] = None):
        """
        Initialize the search repository.
        
        Args:
            index_dir: Directory for the Whoosh index. Defaults to ~/.isopgem/documents
        """
        if index_dir is None:
            # Default to user's home directory
            home = Path.home()
            index_dir = str(home / '.isopgem' / 'documents')
        
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Define schema with StemmingAnalyzer for better matching
        # e.g. "running" matches "run"
        analyzer = StemmingAnalyzer()
        
        self.schema = Schema(
            id=ID(stored=True, unique=True),
            title=TEXT(stored=True, field_boost=2.0, analyzer=analyzer),
            content=TEXT(stored=True, analyzer=analyzer),
            file_type=KEYWORD(stored=True),
            author=TEXT(stored=True),
            collection=KEYWORD(stored=True),
            created_at=DATETIME(stored=True),
            updated_at=DATETIME(stored=True)
        )
        
        # Create or open index
        # Note: If schema changes, we might need to rebuild. 
        # For now, we'll just open. If it fails or is outdated, rebuild_index should be called.
        if index.exists_in(str(self.index_dir)):
            try:
                self.ix = index.open_dir(str(self.index_dir))
                # Check for schema mismatch
                current_fields = set(self.ix.schema.names())
                target_fields = set(self.schema.names())
                if current_fields != target_fields:
                    print(f"Schema mismatch detected. Recreating index. Old: {current_fields}, New: {target_fields}")
                    self.ix = index.create_in(str(self.index_dir), self.schema)
            except Exception:
                # Schema mismatch or corruption, recreate
                self.ix = index.create_in(str(self.index_dir), self.schema)
        else:
            self.ix = index.create_in(str(self.index_dir), self.schema)
            
    def index_document(self, doc: Document):
        """
        Add or update a document in the search index.
        
        Args:
            doc: The document model to index
        """
        writer = self.ix.writer()
        try:
            writer.update_document(
                id=str(doc.id),
                title=doc.title,
                content=doc.content,
                file_type=doc.file_type,
                author=doc.author or "",
                collection=doc.collection or "",
                created_at=doc.created_at,
                updated_at=doc.updated_at or datetime.now()
            )
            writer.commit()
        except Exception as e:
            writer.cancel()
            raise e

    def index_documents(self, docs: List[Document]):
        """
        Add or update multiple documents in the search index efficiently.
        
        Args:
            docs: List of document models to index
        """
        writer = self.ix.writer()
        try:
            for doc in docs:
                writer.update_document(
                    id=str(doc.id),
                    title=doc.title,
                    content=doc.content,
                    file_type=doc.file_type,
                    author=doc.author or "",
                    collection=doc.collection or "",
                    created_at=doc.created_at,
                    updated_at=doc.updated_at or datetime.now()
                )
            writer.commit()
        except Exception as e:
            writer.cancel()
            raise e

    def delete_document(self, doc_id: int):
        """
        Remove a document from the search index.
        
        Args:
            doc_id: The ID of the document to remove
        """
        writer = self.ix.writer()
        try:
            writer.delete_by_term('id', str(doc_id))
            writer.commit()
        except Exception as e:
            writer.cancel()
            raise e

    def search(self, query_str: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Search for documents.
        
        Args:
            query_str: The search query
            limit: Maximum number of results. None for unlimited.
            
        Returns:
            List of dictionaries containing document info (id, title, etc.)
        """
        with self.ix.searcher() as searcher:
            parser = MultifieldParser(["title", "content", "author"], schema=self.schema)
            query = parser.parse(query_str)
            
            results = searcher.search(query, limit=limit)
            results.fragmenter.maxchars = 300
            results.fragmenter.surround = 50
            
            # Return list of dicts, service will map back to DB objects if needed
            # or UI can use these directly for display
            return [
                {
                    'id': int(r['id']),
                    'title': r['title'],
                    'file_type': r['file_type'],
                    'collection': r.get('collection') or '',
                    'created_at': r['created_at'],
                    'highlights': r.highlights("content") or r.highlights("title") or ""
                }
                for r in results
            ]

    def rebuild_index(self, documents: List[Document]):
        """
        Rebuild the entire index from a list of documents.
        Useful for initialization or recovery.
        """
        # Close current index and recreate it to clear everything
        try:
            # Create fresh index (overwrites old one)
            self.ix = index.create_in(str(self.index_dir), self.schema)
            
            # Now add all documents
            writer = self.ix.writer()
            try:
                for doc in documents:
                    writer.add_document(
                        id=str(doc.id),
                        title=doc.title,
                        content=doc.content,
                        file_type=doc.file_type,
                        author=doc.author or "",
                        collection=doc.collection or "",
                        created_at=doc.created_at,
                        updated_at=doc.updated_at or datetime.now()
                    )
                writer.commit()
            except Exception as e:
                writer.cancel()
                raise e
        except Exception as e:
            raise Exception(f"Failed to rebuild search index: {str(e)}")

    def clear_index(self):
        """Clear the entire search index."""
        # Re-create index to clear it
        self.ix = index.create_in(str(self.index_dir), self.schema)
