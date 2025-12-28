"""Audit log repository for verse teaching actions."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from shared.models.document_manager.document_verse import VerseEditLog


class VerseEditLogRepository:
    """
    Verse Edit Log Repository class definition.
    
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

    def log(
        self,
        document_id: Optional[int],
        action: str,
        verse_id: Optional[int] = None,
        rule_id: Optional[int] = None,
        payload: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> VerseEditLog:
        """
        Log logic.
        
        Args:
            document_id: Description of document_id.
            action: Description of action.
            verse_id: Description of verse_id.
            rule_id: Description of rule_id.
            payload: Description of payload.
            notes: Description of notes.
        
        Returns:
            Result of log operation.
        """
        entry = VerseEditLog(
            document_id=document_id,
            verse_id=verse_id,
            rule_id=rule_id,
            action=action,
            payload=payload,
            notes=notes,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def list_recent(self, document_id: int, limit: int = 50) -> List[VerseEditLog]:
        """
        List recent logic.
        
        Args:
            document_id: Description of document_id.
            limit: Description of limit.
        
        Returns:
            Result of list_recent operation.
        """
        return (
            self.db.query(VerseEditLog)
            .filter(VerseEditLog.document_id == document_id)
            .order_by(VerseEditLog.created_at.desc())
            .limit(limit)
            .all()
        )