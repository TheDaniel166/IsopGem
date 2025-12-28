"""Repository helpers for verse rules."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from shared.models.document_manager.document_verse import VerseRule


class VerseRuleRepository:
    """CRUD helpers for `VerseRule`."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, rule_id: int) -> Optional[VerseRule]:
        return self.db.query(VerseRule).filter(VerseRule.id == rule_id).first()

    def list_rules(
        self,
        scope_type: Optional[str] = None,
        scope_value: Optional[str] = None,
        enabled_only: bool = True,
    ) -> List[VerseRule]:
        query = self.db.query(VerseRule)
        if scope_type:
            query = query.filter(VerseRule.scope_type == scope_type)
        if scope_value is not None:
            query = query.filter(VerseRule.scope_value == scope_value)
        if enabled_only:
            query = query.filter(VerseRule.enabled.is_(True))
        return query.order_by(VerseRule.priority.desc(), VerseRule.id.asc()).all()

    def get_all_enabled(self) -> List[VerseRule]:
        return (
            self.db.query(VerseRule)
            .filter(VerseRule.enabled.is_(True))
            .order_by(VerseRule.priority.desc(), VerseRule.id.asc())
            .all()
        )

    def save(self, rule: VerseRule) -> VerseRule:
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete(self, rule_id: int) -> bool:
        deleted = self.db.query(VerseRule).filter(VerseRule.id == rule_id).delete()
        self.db.commit()
        return bool(deleted)

    def increment_hit(self, rule_id: int):
        # Use an SQL-level update to increment hit_count to avoid Pylance type issues
        # and ensure the update is performed atomically at the DB level.
        self.db.query(VerseRule).filter(VerseRule.id == rule_id).update(
            {VerseRule.hit_count: (VerseRule.hit_count + 1)}, synchronize_session="fetch"
        )
        self.db.commit()

