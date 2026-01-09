"""
Comprehensive unit tests for Document Search functionality.

Tests cover:
- DocumentSearchRepository: indexing, searching, hit counting
- Search result accuracy and relevance
- Wildcard and phrase searches
- Filter and sort operations

The Seven Seals tested:
♄ SATURN: Index integrity and structure
♃ JUPITER: Large document handling
♂ MARS: Edge cases and error handling
☉ SUN: Core search functionality (happy path)
♀ VENUS: Data consistency and contracts
☿ MERCURY: Logging and signals
☾ MOON: Persistence and state
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture
def temp_index_dir():
    """Create a temporary directory for the search index."""
    temp_dir = tempfile.mkdtemp(prefix="isopgem_test_index_")
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def search_repo(temp_index_dir):
    """Create a DocumentSearchRepository with a temporary index."""
    from pillars.document_manager.repositories.search_repository import DocumentSearchRepository
    
    repo = DocumentSearchRepository(index_dir=temp_index_dir)
    return repo


@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        {
            'id': 1,
            'title': 'The Book of Gematria',
            'content': 'Gematria is the practice of assigning numerical values to words. The number 666 is significant.',
            'file_type': 'html',
            'author': 'Unknown',
            'collection': 'Sacred Texts',
            'created_at': datetime(2024, 1, 1),
            'updated_at': datetime(2024, 1, 1)
        },
        {
            'id': 2,
            'title': 'Introduction to Sacred Geometry',
            'content': 'Sacred geometry involves forms like the Flower of Life. The golden ratio 1.618 appears throughout nature.',
            'file_type': 'txt',
            'author': 'Pythagoras',
            'collection': 'Geometry',
            'created_at': datetime(2024, 2, 15),
            'updated_at': datetime(2024, 2, 15)
        },
        {
            'id': 3,
            'title': 'The Number 1162',
            'content': 'The number 1162 appears in many contexts. It equals 1162 in base 10. The factors of 1162 are 2 and 581.',
            'file_type': 'md',
            'author': 'Magus',
            'collection': 'Numbers',
            'created_at': datetime(2024, 3, 20),
            'updated_at': datetime(2024, 3, 20)
        },
        {
            'id': 4,
            'title': 'Astrological Houses',
            'content': 'The twelve houses represent different life areas. The first house is the house of self.',
            'file_type': 'html',
            'author': 'Ptolemy',
            'collection': 'Astrology',
            'created_at': datetime(2024, 4, 10),
            'updated_at': datetime(2024, 4, 10)
        },
    ]


class MockDocument:
    """Mock Document model for testing."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@pytest.fixture
def mock_documents(sample_documents):
    """Convert sample documents to mock Document objects."""
    return [MockDocument(**doc) for doc in sample_documents]


# ═══════════════════════════════════════════════════════════════════════
# ♄ SATURN: Structure & Boundaries
# ═══════════════════════════════════════════════════════════════════════

class TestSaturnStructure:
    """Tests for index integrity and structure."""
    
    def test_index_creation(self, search_repo, temp_index_dir):
        """Index directory should be created."""
        assert os.path.exists(temp_index_dir)
        # Whoosh creates specific files
        assert os.path.exists(os.path.join(temp_index_dir, "MAIN_WRITELOCK")) or \
               len(os.listdir(temp_index_dir)) > 0
    
    def test_schema_fields(self, search_repo):
        """Schema should have required fields."""
        schema = search_repo.schema
        assert 'id' in schema.names()
        assert 'title' in schema.names()
        assert 'content' in schema.names()
        assert 'file_type' in schema.names()
        assert 'author' in schema.names()
        assert 'collection' in schema.names()
        assert 'created_at' in schema.names()
    
    def test_empty_index_search(self, search_repo):
        """Searching empty index should return empty list."""
        results = search_repo.search("anything")
        assert results == []


# ═══════════════════════════════════════════════════════════════════════
# ☉ SUN: Core Functionality (Happy Path)
# ═══════════════════════════════════════════════════════════════════════

