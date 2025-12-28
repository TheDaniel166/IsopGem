"""Shared Gematria Models.

Hosted here to prevent circular dependencies (e.g. TQ needs DB entities) and 
maintain pillar sovereignty.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


# -- Calculation Record (DTO) --------------------------------------------

@dataclass
class CalculationRecord:
    """Represents a saved gematria calculation."""
    
    # Core calculation data
    text: str                           # The word/phrase calculated
    value: int                          # The calculated gematria value
    language: str                       # Language/system (e.g., "Hebrew (Standard)")
    method: str                         # Calculation method (e.g., "Standard Value")
    
    # Metadata
    id: Optional[str] = None           # Unique identifier (generated)
    date_created: datetime = field(default_factory=datetime.now)
    date_modified: datetime = field(default_factory=datetime.now)
    
    # Additional information
    notes: str = ""                     # User notes about this calculation
    source: str = ""                    # Source reference (e.g., Bible verse, book)
    tags: List[str] = field(default_factory=list)  # Searchable tags
    
    # Calculation details
    breakdown: str = ""                 # JSON string of letter-value breakdown
    character_count: int = 0            # Number of characters counted
    normalized_text: str = ""           # Text after normalization (no diacritics)
    
    # User organization
    user_rating: int = 0                # 0-5 star rating
    is_favorite: bool = False           # Favorite flag
    category: str = ""                  # User-defined category
    
    # Relationships
    related_ids: List[str] = field(default_factory=list)  # IDs of related calculations
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'text': self.text,
            'value': self.value,
            'language': self.language,
            'method': self.method,
            'date_created': self.date_created.isoformat(),
            'date_modified': self.date_modified.isoformat(),
            'notes': self.notes,
            'source': self.source,
            'tags': json.dumps(self.tags),
            'breakdown': self.breakdown,
            'character_count': self.character_count,
            'normalized_text': self.normalized_text,
            'user_rating': self.user_rating,
            'is_favorite': self.is_favorite,
            'category': self.category,
            'related_ids': json.dumps(self.related_ids),
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CalculationRecord':
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            text=data['text'],
            value=int(data['value']),
            language=data['language'],
            method=data['method'],
            date_created=datetime.fromisoformat(data.get('date_created', datetime.now().isoformat())),
            date_modified=datetime.fromisoformat(data.get('date_modified', datetime.now().isoformat())),
            notes=data.get('notes', ''),
            source=data.get('source', ''),
            tags=json.loads(data.get('tags', '[]')),
            breakdown=data.get('breakdown', ''),
            character_count=int(data.get('character_count', 0)),
            normalized_text=data.get('normalized_text', ''),
            user_rating=int(data.get('user_rating', 0)),
            is_favorite=bool(data.get('is_favorite', False)),
            category=data.get('category', ''),
            related_ids=json.loads(data.get('related_ids', '[]')),
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.text} ({self.language}) = {self.value}"


# -- Calculation Entity (DB Model) ---------------------------------------

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

    def update_from_record(self, record: CalculationRecord) -> None:
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

    def to_record(self) -> CalculationRecord:
        """Convert this entity into a `CalculationRecord`."""

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
