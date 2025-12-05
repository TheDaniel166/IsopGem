"""Audit log repository for verse teaching actions."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from pillars.document_manager.models import VerseEditLog


class VerseEditLogRepository:
    def __init__(self, db: Session):
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
        return (
            self.db.query(VerseEditLog)
            .filter(VerseEditLog.document_id == document_id)
            .order_by(VerseEditLog.created_at.desc())
            .limit(limit)
            .all()
        )
