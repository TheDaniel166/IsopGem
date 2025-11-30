"""Data model for stored gematria calculations."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
import json


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
