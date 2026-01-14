"""Models supporting curated Holy Book verses and parser training."""
from __future__ import annotations

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    ForeignKey,
    Boolean,
    DateTime,
    Index,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from shared.database import Base


class DocumentVerse(Base):
    """Represents a single verse segment curated for a document."""

    __tablename__ = "document_verses"
    __table_args__ = (
        Index("ix_document_verses_document", "document_id", "verse_number"),
        Index("ix_document_verses_offsets", "document_id", "start_offset", "end_offset"),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    verse_number = Column(Integer, nullable=False)
    start_offset = Column(Integer, nullable=False)
    end_offset = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

    status = Column(String, default="auto", nullable=False, index=True)
    confidence = Column(Float, default=0.0)
    source_type = Column(String, default="parser", nullable=False)
    rule_id = Column(Integer, ForeignKey("verse_rules.id"), nullable=True)
    notes = Column(Text, nullable=True)
    extra_data = Column(Text, nullable=True)  # JSON blob for future metadata

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    rule = relationship("VerseRule", back_populates="verses")
    edit_logs = relationship(
        "VerseEditLog",
        back_populates="verse",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class VerseRule(Base):
    """A reusable heuristic describing how to treat a verse marker."""

    __tablename__ = "verse_rules"
    __table_args__ = (
        Index("ix_verse_rules_scope", "scope_type", "scope_value"),
        Index("ix_verse_rules_priority", "priority", "enabled"),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, index=True)
    scope_type = Column(String, default="global", nullable=False)
    scope_value = Column(String, nullable=True)
    description = Column(String, nullable=True)
    pattern_before = Column(String, nullable=True)
    pattern_after = Column(String, nullable=True)
    action = Column(String, default="promote", nullable=False)
    parameters = Column(Text, nullable=True)
    priority = Column(Integer, default=0, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    hit_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    verses = relationship("DocumentVerse", back_populates="rule")
    edit_logs = relationship("VerseEditLog", back_populates="rule")


class VerseEditLog(Base):
    """Audit log for verse edits and teaching actions."""

    __tablename__ = "verse_edit_log"
    __table_args__ = (
        Index("ix_verse_edit_log_document", "document_id", "created_at"),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)
    verse_id = Column(Integer, ForeignKey("document_verses.id", ondelete="SET NULL"), nullable=True)
    rule_id = Column(Integer, ForeignKey("verse_rules.id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False)
    payload = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    verse = relationship("DocumentVerse", back_populates="edit_logs")
    rule = relationship("VerseRule", back_populates="edit_logs")