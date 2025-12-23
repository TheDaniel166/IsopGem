"""Service for building and managing a corpus-based dictionary."""
import re
import logging
from typing import Set, Optional
from sqlalchemy.orm import Session
from pillars.document_manager.repositories.document_repository import DocumentRepository
from shared.database import get_db

logger = logging.getLogger(__name__)

class CorpusDictionaryService:
    """
    Scans documents (specifically those marked as 'Holy' or other criteria)
    to build a set of valid words for acrostic validation.
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CorpusDictionaryService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_session: Optional[Session] = None):
        if self._initialized:
            return
            
        self._words: Set[str] = set()
        self._is_loaded = False
        self.db = db_session if db_session else next(get_db())
        self.repo = DocumentRepository(self.db)
        self._initialized = True

    def load_dictionary(self, collection_filter: str = "Holy") -> int:
        """
        Loads words from documents matching the collection filter.
        Returns the number of unique words found.
        """
        logger.info(f"Building dictionary from collection containing: '{collection_filter}'...")
        
        docs = self.repo.get_by_collection_name(collection_filter)
        if not docs:
            logger.warning(f"No documents found for collection filter: {collection_filter}")
            return 0
            
        word_pattern = re.compile(r'\b[a-zA-Z]{2,}\b') # Words with 2+ letters
        
        new_words = set()
        for doc in docs:
            if not doc.content:
                continue
            
            # Simple content cleaning and traversing
            # Case insensitive storage
            found = word_pattern.findall(doc.content)
            for w in found:
                new_words.add(w.upper())
                
        self._words = new_words
        self._is_loaded = True
        logger.info(f"Dictionary built. Total unique words: {len(self._words)}")
        return len(self._words)

    def get_words(self) -> list[str]:
        """Return a sorted list of all words in the dictionary."""
        return sorted(list(self._words))

    def is_word(self, candidate: str) -> bool:
        """Check if a candidate string exists in the loaded dictionary."""
        if not self._is_loaded:
            logger.warning("Dictionary not loaded! Call load_dictionary() first.")
            return False
        return candidate.upper() in self._words

    @property
    def word_count(self) -> int:
        return len(self._words)
