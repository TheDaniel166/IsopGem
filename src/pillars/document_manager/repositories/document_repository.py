"""Repository for Document model."""
from sqlalchemy.orm import Session, defer
from pillars.document_manager.models.document import Document
from typing import List, Optional
import time
import logging

logger = logging.getLogger(__name__)

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, doc_id: int) -> Optional[Document]:
        return self.db.query(Document).filter(Document.id == doc_id).first()

    def get_by_ids(self, doc_ids: List[int]) -> List[Document]:
        return self.db.query(Document).filter(Document.id.in_(doc_ids)).all()

    def get_all(self) -> List[Document]:
        return self.db.query(Document).all()

    def get_all_metadata(self) -> List[Document]:
        """Fetch all documents but defer loading of heavy content fields."""
        start = time.perf_counter()
        logger.debug("DocumentRepository: preparing metadata query with deferred content")
        query = self.db.query(Document).options(
            defer(Document.content), 
            defer(Document.raw_content)
        )
        logger.debug("DocumentRepository: executing metadata query ...")
        docs = query.all()
        logger.debug(
            "DocumentRepository: get_all_metadata fetched %s rows in %.1f ms",
            len(docs),
            (time.perf_counter() - start) * 1000,
        )
        return docs

    def search(self, query: str) -> List[Document]:
        # Basic SQL LIKE search. For advanced search, we'd use Whoosh or Full Text Search.
        return self.db.query(Document).filter(
            (Document.title.ilike(f"%{query}%")) | 
            (Document.content.ilike(f"%{query}%"))
        ).all()

    def create(self, title: str, content: str, file_type: str, file_path: str = None, raw_content: str = None, 
               tags: str = None, author: str = None, collection: str = None) -> Document:
        db_doc = Document(
            title=title,
            content=content,
            file_type=file_type,
            file_path=file_path,
            raw_content=raw_content,
            tags=tags,
            author=author,
            collection=collection
        )
        self.db.add(db_doc)
        self.db.commit()
        self.db.refresh(db_doc)
        return db_doc

    def update(self, doc_id: int, **kwargs) -> Optional[Document]:
        doc = self.get(doc_id)
        if doc:
            for key, value in kwargs.items():
                setattr(doc, key, value)
            self.db.commit()
            self.db.refresh(doc)
        return doc

    def delete(self, doc_id: int) -> bool:
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
