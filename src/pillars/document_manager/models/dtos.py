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
