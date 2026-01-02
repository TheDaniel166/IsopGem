"""
Concordance Indexer Service - Bridges Holy Books to the Master Key.

Indexes words from curated document verses into the TQ Lexicon concordance,
enabling Strong's-style word lookup and cross-referencing across texts.
"""
import re
import logging
from typing import List, Dict, Optional, Tuple, Callable, Any, Sequence
from dataclasses import dataclass, field

from shared.repositories.lexicon.key_database import KeyDatabase
from shared.services.lexicon.holy_key_service import HolyKeyService
from shared.services.gematria.tq_calculator import TQGematriaCalculator

logger = logging.getLogger(__name__)


@dataclass
class IndexingResult:
    """Result of indexing a document."""
    document_id: int
    document_title: str
    total_verses: int
    total_words: int
    new_keys_added: int
    occurrences_added: int
    errors: List[str] = field(default_factory=list)


@dataclass  
class ParseAndIndexResult:
    """Combined result of parsing and indexing."""
    document_id: int
    document_title: str
    # Parsing results
    verses: List[Dict[str, Any]] = field(default_factory=list)
    source: str = "parser"  # 'parser', 'curated', 'fresh'
    anomalies: Dict[str, Any] = field(default_factory=dict)
    rules_applied: List[Dict[str, Any]] = field(default_factory=list)
    # Indexing results
    total_words: int = 0
    new_keys_added: int = 0
    occurrences_added: int = 0
    errors: List[str] = field(default_factory=list)
    # Status
    verses_saved: bool = False
    indexed: bool = False


