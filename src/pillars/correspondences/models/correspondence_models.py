"""
Correspondence Models - The Emerald Scrolls.
SQLAlchemy models for storing correspondence tables with JSON-based grid content.
"""
from sqlalchemy import Column, String, DateTime, JSON
from shared.database import Base
from datetime import datetime
import uuid

class CorrespondenceTable(Base):
    """
    Represents a 'Spreadsheet' or 'Table' of correspondences.
    
    The 'content' JSON blob stores the grid data:
    {
        "columns": ["Hebrew", "English", "Number"],
        "rows": [
            {"0": "Aleph", "1": "A", "2": 1},
            {"0": "Beth",  "1": "B", "2": 2}
        ],
        "meta": {
            "formulae": {"0:2": "=GEMATRIA(0:0)"}
        }
    }
    """
    __tablename__ = 'correspondence_tables'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Store the entire grid state as JSON for maximum flexibility (schema-less)
    content = Column(JSON, default=dict)

    def to_dict(self):
        """Clean serialization for UI/Transport."""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "content": self.content or {}
        }
