"""Repository helpers for document verse records."""
from __future__ import annotations

from typing import Iterable, List, Optional, Sequence

from sqlalchemy.orm import Session

from shared.models.document_manager.document_verse import DocumentVerse


class DocumentVerseRepository:
    """Encapsulates CRUD operations for `DocumentVerse` rows."""

    def __init__(self, db: Session):
        """
          init   logic.
        
        Args:
            db: Description of db.
        
        """
        self.db = db

    def get(self, verse_id: int) -> Optional[DocumentVerse]:
        """
        Retrieve logic.
        
        Args:
            verse_id: Description of verse_id.
        
        Returns:
            Result of get operation.
        """
        return self.db.query(DocumentVerse).filter(DocumentVerse.id == verse_id).first()

    def get_by_document(self, document_id: int, include_ignored: bool = True) -> List[DocumentVerse]:
        """
        Retrieve by document logic.
        
        Args:
            document_id: Description of document_id.
            include_ignored: Description of include_ignored.
        
        Returns:
            Result of get_by_document operation.
        """
        query = self.db.query(DocumentVerse).filter(DocumentVerse.document_id == document_id)
        if not include_ignored:
            query = query.filter(DocumentVerse.status != "ignored")
        return query.order_by(DocumentVerse.verse_number, DocumentVerse.start_offset).all()

    def replace_document_verses(
        self,
        document_id: int,
        verse_payload: Sequence[dict],
    ) -> List[DocumentVerse]:
        """Replace all verse rows for a document with the provided payload."""
        self.delete_by_document(document_id)
        objects: List[DocumentVerse] = []
        for data in verse_payload:
            obj = DocumentVerse(
                document_id=document_id,
                verse_number=int(data.get("verse_number") or data.get("number", 0)),
                start_offset=int(data.get("start_offset") or data.get("start", 0)),
                end_offset=int(data.get("end_offset") or data.get("end", 0)),
                text=data.get("text", ""),
                status=data.get("status", "auto"),
                confidence=float(data.get("confidence", 0.0)),
                source_type=data.get("source_type", "parser"),
                rule_id=data.get("rule_id"),
                notes=data.get("notes"),
                extra_data=data.get("extra_data"),
            )
            objects.append(obj)

        if objects:
            self.db.add_all(objects)
        self.db.commit()
        for obj in objects:
            self.db.refresh(obj)
        return objects

    def delete_by_document(self, document_id: int) -> int:
        """Delete all verses tied to a document."""
        deleted = (
            self.db.query(DocumentVerse)
            .filter(DocumentVerse.document_id == document_id)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted

    def save(self, verse: DocumentVerse) -> DocumentVerse:
        """
        Save logic.
        
        Args:
            verse: Description of verse.
        
        Returns:
            Result of save operation.
        """
        self.db.add(verse)
        self.db.commit()
        self.db.refresh(verse)
        return verse

    def bulk_upsert(self, verses: Iterable[DocumentVerse]) -> List[DocumentVerse]:
        """
        Bulk upsert logic.
        
        Args:
            verses: Description of verses.
        
        Returns:
            Result of bulk_upsert operation.
        """
        verses = list(verses)
        if not verses:
            return []
        self.db.add_all(verses)
        self.db.commit()
        for verse in verses:
            self.db.refresh(verse)
        return verses

    def count_for_document(self, document_id: int) -> int:
        """
        Count for document logic.
        
        Args:
            document_id: Description of document_id.
        
        Returns:
            Result of count_for_document operation.
        """
        return (
            self.db.query(DocumentVerse)
            .filter(DocumentVerse.document_id == document_id)
            .count()
        )