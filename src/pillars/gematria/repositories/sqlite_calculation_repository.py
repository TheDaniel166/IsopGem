"""SQLite-backed repository for gematria calculations."""
from __future__ import annotations

import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Callable, Iterator, List, Optional, Sequence

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from shared.database import SessionLocal
from ..models import CalculationEntity, CalculationRecord


class SQLiteCalculationRepository:
    """Repository implementation that stores data in SQLite via SQLAlchemy."""

    def __init__(self, session_factory: Callable[[], Session] = SessionLocal):
        """
          init   logic.
        
        Args:
            session_factory: Description of session_factory.
        
        """
        self._session_factory = session_factory

    @contextmanager
    def _session(self) -> Iterator[Session]:
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def save(self, record: CalculationRecord) -> CalculationRecord:
        """Insert or update a record, returning the saved version."""
        with self._session() as session:
            entity = None
            if record.id:
                entity = session.get(CalculationEntity, record.id)
            if entity is None:
                entity = CalculationEntity(id=record.id or str(uuid.uuid4()))
                session.add(entity)
                if not record.id:
                    record.id = str(entity.id)
                    record.date_created = datetime.utcnow()
            if not record.date_created:
                record.date_created = datetime.utcnow()
            record.date_modified = datetime.utcnow()
            entity.update_from_record(record)
            session.flush()
            return entity.to_record()

    def get_by_id(self, record_id: str) -> Optional[CalculationRecord]:
        """Fetch a record by primary key."""
        with self._session() as session:
            entity = session.get(CalculationEntity, record_id)
            return entity.to_record() if entity else None

    def delete(self, record_id: str) -> bool:
        """Remove a record by ID."""
        with self._session() as session:
            entity = session.get(CalculationEntity, record_id)
            if not entity:
                return False
            session.delete(entity)
            session.flush()
            return True

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def search(
        self,
        query_str: Optional[str] = None,
        language: Optional[str] = None,
        value: Optional[int] = None,
        tags: Optional[Sequence[str]] = None,
        favorites_only: bool = False,
        limit: int = 100,
        page: int = 1,
        summary_only: bool = True,
        search_mode: str = "General",
    ) -> List[CalculationRecord]:
        """Search calculations by metadata."""
        with self._session() as session:
            stmt = select(CalculationEntity)

            if query_str:
                if search_mode == "Exact":
                    # Strict equality on Text or Notes
                    stmt = stmt.where(
                        or_(
                            CalculationEntity.text == query_str,
                            CalculationEntity.notes == query_str
                        )
                    )
                elif search_mode == "Regex":
                    # Uses the REGEXP function we injected
                    stmt = stmt.where(
                        or_(
                            CalculationEntity.text.op("REGEXP")(query_str),
                            CalculationEntity.notes.op("REGEXP")(query_str)
                        )
                    )
                elif search_mode == "Wildcard":
                    # Use LIKE with user-provided wildcards (no auto-%)
                    stmt = stmt.where(
                        or_(
                            CalculationEntity.text.like(query_str),
                            CalculationEntity.notes.like(query_str)
                        )
                    )
                else:
                    # General: Contains (auto-wildcards)
                    like_pattern = f"%{query_str}%"
                    stmt = stmt.where(
                        or_(
                            CalculationEntity.text.ilike(like_pattern),
                            CalculationEntity.normalized_text.ilike(like_pattern),
                            CalculationEntity.notes.ilike(like_pattern),
                            CalculationEntity.source.ilike(like_pattern),
                        )
                    )

            if language:
                stmt = stmt.where(CalculationEntity.language.ilike(f"%{language}%"))

            if value is not None:
                stmt = stmt.where(CalculationEntity.value == value)

            if favorites_only:
                stmt = stmt.where(CalculationEntity.is_favorite.is_(True))

            stmt = stmt.order_by(CalculationEntity.date_modified.desc())
            offset = max(page - 1, 0) * max(limit, 1)
            stmt = stmt.offset(offset).limit(limit)

            entities = session.execute(stmt).scalars().all()

            records = [entity.to_record() for entity in entities]
            if tags:
                normalized_tags = {tag.strip().lower() for tag in tags if tag}
                records = [
                    record
                    for record in records
                    if normalized_tags.intersection({t.lower() for t in record.tags})
                ]

            if summary_only:
                for record in records:
                    record.notes = ""
                    record.source = ""
                    record.breakdown = ""
            return records

    def get_all(self, limit: int = 1000) -> List[CalculationRecord]:
        """
        Retrieve all logic.
        
        Args:
            limit: Description of limit.
        
        Returns:
            Result of get_all operation.
        """
        return self.search(limit=limit, page=1, summary_only=False)

    def get_by_value(self, value: int, limit: int = 100) -> List[CalculationRecord]:
        """
        Retrieve by value logic.
        
        Args:
            value: Description of value.
            limit: Description of limit.
        
        Returns:
            Result of get_by_value operation.
        """
        return self.search(value=value, limit=limit, summary_only=False)

    def get_favorites(self, limit: int = 100) -> List[CalculationRecord]:
        """
        Retrieve favorites logic.
        
        Args:
            limit: Description of limit.
        
        Returns:
            Result of get_favorites operation.
        """
        return self.search(favorites_only=True, limit=limit, summary_only=False)

    def get_by_tags(self, tags: List[str], limit: int = 100) -> List[CalculationRecord]:
        """
        Retrieve by tags logic.
        
        Args:
            tags: Description of tags.
            limit: Description of limit.
        
        Returns:
            Result of get_by_tags operation.
        """
        return self.search(tags=tags, limit=limit, summary_only=False)

    def get_by_text(self, text: str, limit: int = 100) -> List[CalculationRecord]:
        """Fetch records with exact text match."""
        with self._session() as session:
            stmt = select(CalculationEntity).where(CalculationEntity.text == text)
            stmt = stmt.limit(limit)
            entities = session.execute(stmt).scalars().all()
            return [entity.to_record() for entity in entities]