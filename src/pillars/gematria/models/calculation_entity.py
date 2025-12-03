"""SQLAlchemy entity for persisting gematria calculations."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base

if TYPE_CHECKING:  # pragma: no cover - import only for typing
    from .calculation_record import CalculationRecord


class CalculationEntity(Base):
    """SQLAlchemy model that stores gematria calculation metadata."""

    __tablename__ = "gematria_calculations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    value: Mapped[int] = mapped_column(nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    method: Mapped[str] = mapped_column(String(120), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    source: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tags: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    breakdown: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    character_count: Mapped[int] = mapped_column(nullable=False, default=0)
    normalized_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="", index=True)
    user_rating: Mapped[int] = mapped_column(nullable=False, default=0)
    is_favorite: Mapped[bool] = mapped_column(nullable=False, default=False, index=True)
    category: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    related_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    date_created: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    date_modified: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def update_from_record(self, record: "CalculationRecord") -> None:
        """Populate entity fields from a `CalculationRecord`."""

        self.text = record.text
        self.normalized_text = record.normalized_text
        self.value = record.value
        self.language = record.language
        self.method = record.method
        self.notes = record.notes
        self.source = record.source
        self.tags = json.dumps(record.tags, ensure_ascii=False)
        self.breakdown = record.breakdown or "[]"
        self.character_count = record.character_count
        self.normalized_hash = record.normalized_text.lower()
        self.user_rating = record.user_rating
        self.is_favorite = record.is_favorite
        self.category = record.category
        self.related_ids = json.dumps(record.related_ids, ensure_ascii=False)
        self.date_created = record.date_created
        self.date_modified = record.date_modified

    def to_record(self) -> "CalculationRecord":
        """Convert this entity into a `CalculationRecord`."""

        from .calculation_record import CalculationRecord  # local import to avoid cycle

        tags: List[str] = json.loads(self.tags or "[]")
        related_ids: List[str] = json.loads(self.related_ids or "[]")

        return CalculationRecord(
            id=self.id,
            text=self.text,
            normalized_text=self.normalized_text,
            value=self.value,
            language=self.language,
            method=self.method,
            notes=self.notes,
            source=self.source,
            tags=tags,
            breakdown=self.breakdown,
            character_count=self.character_count,
            user_rating=self.user_rating,
            is_favorite=self.is_favorite,
            category=self.category,
            related_ids=related_ids,
            date_created=self.date_created,
            date_modified=self.date_modified,
        )
