"""Repository helpers for verse rules."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from shared.models.document_manager.document_verse import VerseRule


class VerseRuleRepository:
    """CRUD helpers for `VerseRule`."""

    def __init__(self, db: Session):
        """
          init   logic.
        
        Args:
            db: Description of db.
        
        """
        self.db = db

    def get(self, rule_id: int) -> Optional[VerseRule]:
        """
        Retrieve logic.
        
        Args:
            rule_id: Description of rule_id.
        
        Returns:
            Result of get operation.
        """
        return self.db.query(VerseRule).filter(VerseRule.id == rule_id).first()

    def list_rules(
        self,
        scope_type: Optional[str] = None,
        scope_value: Optional[str] = None,
        enabled_only: bool = True,
    ) -> List[VerseRule]:
        """
        List rules logic.
        
        Args:
            scope_type: Description of scope_type.
            scope_value: Description of scope_value.
            enabled_only: Description of enabled_only.
        
        Returns:
            Result of list_rules operation.
        """
        query = self.db.query(VerseRule)
        if scope_type:
            query = query.filter(VerseRule.scope_type == scope_type)
        if scope_value is not None:
            query = query.filter(VerseRule.scope_value == scope_value)
        if enabled_only:
            query = query.filter(VerseRule.enabled.is_(True))
        return query.order_by(VerseRule.priority.desc(), VerseRule.id.asc()).all()

    def get_all_enabled(self) -> List[VerseRule]:
        """
        Retrieve all enabled logic.
        
        Returns:
            Result of get_all_enabled operation.
        """
        return (
            self.db.query(VerseRule)
            .filter(VerseRule.enabled.is_(True))
            .order_by(VerseRule.priority.desc(), VerseRule.id.asc())
            .all()
        )

    def save(self, rule: VerseRule) -> VerseRule:
        """
        Save logic.
        
        Args:
            rule: Description of rule.
        
        Returns:
            Result of save operation.
        """
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete(self, rule_id: int) -> bool:
        """
        Remove logic.
        
        Args:
            rule_id: Description of rule_id.
        
        Returns:
            Result of delete operation.
        """
        deleted = self.db.query(VerseRule).filter(VerseRule.id == rule_id).delete()
        self.db.commit()
        return bool(deleted)

    def increment_hit(self, rule_id: int):
        # Use an SQL-level update to increment hit_count to avoid Pylance type issues
        # and ensure the update is performed atomically at the DB level.
        """
        Increment hit logic.
        
        Args:
            rule_id: Description of rule_id.
        
        """
        self.db.query(VerseRule).filter(VerseRule.id == rule_id).update(
            {VerseRule.hit_count: (VerseRule.hit_count + 1)}, synchronize_session="fetch"
        )
        self.db.commit()