class ConcordanceIndexerService:
    """
    Unified service for parsing holy books and indexing to the TQ Lexicon.
    
    Provides a single workflow that:
    1. Parses documents into verses (or retrieves curated verses)
    2. Indexes all words into the master key
    3. Records word occurrences linked to verses
    4. Saves curated verses for future use
    
    This eliminates the need for separate parsing and indexing steps.
    """
    
    # Words to skip during indexing (common words with low semantic value)
    STOP_WORDS = {
        'a', 'an', 'the', 'and', 'or', 'but', 'if', 'of', 'to', 'in', 'on',
        'at', 'by', 'for', 'is', 'it', 'be', 'as', 'so', 'we', 'he', 'she',
        'they', 'this', 'that', 'with', 'from', 'are', 'was', 'were', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'can', 'not', 'no', 'yes',
        'all', 'any', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
        'some', 'such', 'than', 'too', 'very', 'just', 'also', 'now', 'only',
        'into', 'upon', 'then', 'when', 'where', 'which', 'who', 'whom', 'whose',
        'what', 'how', 'why', 'here', 'there', 'their', 'them', 'his', 'her',
        'its', 'our', 'your', 'my', 'me', 'him', 'us', 'you', 'i', 'am'
    }
    
    # Minimum word length to index
    MIN_WORD_LENGTH = 2
    
    def __init__(self, db_path: Optional[str] = None):
        self.db = KeyDatabase(db_path)
        self.calculator = TQGematriaCalculator()
        self._ignored_words = None  # Lazy load
        
    def _get_ignored_words(self) -> set:
        """Get the set of ignored words (cached)."""
        if self._ignored_words is None:
            self._ignored_words = set(self.db.get_all_ignored())
        return self._ignored_words
    
    # =========================================================================
    # UNIFIED PARSE + INDEX WORKFLOW
    # =========================================================================
    
    def parse_and_index(
        self,
        document_id: int,
        allow_inline: bool = True,
        apply_rules: bool = True,
        auto_save: bool = True,
        reindex: bool = False,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> ParseAndIndexResult:
        """
        Parse a document into verses and immediately index all words to the concordance.
        
        This is the primary entry point for the unified workflow.
        
        Args:
            document_id: ID of the document to process
            allow_inline: Allow inline verse markers during parsing
            apply_rules: Apply any stored parsing rules
            auto_save: Automatically save verses as curated
            reindex: Clear existing index before re-indexing
            progress_callback: Optional (current, total, message) callback
            
        Returns:
            ParseAndIndexResult with complete parsing and indexing data
        """
        from shared.database import get_db_session
        from shared.services.document_manager.verse_teacher_service import VerseTeacherService
        from shared.repositories.document_manager.document_repository import DocumentRepository
        
        result = ParseAndIndexResult(document_id=document_id, document_title="")
        
        with get_db_session() as db:
            # Get document info
            doc_repo = DocumentRepository(db)
            document = doc_repo.get(document_id)
            
            if not document:
                result.errors.append(f"Document {document_id} not found")
                return result
                
            result.document_title = document.title
            
            if progress_callback:
                progress_callback(0, 100, f"Parsing '{document.title}'...")
            
            # Step 1: Parse or retrieve verses
            verse_service = VerseTeacherService(db)
            parse_result = verse_service.get_or_parse_verses(
                document_id,
                allow_inline=allow_inline,
                apply_rules=apply_rules
            )
            
            result.verses = parse_result.get('verses', [])
            result.source = parse_result.get('source', 'parser')
            result.anomalies = parse_result.get('anomalies', {})
            result.rules_applied = parse_result.get('rules_applied', [])
            
            if not result.verses:
                result.errors.append("No verses found after parsing")
                return result
            
            if progress_callback:
                progress_callback(10, 100, f"Found {len(result.verses)} verses")
            
            # Step 2: Save curated verses (if auto_save and source is parser)
            if auto_save and result.source == 'parser':
                try:
                    verse_service.save_curated_verses(
                        document_id=document_id,
                        verses=result.verses,
                        actor="concordance-indexer",
                        notes="Auto-saved during parse-and-index"
                    )
                    result.verses_saved = True
                    
                    if progress_callback:
                        progress_callback(15, 100, "Verses saved")
                except Exception as e:
                    result.errors.append(f"Failed to save verses: {e}")
        
        # Step 3: Index to concordance (exclude ignored verses)
        if progress_callback:
            progress_callback(20, 100, "Indexing words...")
        
        # Filter out ignored verses before indexing
        active_verses = [
            v for v in result.verses 
            if v.get('status', 'auto') != 'ignored'
        ]
            
        indexing_result = self.index_document(
            document_id=document_id,
            document_title=result.document_title,
            verses=active_verses,
            progress_callback=lambda c, t, m: progress_callback(20 + int(c/t * 80), 100, m) if progress_callback else None,
            reindex=reindex
        )
        
        result.total_words = indexing_result.total_words
        result.new_keys_added = indexing_result.new_keys_added
        result.occurrences_added = indexing_result.occurrences_added
        result.errors.extend(indexing_result.errors)
        result.indexed = True
        
        if progress_callback:
            progress_callback(100, 100, "Complete")
        
        return result
    
    def parse_document(
        self,
        document_id: int,
        allow_inline: bool = True,
        apply_rules: bool = True,
        force_reparse: bool = False
    ) -> Dict[str, Any]:
        """
        Parse a document into verses without indexing.
        
        Args:
            document_id: ID of the document
            allow_inline: Allow inline verse markers
            apply_rules: Apply stored parsing rules
            force_reparse: Force fresh parse even if curated exists
            
        Returns:
            Dict with verses, source, anomalies, rules_applied
        """
        from shared.database import get_db_session
        from shared.services.document_manager.verse_teacher_service import VerseTeacherService
        
        with get_db_session() as db:
            verse_service = VerseTeacherService(db)
            
            if force_reparse:
                return verse_service.generate_parser_run(
                    document_id,
                    allow_inline=allow_inline,
                    apply_rules=apply_rules
                )
            else:
                return verse_service.get_or_parse_verses(
                    document_id,
                    allow_inline=allow_inline,
                    apply_rules=apply_rules
                )
    
    def save_verses(
        self,
        document_id: int,
        verses: Sequence[Dict[str, Any]],
        actor: str = "user",
        notes: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Save curated verses for a document.
        
        Args:
            document_id: Document ID
            verses: List of verse dicts
            actor: Who is saving (for audit)
            notes: Optional notes
            
        Returns:
            List of saved verse dicts
        """
        from shared.database import get_db_session
        from shared.services.document_manager.verse_teacher_service import VerseTeacherService
        
        with get_db_session() as db:
            verse_service = VerseTeacherService(db)
            return verse_service.save_curated_verses(
                document_id=document_id,
                verses=verses,
                actor=actor,
                notes=notes
            )
    
    def get_document_status(self, document_id: int) -> Dict[str, Any]:
        """
        Get the current parsing and indexing status of a document.
        
        Returns:
            Dict with has_curated_verses, is_indexed, verse_count, occurrence_count
        """
        from shared.database import get_db_session
        from shared.services.document_manager.verse_teacher_service import VerseTeacherService
        
        is_indexed = self.db.is_document_indexed(document_id)
        
        with get_db_session() as db:
            verse_service = VerseTeacherService(db)
            curated = verse_service.get_curated_verses(document_id)
            
        return {
            'document_id': document_id,
            'has_curated_verses': len(curated) > 0,
            'verse_count': len(curated),
            'is_indexed': is_indexed,
            'occurrence_count': self._get_document_occurrence_count(document_id) if is_indexed else 0
        }
    
    def _get_document_occurrence_count(self, document_id: int) -> int:
        """Get count of word occurrences for a document."""
        conn = self.db._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM word_occurrences WHERE document_id = ?",
            (document_id,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    # =========================================================================
    # INDEXING METHODS (existing functionality)
    # =========================================================================
    
    def _tokenize_text(self, text: str) -> List[Tuple[str, int, str]]:
        """
        Tokenize text into words with positions.
        
        Returns: List of (normalized_word, position, original_form)
        """
        # Match word tokens (letters only for TQ calculation)
        pattern = re.compile(r'\b([a-zA-Z]+)\b')
        tokens = []
        
        for position, match in enumerate(pattern.finditer(text)):
            original = match.group(1)
            normalized = original.lower()
            
            # Skip if too short
            if len(normalized) < self.MIN_WORD_LENGTH:
                continue
                
            # Skip stop words
            if normalized in self.STOP_WORDS:
                continue
                
            # Skip ignored words
            if normalized in self._get_ignored_words():
                continue
                
            tokens.append((normalized, position, original))
            
        return tokens
    
    def _create_context_snippet(self, text: str, word: str, max_context: int = 60) -> str:
        """
        Create a KWIC (Key Word In Context) snippet.
        Highlights the target word with uppercase.
        """
        # Find word in text (case-insensitive)
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        match = pattern.search(text)
        
        if not match:
            return text[:max_context] + "..." if len(text) > max_context else text
            
        start = match.start()
        end = match.end()
        
        # Calculate context window
        ctx_start = max(0, start - max_context // 2)
        ctx_end = min(len(text), end + max_context // 2)
        
        # Build snippet
        prefix = "..." if ctx_start > 0 else ""
        suffix = "..." if ctx_end < len(text) else ""
        
        snippet = text[ctx_start:start] + word.upper() + text[end:ctx_end]
        return prefix + snippet.strip() + suffix
    
    def index_document(
        self,
        document_id: int,
        document_title: str,
        verses: List[Dict],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        reindex: bool = False
    ) -> IndexingResult:
        """
        Index all words from a document's verses into the concordance.
        
        Args:
            document_id: The document ID from documents table
            document_title: Title of the document (cached in occurrences)
            verses: List of verse dicts with keys: id, verse_number, text
            progress_callback: Optional (current, total, message) callback
            reindex: If True, clear existing occurrences first
            
        Returns:
            IndexingResult with statistics
        """
        errors = []
        new_keys = 0
        occurrences = 0
        total_words = 0
        
        # Clear existing if reindexing
        if reindex:
            cleared = self.db.clear_document_occurrences(document_id)
            logger.info(f"Cleared {cleared} existing occurrences for document {document_id}")
        elif self.db.is_document_indexed(document_id):
            # Already indexed and not reindexing
            return IndexingResult(
                document_id=document_id,
                document_title=document_title,
                total_verses=len(verses),
                total_words=0,
                new_keys_added=0,
                occurrences_added=0,
                errors=["Document already indexed. Use reindex=True to update."]
            )
        
        total_verses = len(verses)
        
        for i, verse in enumerate(verses):
            verse_id = verse.get('id')
            verse_number = verse.get('verse_number') or verse.get('number')
            verse_text = verse.get('text', '')
            
            if not verse_text:
                continue
                
            if progress_callback:
                progress_callback(i + 1, total_verses, f"Indexing verse {verse_number}")
            
            # Tokenize verse text
            tokens = self._tokenize_text(verse_text)
            
            for normalized, position, original in tokens:
                total_words += 1
                
                try:
                    # Calculate TQ value (Standard TQ)
                    tq_value = self.calculator.calculate(normalized)
                    
                    # Add to master_key (or get existing ID and update TQ value)
                    existing_id = self.db.get_id_by_word(normalized)
                    if existing_id is None:
                        key_id = self.db.add_word(normalized, tq_value)
                        new_keys += 1
                    else:
                        key_id = existing_id
                        # Always update TQ value to ensure standard TQ is used
                        self.db.update_tq_value(key_id, tq_value)
                    
                    # Create context snippet
                    context = self._create_context_snippet(verse_text, normalized)
                    
                    # Add word occurrence
                    occ_id = self.db.add_word_occurrence(
                        key_id=key_id,
                        document_id=document_id,
                        document_title=document_title,
                        verse_id=verse_id,
                        verse_number=verse_number,
                        word_position=position,
                        original_form=original,
                        context_snippet=context
                    )
                    
                    if occ_id is not None:
                        occurrences += 1
                        
                except Exception as e:
                    error_msg = f"Error indexing '{normalized}' in verse {verse_number}: {e}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
        
        logger.info(
            f"Indexed document '{document_title}': "
            f"{total_words} words, {new_keys} new keys, {occurrences} occurrences"
        )
        
        return IndexingResult(
            document_id=document_id,
            document_title=document_title,
            total_verses=total_verses,
            total_words=total_words,
            new_keys_added=new_keys,
            occurrences_added=occurrences,
            errors=errors
        )
    
    def index_from_verse_teacher(
        self,
        document_id: int,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        reindex: bool = False
    ) -> IndexingResult:
        """
        Index a document using curated verses from the VerseTeacher system.
        
        This is the primary entry point for indexing holy books.
        """
        from shared.database import get_db_session
        from shared.services.document_manager.verse_teacher_service import VerseTeacherService
        from shared.repositories.document_manager.document_repository import DocumentRepository
        
        with get_db_session() as db:
            # Get document info
            doc_repo = DocumentRepository(db)
            document = doc_repo.get(document_id)
            
            if not document:
                return IndexingResult(
                    document_id=document_id,
                    document_title="Unknown",
                    total_verses=0,
                    total_words=0,
                    new_keys_added=0,
                    occurrences_added=0,
                    errors=[f"Document {document_id} not found"]
                )
            
            # Get curated verses (excluding ignored ones)
            verse_service = VerseTeacherService(db)
            result = verse_service.get_or_parse_verses(document_id)
            all_verses = result.get('verses', [])
            
            # Filter out ignored verses - they should not be indexed
            verses = [
                v for v in all_verses 
                if v.get('status', 'auto') != 'ignored'
            ]
            
            if not verses:
                return IndexingResult(
                    document_id=document_id,
                    document_title=document.title,
                    total_verses=0,
                    total_words=0,
                    new_keys_added=0,
                    occurrences_added=0,
                    errors=["No verses found. Parse the document first with Verse Teacher."]
                )
            
            # Convert verse format if needed
            formatted_verses = []
            for v in verses:
                formatted_verses.append({
                    'id': v.get('id'),
                    'verse_number': v.get('number') or v.get('verse_number'),
                    'text': v.get('text', '')
                })
            
            return self.index_document(
                document_id=document_id,
                document_title=document.title,
                verses=formatted_verses,
                progress_callback=progress_callback,
                reindex=reindex
            )
    
    def get_word_references(self, key_id: int) -> List[Dict]:
        """
        Get all references for a word, formatted for display.
        
        Returns list of dicts with:
        - document_title
        - verse_number  
        - context (KWIC snippet)
        - verse_id (for navigation)
        """
        occurrences = self.db.get_word_occurrences(key_id)
        
        references = []
        for occ in occurrences:
            references.append({
                'document_title': occ.document_title,
                'document_id': occ.document_id,
                'verse_number': occ.verse_number,
                'verse_id': occ.verse_id,
                'context': occ.context_snippet,
                'original_form': occ.original_form
            })
        
        return references
    
    def get_stats(self) -> Dict[str, int]:
        """Get concordance statistics."""
        return self.db.get_concordance_stats()
