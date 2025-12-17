"""Service layer for Document Manager."""
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Optional, List, Tuple
from contextlib import contextmanager
import time
import logging
import re
from shared.database import get_db_session
from pillars.document_manager.repositories.document_repository import DocumentRepository
from pillars.document_manager.repositories.document_verse_repository import DocumentVerseRepository
from pillars.document_manager.repositories.search_repository import DocumentSearchRepository
from pillars.document_manager.repositories.image_repository import ImageRepository
from pillars.document_manager.utils.parsers import DocumentParser
from pillars.document_manager.utils.image_utils import (
    extract_images_from_html, 
    restore_images_in_html,
    has_embedded_images
)
from pillars.document_manager.models.document import Document

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DocumentRepository(db)
        self.verse_repo = DocumentVerseRepository(db)
        self.image_repo = ImageRepository(db)
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

    def import_document(self, file_path: str, collection: Optional[str] = None) -> Document:
        """
        Import a document from a file path.
        Parses content and saves to database.
        """
        start = time.perf_counter()
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check for existing document to prevent unique constraint errors
        existing_doc = self.repo.db.query(Document).filter(Document.file_path == str(path)).first()
        if existing_doc:
            logger.info("DocumentService: Skipping import, file already exists: %s", path)
            return existing_doc

        # Parse file
        content, raw_content, file_type, metadata = DocumentParser.parse_file(str(path))
        
        # Determine title
        title = path.stem
        # Use metadata title if available
        doc_title = metadata.get('title')
        if not doc_title or not doc_title.strip():
            doc_title = path.stem

        # Create document record first (without images extracted yet)
        doc = self.repo.create(
            title=doc_title,
            content=content,
            file_type=file_type,
            file_path=str(path),
            raw_content=raw_content,  # Will be updated after image extraction
            author=metadata.get('author') or "",
            collection=collection or ""
        )
        
        # Extract and store images separately if raw_content has embedded images
        if raw_content and has_embedded_images(raw_content):
            def store_image(image_bytes: bytes, mime_type: str) -> int:
                img = self.image_repo.create(
                    document_id=doc.id,
                    data=image_bytes,
                    mime_type=mime_type
                )
                return img.id
            
            # Extract images and update raw_content with docimg:// references
            modified_html, images_info = extract_images_from_html(raw_content, store_image)
            
            if images_info:
                # Update the document with the lighter raw_content
                doc.raw_content = modified_html
                self.db.commit()
                logger.debug(
                    "DocumentService: extracted %d images from '%s'",
                    len(images_info), path.name
                )
        
        # Update links
        self._update_links(doc)
        
        # Index document
        self.search_repo.index_document(doc)
        
        duration = (time.perf_counter() - start) * 1000
        logger.debug("DocumentService: imported '%s' in %.1f ms", path.name, duration)
        return doc

    def search_documents(self, query: str, limit: Optional[int] = None):
        # Search using Whoosh
        start = time.perf_counter()
        results = self.search_repo.search(query, limit=limit)
        ids = [r['id'] for r in results]
        
        if not ids:
            logger.debug(
                "DocumentService: search '%s' returned 0 results in %.1f ms",
                query,
                (time.perf_counter() - start) * 1000,
            )
            return []
            
        # Fetch full objects from DB
        docs = self.repo.get_by_ids(ids)
        
        # Re-order to match search result relevance
        doc_map = {d.id: d for d in docs}
        ordered_docs = []
        for doc_id in ids:
            if doc_id in doc_map:
                ordered_docs.append(doc_map[doc_id])
                
        duration = (time.perf_counter() - start) * 1000
        logger.debug(
            "DocumentService: search '%s' returned %s mapped docs in %.1f ms",
            query,
            len(ordered_docs),
            duration,
        )
        return ordered_docs

    def search_documents_with_highlights(self, query: str, limit: Optional[int] = None):
        """Search documents and return results with highlights."""
        return self.search_repo.search(query, limit=limit)

    def get_all_documents(self):
        return self.repo.get_all()
    
    def get_all_documents_metadata(self):
        """Get all documents without loading heavy content fields."""
        start = time.perf_counter()
        docs = self.repo.get_all_metadata()
        logger.debug(
            "DocumentService: get_all_documents_metadata fetched %s docs in %.1f ms",
            len(docs),
            (time.perf_counter() - start) * 1000,
        )
        return docs
    
    def get_document(self, doc_id: int):
        return self.repo.get(doc_id)
    
    def get_document_with_images(self, doc_id: int) -> Optional[Tuple[Document, str]]:
        """
        Get a document with images restored in raw_content.
        
        Returns:
            Tuple of (Document, restored_html) or None if not found
        """
        doc = self.repo.get(doc_id)
        if not doc:
            return None
        
        raw_content = doc.raw_content or doc.content or ""
        
        # If the document has docimg:// references, restore them
        from pillars.document_manager.utils.image_utils import has_docimg_references
        
        if has_docimg_references(raw_content):
            def fetch_image(image_id: int) -> Tuple[bytes, str]:
                img = self.image_repo.get(image_id)
                if img:
                    data = self.image_repo.get_decompressed_data(img)
                    return data, img.mime_type
                raise ValueError(f"Image {image_id} not found")
            
            restored_html = restore_images_in_html(raw_content, fetch_image)
            return doc, restored_html
        
        return doc, raw_content
    
    def get_image(self, image_id: int) -> Optional[Tuple[bytes, str]]:
        """
        Get an image by ID.
        
        Returns:
            Tuple of (image_bytes, mime_type) or None if not found
        """
        img = self.image_repo.get(image_id)
        if img:
            data = self.image_repo.get_decompressed_data(img)
            return data, img.mime_type
        return None
    
    def update_document(self, doc_id: int, **kwargs):
        """
        Update document fields.
        Args:
            doc_id: Document ID
            **kwargs: Fields to update (content, raw_content, title, author, collection)
        """
        start = time.perf_counter()
        doc = self.repo.update(doc_id, **kwargs)
        if doc:
            # If content was updated, re-parse links
            if 'content' in kwargs:
                self._update_links(doc)
            self.search_repo.index_document(doc)
        logger.debug(
            "DocumentService: update_document %s finished in %.1f ms (fields=%s)",
            doc_id,
            (time.perf_counter() - start) * 1000,
            list(kwargs.keys()),
        )
        return doc

    def update_documents(self, doc_ids: list[int], **kwargs):
        """
        Update multiple documents efficiently.
        Args:
            doc_ids: List of Document IDs
            **kwargs: Fields to update
        """
        start = time.perf_counter()
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
        
        logger.debug(
            "DocumentService: update_documents %s ids finished in %.1f ms",
            len(doc_ids),
            (time.perf_counter() - start) * 1000,
        )
        return updated_docs

    def delete_document(self, doc_id: int):
        start = time.perf_counter()
        success = self.repo.delete(doc_id)
        if success:
            self.search_repo.delete_document(doc_id)
        logger.debug(
            "DocumentService: delete_document %s success=%s in %.1f ms",
            doc_id,
            success,
            (time.perf_counter() - start) * 1000,
        )
        return success
    
    def delete_all_documents(self):
        """Delete all documents from database and search index."""
        start = time.perf_counter()
        count = self.repo.delete_all()
        self.search_repo.clear_index()
        logger.debug(
            "DocumentService: delete_all_documents removed %s entries in %.1f ms",
            count,
            (time.perf_counter() - start) * 1000,
        )
        return count

    def rebuild_search_index(self):
        """Rebuild the search index from the database."""
        start = time.perf_counter()
        docs = self.repo.get_all()
        self.search_repo.rebuild_index(docs)
        logger.debug(
            "DocumentService: rebuild_search_index for %s docs in %.1f ms",
            len(docs),
            (time.perf_counter() - start) * 1000,
        )

    # ------------------------------------------------------------------
    # Verse helpers (used by the Holy Book teacher backend)
    # ------------------------------------------------------------------
    def get_document_verses(self, doc_id: int, include_ignored: bool = True):
        return self.verse_repo.get_by_document(doc_id, include_ignored=include_ignored)

    def replace_document_verses(self, doc_id: int, verses: List[dict]):
        return self.verse_repo.replace_document_verses(doc_id, verses)

    def delete_document_verses(self, doc_id: int) -> int:
        return self.verse_repo.delete_by_document(doc_id)


@contextmanager
def document_service_context():
    """Yield a DocumentService backed by a managed DB session."""
    start = time.perf_counter()
    with get_db_session() as db:
        logger.debug("document_service_context: session acquired in %.1f ms", (time.perf_counter() - start) * 1000)
        yield DocumentService(db)
