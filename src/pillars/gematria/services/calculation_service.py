"""Service layer for managing gematria calculations."""
import json
from typing import List, Optional
from datetime import datetime

from ..models import CalculationRecord
from ..repositories import CalculationRepository
from .base_calculator import GematriaCalculator


class CalculationService:
    """Service for managing calculation records."""
    
    def __init__(self, repository: Optional[CalculationRepository] = None):
        """
        Initialize the calculation service.
        
        Args:
            repository: Optional repository instance. Creates default if not provided.
        """
        self.repository = repository or CalculationRepository()
    
    def save_calculation(
        self,
        text: str,
        value: int,
        calculator: GematriaCalculator,
        breakdown: List[tuple],
        notes: str = "",
        source: str = "",
        tags: List[str] = None,
        category: str = "",
        user_rating: int = 0,
        is_favorite: bool = False,
    ) -> CalculationRecord:
        """
        Save a new calculation.
        
        Args:
            text: The original text
            value: The calculated value
            calculator: The calculator used
            breakdown: List of (char, value) tuples
            notes: User notes
            source: Source reference
            tags: List of tags
            category: User category
            user_rating: 0-5 star rating
            is_favorite: Favorite flag
            
        Returns:
            The saved calculation record
        """
        # Convert breakdown to JSON string
        breakdown_data = [{"char": char, "value": val} for char, val in breakdown]
        breakdown_json = json.dumps(breakdown_data, ensure_ascii=False)
        
        # Get normalized text
        normalized_text = calculator.normalize_text(text)
        
        # Create record
        record = CalculationRecord(
            text=text,
            normalized_text=normalized_text,
            value=value,
            language=calculator.name,
            method=calculator.name,
            notes=notes,
            source=source,
            tags=tags or [],
            breakdown=breakdown_json,
            character_count=len(breakdown),
            category=category,
            user_rating=user_rating,
            is_favorite=is_favorite,
        )
        
        return self.repository.save(record)
    
    def update_calculation(
        self,
        record_id: str,
        notes: Optional[str] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        user_rating: Optional[int] = None,
        is_favorite: Optional[bool] = None,
    ) -> Optional[CalculationRecord]:
        """
        Update an existing calculation's metadata.
        
        Args:
            record_id: The record ID to update
            notes: Updated notes (if provided)
            source: Updated source (if provided)
            tags: Updated tags (if provided)
            category: Updated category (if provided)
            user_rating: Updated rating (if provided)
            is_favorite: Updated favorite status (if provided)
            
        Returns:
            The updated record or None if not found
        """
        record = self.repository.get_by_id(record_id)
        if not record:
            return None
        
        # Update only provided fields
        if notes is not None:
            record.notes = notes
        if source is not None:
            record.source = source
        if tags is not None:
            record.tags = tags
        if category is not None:
            record.category = category
        if user_rating is not None:
            record.user_rating = user_rating
        if is_favorite is not None:
            record.is_favorite = is_favorite
        
        record.date_modified = datetime.now()
        
        return self.repository.save(record)
    
    def delete_calculation(self, record_id: str) -> bool:
        """
        Delete a calculation.
        
        Args:
            record_id: The record ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete(record_id)
    
    def get_calculation(self, record_id: str) -> Optional[CalculationRecord]:
        """
        Get a calculation by ID.
        
        Args:
            record_id: The record ID
            
        Returns:
            The calculation record or None if not found
        """
        return self.repository.get_by_id(record_id)
    
    def search_calculations(
        self,
        query: Optional[str] = None,
        language: Optional[str] = None,
        value: Optional[int] = None,
        tags: Optional[List[str]] = None,
        favorites_only: bool = False,
        limit: int = 100,
        page: int = 1,
        summary_only: bool = True,
    ) -> List[CalculationRecord]:
        """
        Search for calculations.
        
        Args:
            query: Search text
            language: Filter by language
            value: Filter by value
            tags: Filter by tags
            favorites_only: Only favorites
            limit: Max results
            page: Page number (1-indexed)
            summary_only: Return lightweight records if True
            
        Returns:
            List of matching records
        """
        return self.repository.search(
            query_str=query,
            language=language,
            value=value,
            tags=tags,
            favorites_only=favorites_only,
            limit=limit,
            page=page,
            summary_only=summary_only,
        )
    
    def get_all_calculations(self, limit: int = 1000) -> List[CalculationRecord]:
        """
        Get all calculations.
        
        Args:
            limit: Maximum records to return
            
        Returns:
            List of all calculation records
        """
        return self.repository.get_all(limit=limit)
    
    def get_calculations_by_value(self, value: int) -> List[CalculationRecord]:
        """
        Find all calculations with a specific value.
        
        Args:
            value: The gematria value to search for
            
        Returns:
            List of calculations with that value
        """
        return self.repository.get_by_value(value)
    
    def get_favorite_calculations(self) -> List[CalculationRecord]:
        """
        Get all favorite calculations.
        
        Returns:
            List of favorite records
        """
        return self.repository.get_favorites()
    
    def toggle_favorite(self, record_id: str) -> Optional[CalculationRecord]:
        """
        Toggle the favorite status of a calculation.
        
        Args:
            record_id: The record ID
            
        Returns:
            The updated record or None if not found
        """
        record = self.repository.get_by_id(record_id)
        if not record:
            return None
        
        record.is_favorite = not record.is_favorite
        record.date_modified = datetime.now()
        
        return self.repository.save(record)
    
    def get_breakdown_from_record(self, record: CalculationRecord) -> List[tuple]:
        """
        Parse breakdown JSON from record.
        
        Args:
            record: The calculation record
            
        Returns:
            List of (char, value) tuples
        """
        if not record.breakdown:
            return []
        
        try:
            breakdown_data = json.loads(record.breakdown)
            parsed: List[tuple] = []
            for item in breakdown_data if isinstance(breakdown_data, list) else []:
                # Support both dict format {"char": c, "value": v} and list/tuple [c, v]
                if isinstance(item, dict):
                    c = item.get('char')
                    v = item.get('value')
                    if c is not None and v is not None:
                        parsed.append((c, int(v)))
                elif isinstance(item, (list, tuple)) and len(item) == 2:
                    parsed.append((item[0], int(item[1])))
                else:
                    # Ignore unknown shapes
                    continue
            return parsed
        except Exception:
            # Any parsing problem -> return empty breakdown for robustness
            return []
