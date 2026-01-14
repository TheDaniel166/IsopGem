"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: Contract (Document schemas) - GRANDFATHERED, may be infrastructure
- USED BY: Document_manager (4 references)
- CRITERION: 4 (Shared data contract) OR 2 (if docs are global infrastructure)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""Data Transfer Objects for Document Manager."""
from dataclasses import dataclass
from typing import Optional

from datetime import datetime

@dataclass
class DocumentMetadataDTO:
    """Lightweight representation of document metadata."""

    id: int
    title: str
    file_type: str
    collection: Optional[str]
    author: Optional[str]
    updated_at: Optional[datetime]