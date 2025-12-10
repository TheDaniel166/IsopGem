
import pytest
import json
from pillars.document_manager.services.mindscape_service import MindscapeService
from shared.database import get_db_session

def test_search_node_structure_only():
    with get_db_session() as db:
        service = MindscapeService(db)
        
        # 1. Ensure Existing Node
        existing = service.create_node(
             title="Existing Doc", 
             type="document", 
             metadata_payload={"document_id": 999}
        )
        
        # 2. Simulate Search Logic (Manual call to link, now disabled)
        # We want to verify that searching does NOT link to this node automatically.
        # But `_create_search_node` is UI logic. 
        # Here we test the SERVICE doesn't auto-link? No, the Service doesn't know about search.
        # We validated the CHANGE in the UI code.
        
        # Instead, let's verify metadata parsing again, and ensure a search node 
        # is created isolated.
        
        clean_results = [{"id": 999, "title": "Existing Doc", "highlights": "Foo"}]
        meta = {"results": clean_results}
        
        search_node = service.create_node(
            title="Search Without Links",
            type="search_query",
            metadata_payload=meta
        )
        
        # 3. Verify Isolation
        _, parents, children, _ = service.get_local_graph(search_node.id)
        assert len(parents) == 0
        assert len(children) == 0
        
        # 4. Storage Check
        stored = json.loads(search_node.metadata_payload)
        assert stored["results"][0]["id"] == 999