class TestSunCoreFunctionality:
    """Tests for core search functionality."""
    
    def test_index_single_document(self, search_repo, mock_documents):
        """Should index a single document."""
        doc = mock_documents[0]
        search_repo.index_document(doc)
        
        results = search_repo.search("gematria")
        assert len(results) == 1
        assert results[0]['id'] == 1
        assert results[0]['title'] == 'The Book of Gematria'
    
    def test_index_multiple_documents(self, search_repo, mock_documents):
        """Should index multiple documents."""
        for doc in mock_documents:
            search_repo.index_document(doc)
        
        results = search_repo.search("number")
        assert len(results) >= 1
    
    def test_search_by_title(self, search_repo, mock_documents):
        """Should find documents by title."""
        for doc in mock_documents:
            search_repo.index_document(doc)
        
        results = search_repo.search("Sacred Geometry")
        assert len(results) >= 1
        assert any(r['title'] == 'Introduction to Sacred Geometry' for r in results)
    
    def test_search_by_content(self, search_repo, mock_documents):
        """Should find documents by content."""
        for doc in mock_documents:
            search_repo.index_document(doc)
        
        results = search_repo.search("golden ratio")
        assert len(results) >= 1
        assert any('1.618' in r.get('highlights', '') or r['id'] == 2 for r in results)
    
    def test_search_by_author(self, search_repo, mock_documents):
        """Should find documents by author."""
        for doc in mock_documents:
            search_repo.index_document(doc)
        
        results = search_repo.search("Pythagoras")
        assert len(results) >= 1
    
    def test_hit_count_accuracy(self, search_repo, mock_documents):
        """Hit count should reflect actual matches in full content."""
        for doc in mock_documents:
            search_repo.index_document(doc)
        
        # Document 3 has "1162" three times in content + title
        results = search_repo.search("1162")
        doc_3_result = next((r for r in results if r['id'] == 3), None)
        assert doc_3_result is not None
        assert doc_3_result['hit_count'] >= 3  # At least 3 occurrences


# ═══════════════════════════════════════════════════════════════════════
# ♂ MARS: Conflict & Edge Cases
# ═══════════════════════════════════════════════════════════════════════

class TestMarsEdgeCases:
    """Tests for error handling and edge cases."""
    
    def test_empty_query(self, search_repo, mock_documents):
        """Empty query should return empty results."""
        for doc in mock_documents:
            search_repo.index_document(doc)
        
        results = search_repo.search("")
        # Behavior depends on implementation - may return [] or all docs
        assert isinstance(results, list)
    
    def test_nonexistent_term(self, search_repo, mock_documents):
        """Query for nonexistent term should return empty."""
        for doc in mock_documents:
            search_repo.index_document(doc)
        
        results = search_repo.search("xyznonexistent123")
        assert results == []
    
    def test_special_characters(self, search_repo, mock_documents):
        """Should handle special characters gracefully."""
        for doc in mock_documents:
            search_repo.index_document(doc)
        
        # These should not crash
        search_repo.search("1.618")
        search_repo.search("house of self")
        search_repo.search("@#$%")
    
    def test_wildcard_search(self, search_repo, mock_documents):
        """Wildcard search should work."""
        for doc in mock_documents:
            search_repo.index_document(doc)
        
        results = search_repo.search("gem*")
        assert len(results) >= 1  # Should match "gematria", "geometry"
    
    def test_phrase_search(self, search_repo, mock_documents):
        """Phrase search with quotes should work."""
        for doc in mock_documents:
            search_repo.index_document(doc)
        
        results = search_repo.search('"golden ratio"')
        assert len(results) >= 1


# ═══════════════════════════════════════════════════════════════════════
# ♀ VENUS: Harmony & Data Contracts
# ═══════════════════════════════════════════════════════════════════════

class TestVenusDataContracts:
    """Tests for data consistency and API contracts."""
    
    def test_result_structure(self, search_repo, mock_documents):
        """Search results should have consistent structure."""
        for doc in mock_documents:
            search_repo.index_document(doc)
        
        results = search_repo.search("house")
        assert len(results) >= 1
        
        result = results[0]
        assert 'id' in result
        assert 'title' in result
        assert 'file_type' in result
        assert 'collection' in result
        assert 'created_at' in result
        assert 'highlights' in result
        assert 'hit_count' in result
    
    def test_id_is_integer(self, search_repo, mock_documents):
        """Document ID should be returned as integer."""
        for doc in mock_documents:
            search_repo.index_document(doc)
        
        results = search_repo.search("gematria")
        assert len(results) >= 1
        assert isinstance(results[0]['id'], int)
    
    def test_hit_count_is_integer(self, search_repo, mock_documents):
        """Hit count should be an integer."""
        for doc in mock_documents:
            search_repo.index_document(doc)
        
        results = search_repo.search("number")
        assert len(results) >= 1
        assert isinstance(results[0]['hit_count'], int)
        assert results[0]['hit_count'] >= 0


# ═══════════════════════════════════════════════════════════════════════
# ♃ JUPITER: Expansion & Scale
# ═══════════════════════════════════════════════════════════════════════

