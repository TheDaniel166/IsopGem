"""Whoosh-based repository for storing and searching gematria calculations."""
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

from whoosh import index
from whoosh.fields import Schema, TEXT, NUMERIC, ID, DATETIME, BOOLEAN, KEYWORD
from whoosh.qparser import MultifieldParser
from whoosh.query import And, Term, Or, Every

from ..models import CalculationRecord


class CalculationRepository:
    """Repository for managing gematria calculation storage and retrieval using Whoosh."""
    
    def __init__(self, index_dir: Optional[str] = None):
        """
        Initialize the calculation repository.
        
        Args:
            index_dir: Directory for the Whoosh index. Defaults to ~/.isopgem/calculations
        """
        if index_dir is None:
            # Default to user's home directory
            home = Path.home()
            index_dir = str(home / '.isopgem' / 'calculations')
        
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Define schema
        self.schema = Schema(
            id=ID(stored=True, unique=True),
            text=TEXT(stored=True),
            normalized_text=TEXT(stored=True),
            value=NUMERIC(stored=True, sortable=True),
            language=TEXT(stored=True),
            method=TEXT(stored=True),
            date_created=DATETIME(stored=True, sortable=True),
            date_modified=DATETIME(stored=True, sortable=True),
            notes=TEXT(stored=True),
            source=TEXT(stored=True),
            tags=KEYWORD(stored=True, commas=True, scorable=True),
            breakdown=TEXT(stored=True),
            character_count=NUMERIC(stored=True),
            user_rating=NUMERIC(stored=True),
            is_favorite=BOOLEAN(stored=True),
            category=TEXT(stored=True),
            related_ids=TEXT(stored=True),
        )
        
        # Create or open index
        if index.exists_in(str(self.index_dir)):
            self.ix = index.open_dir(str(self.index_dir))
        else:
            self.ix = index.create_in(str(self.index_dir), self.schema)

        self._text_parser = MultifieldParser(
            ["text", "normalized_text", "notes", "source"],
            schema=self.schema,
        )
        self._match_all_query = Every()
    
    def save(self, record: CalculationRecord) -> CalculationRecord:
        """
        Save a calculation record.
        
        Args:
            record: The calculation record to save
            
        Returns:
            The saved record with ID assigned
        """
        writer = self.ix.writer()
        
        try:
            # Generate ID if not present
            if not record.id:
                record.id = str(uuid.uuid4())
            
            # Update modification time
            record.date_modified = datetime.now()
            
            # Prepare tags as comma-separated string
            tags_str = ','.join(record.tags) if record.tags else ''
            
            # Add/update document
            writer.update_document(
                id=record.id,
                text=record.text,
                normalized_text=record.normalized_text,
                value=record.value,
                language=record.language,
                method=record.method,
                date_created=record.date_created,
                date_modified=record.date_modified,
                notes=record.notes,
                source=record.source,
                tags=tags_str,
                breakdown=record.breakdown,
                character_count=record.character_count,
                user_rating=record.user_rating,
                is_favorite=record.is_favorite,
                category=record.category,
                related_ids=','.join(record.related_ids) if record.related_ids else '',
            )
            
            writer.commit()
            return record
            
        except Exception as e:
            writer.cancel()
            raise e
    
    def get_by_id(self, record_id: str) -> Optional[CalculationRecord]:
        """
        Retrieve a calculation by ID.
        
        Args:
            record_id: The record ID
            
        Returns:
            The calculation record or None if not found
        """
        with self.ix.searcher() as searcher:
            query = Term("id", record_id)
            results = searcher.search(query, limit=1)
            
            if results:
                return self._result_to_record(results[0])
            return None
    
    def delete(self, record_id: str) -> bool:
        """
        Delete a calculation record.
        
        Args:
            record_id: The record ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        writer = self.ix.writer()
        
        try:
            writer.delete_by_term('id', record_id)
            writer.commit()
            return True
        except Exception as e:
            writer.cancel()
            raise e
    
    def search(
        self,
        query_str: Optional[str] = None,
        language: Optional[str] = None,
        value: Optional[int] = None,
        tags: Optional[List[str]] = None,
        favorites_only: bool = False,
        limit: int = 100,
        page: int = 1,
        summary_only: bool = True,
    ) -> List[CalculationRecord]:
        """
        Search for calculation records.
        
        Args:
            query_str: Search text (searches text, notes, source)
            language: Filter by language
            value: Filter by exact value
            tags: Filter by tags (any match)
            favorites_only: Only return favorites
            limit: Page size to return
            page: 1-based page number
            summary_only: Return lightweight records if True
            
        Returns:
            List of matching calculation records
        """
        with self.ix.searcher() as searcher:
            queries = []
            
            # Text search across multiple fields
            if query_str:
                queries.append(self._text_parser.parse(query_str))
            
            # Filter by language
            if language:
                queries.append(Term("language", language))
            
            # Filter by value
            if value is not None:
                queries.append(Term("value", value))
            
            # Filter by tags
            if tags:
                tag_terms = [Term("tags", tag) for tag in tags if tag]
                if tag_terms:
                    queries.append(Or(tag_terms))
            
            # Filter favorites
            if favorites_only:
                queries.append(Term("is_favorite", True))
            
            # Combine queries
            query = And(queries) if queries else self._match_all_query

            pagelen = max(1, limit)
            page = max(1, page)
            try:
                results = searcher.search_page(
                    query,
                    page,
                    pagelen=pagelen,
                    sortedby="date_modified",
                    reverse=True,
                )
            except ValueError:
                return []

            converter = (
                self._result_to_summary if summary_only else self._result_to_record
            )
            return [converter(result) for result in results]
    
    def get_all(self, limit: int = 1000) -> List[CalculationRecord]:
        """
        Get all calculation records.
        
        Args:
            limit: Maximum records to return
            
        Returns:
            List of all calculation records
        """
        return self.search(limit=limit, page=1, summary_only=False)
    
    def get_by_value(self, value: int, limit: int = 100) -> List[CalculationRecord]:
        """
        Get all calculations with a specific value.
        
        Args:
            value: The gematria value to search for
            limit: Maximum results to return
            
        Returns:
            List of matching records
        """
        return self.search(value=value, limit=limit, summary_only=False)
    
    def get_favorites(self, limit: int = 100) -> List[CalculationRecord]:
        """
        Get all favorite calculations.
        
        Args:
            limit: Maximum results to return
            
        Returns:
            List of favorite records
        """
        return self.search(favorites_only=True, limit=limit, summary_only=False)
    
    def get_by_tags(self, tags: List[str], limit: int = 100) -> List[CalculationRecord]:
        """
        Get calculations by tags.
        
        Args:
            tags: List of tags to search for
            limit: Maximum results to return
            
        Returns:
            List of matching records
        """
        return self.search(tags=tags, limit=limit, summary_only=False)
    
    def _result_to_summary(self, result) -> CalculationRecord:
        """Convert a Whoosh result into a lightweight CalculationRecord."""
        tags = result['tags'].split(',') if result.get('tags') else []
        tags = [t.strip() for t in tags if t.strip()]

        return CalculationRecord(
            id=result['id'],
            text=result['text'],
            normalized_text=result.get('normalized_text', ''),
            value=result['value'],
            language=result['language'],
            method=result['method'],
            date_created=result['date_created'],
            date_modified=result['date_modified'],
            tags=tags,
            character_count=result.get('character_count', 0),
            user_rating=result.get('user_rating', 0),
            is_favorite=result.get('is_favorite', False),
            category=result.get('category', ''),
        )

    def _result_to_record(self, result) -> CalculationRecord:
        """Convert Whoosh search result to CalculationRecord."""
        # Parse tags
        tags = result['tags'].split(',') if result.get('tags') else []
        tags = [t.strip() for t in tags if t.strip()]
        
        # Parse related IDs
        related_ids = result.get('related_ids', '').split(',') if result.get('related_ids') else []
        related_ids = [r.strip() for r in related_ids if r.strip()]
        
        return CalculationRecord(
            id=result['id'],
            text=result['text'],
            normalized_text=result.get('normalized_text', ''),
            value=result['value'],
            language=result['language'],
            method=result['method'],
            date_created=result['date_created'],
            date_modified=result['date_modified'],
            notes=result.get('notes', ''),
            source=result.get('source', ''),
            tags=tags,
            breakdown=result.get('breakdown', ''),
            character_count=result.get('character_count', 0),
            user_rating=result.get('user_rating', 0),
            is_favorite=result.get('is_favorite', False),
            category=result.get('category', ''),
            related_ids=related_ids,
        )
