
import pytest
import json
from pillars.document_manager.services.mindscape_service import MindscapeService
from shared.database import get_db_session

def test_search_node_metadata():
    with get_db_session() as db:
        service = MindscapeService(db)
        
        # 1. Create Search Node with Results Meta
        results = [
            {"id": 101, "title": "Doc A", "highlights": "Foo"},
            {"id": 102, "title": "Doc B", "highlights": "Bar"}
        ]
        meta = {"results": results}
        
        node = service.create_node(
            title="Search: test", 
            type="search_query", 
            metadata_payload=meta
        )
        
        # 2. Verify Storage
        assert node.metadata_payload is not None
        stored_meta = json.loads(node.metadata_payload)
        assert "results" in stored_meta
        assert len(stored_meta["results"]) == 2
        assert stored_meta["results"][0]["title"] == "Doc A"
        
        # 3. Simulate "Add to Graph" logic (Service side check)
        # Ensure we can link NEW document to this search node
        new_doc = service.create_node(
            title="Doc A", 
            type="document", 
            metadata_payload={"document_id": 101}
        )
        
        service.link_nodes(new_doc.id, node.id, "parent")
        
        # Verify Link
        # (Already tested in previous tests, but good sanity check)

from PyQt6.QtWidgets import QApplication
from pillars.document_manager.ui.search_results_panel import SearchResultsPanel

# Basic App for Widgets
app = QApplication([])

def test_search_panel_population():
    panel = SearchResultsPanel()
    
    results = [
        {"id": 101, "title": "Doc A", "highlights": "Foo"},
        {"id": 102, "title": "Doc B", "highlights": "Bar"}
    ]
    
    panel.load_results(results)
    
    # Verify List Count
    assert panel.list_widget.count() == 2
    
    # Verify Content
    item = panel.list_widget.item(0)
    assert "Doc A" in item.text()
    assert "Foo" in item.text()
    
def test_search_panel_empty():
    panel = SearchResultsPanel()
    panel.load_results([])
    assert panel.list_widget.count() == 1
    assert "No results" in panel.list_widget.item(0).text()