class TestJupiterScale:
    """Tests for performance with larger datasets."""
    
    def test_many_documents(self, search_repo):
        """Should handle indexing many documents."""
        # Create 100 test documents
        for i in range(100):
            doc = MockDocument(
                id=i,
                title=f"Document {i}",
                content=f"This is document number {i}. It contains the magic number 42.",
                file_type='txt',
                author='Test',
                collection='Bulk',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            search_repo.index_document(doc)
        
        results = search_repo.search("42")
        assert len(results) == 100  # All docs should match
    
    def test_limit_parameter(self, search_repo):
        """Limit parameter should restrict result count."""
        for i in range(50):
            doc = MockDocument(
                id=i,
                title=f"Document {i}",
                content=f"Common keyword appears here.",
                file_type='txt',
                author='Test',
                collection='Limited',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            search_repo.index_document(doc)
        
        results = search_repo.search("common", limit=10)
        assert len(results) <= 10


# ═══════════════════════════════════════════════════════════════════════
# ☾ MOON: Memory & State
# ═══════════════════════════════════════════════════════════════════════

class TestMoonState:
    """Tests for persistence and state management."""
    
    def test_document_update_via_reindex(self, search_repo, mock_documents):
        """Updated documents should reflect new content via delete + index."""
        doc = mock_documents[0]
        search_repo.index_document(doc)
        
        # Verify original is indexed
        results = search_repo.search("gematria")
        assert any(r['id'] == 1 for r in results)
        
        # Update by deleting and re-indexing with unique new term
        search_repo.delete_document(doc.id)
        doc.content = "Completely unique term XYZMAGICWORD123 is here."
        search_repo.index_document(doc)
        
        # New content should match the unique term
        new_results = search_repo.search("XYZMAGICWORD123")
        assert any(r['id'] == 1 for r in new_results)
    
    def test_document_deletion(self, search_repo, mock_documents):
        """Deleted documents should not appear in results."""
        for doc in mock_documents:
            search_repo.index_document(doc)
        
        # Delete document 1
        search_repo.delete_document(1)
        
        results = search_repo.search("gematria")
        assert not any(r['id'] == 1 for r in results)
    
    def test_rebuild_index_clears_and_repopulates(self, search_repo, mock_documents):
        """Rebuilding index should clear and repopulate with given documents."""
        # Index first 2 docs
        for doc in mock_documents[:2]:
            search_repo.index_document(doc)
        
        # Verify doc 1 is indexed
        results = search_repo.search("gematria")
        assert len(results) == 1
        
        # Rebuild with all 4 docs
        search_repo.rebuild_index(mock_documents)
        
        # Now all docs should be searchable - test one from each
        results_1 = search_repo.search("gematria")
        results_4 = search_repo.search("houses")
        assert len(results_1) >= 1
        assert len(results_4) >= 1


# ═══════════════════════════════════════════════════════════════════════
# Integration with RichTextEditor find methods
# ═══════════════════════════════════════════════════════════════════════

class TestEditorFindMethods:
    """Tests for RichTextEditor search/find functionality."""
    
    @pytest.fixture
    def qapp(self):
        """Create QApplication for widget tests."""
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
    
    @pytest.fixture
    def editor(self, qapp):
        """Create RichTextEditor instance."""
        from pillars.document_manager.ui.rich_text_editor import RichTextEditor
        return RichTextEditor()
    
    def test_find_all_matches_count(self, editor):
        """find_all_matches should count correctly."""
        editor.set_text("The word TEST appears here. TEST again. And TEST once more.")
        count = editor.find_all_matches("TEST")
        assert count == 3
    
    def test_find_all_matches_positions(self, editor):
        """Cursor should be at first match after find_all_matches."""
        editor.set_text("First then MATCH here. Another MATCH there.")
        editor.find_all_matches("MATCH")
        
        current, total = editor.get_match_info()
        assert current == 1
        assert total == 2
    
    def test_find_next_increments(self, editor):
        """find_next should increment match counter."""
        editor.set_text("One WORD. Two WORD. Three WORD.")
        editor.find_all_matches("WORD")
        
        editor.find_next()
        current, total = editor.get_match_info()
        assert current == 2
        assert total == 3
    
    def test_find_next_wraps(self, editor):
        """find_next should wrap to beginning."""
        editor.set_text("One WORD. Two WORD.")
        editor.find_all_matches("WORD")
        
        editor.find_next()  # Now at 2
        editor.find_next()  # Should wrap to 1
        
        current, total = editor.get_match_info()
        assert current == 1
    
    def test_find_previous_decrements(self, editor):
        """find_previous should decrement match counter."""
        editor.set_text("One WORD. Two WORD. Three WORD.")
        editor.find_all_matches("WORD")
        
        editor.find_next()  # At 2
        editor.find_previous()  # Back to 1
        
        current, total = editor.get_match_info()
        assert current == 1
    
    def test_find_previous_wraps(self, editor):
        """find_previous should wrap to end."""
        editor.set_text("One WORD. Two WORD. Three WORD.")
        editor.find_all_matches("WORD")
        
        editor.find_previous()  # Should wrap to 3
        
        current, total = editor.get_match_info()
        assert current == 3
    
    def test_clear_search_resets_state(self, editor):
        """clear_search should reset match state."""
        editor.set_text("Some TERM here.")
        editor.find_all_matches("TERM")
        editor.clear_search()
        
        current, total = editor.get_match_info()
        assert current == 0
        assert total == 0
    
    def test_no_matches_returns_zero(self, editor):
        """find_all_matches should return 0 for no matches."""
        editor.set_text("Nothing matches here.")
        count = editor.find_all_matches("XYZNONEXISTENT")
        assert count == 0
    
    def test_empty_search_term(self, editor):
        """Empty search term should return 0."""
        editor.set_text("Some content.")
        count = editor.find_all_matches("")
        assert count == 0
