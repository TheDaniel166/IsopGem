
import pytest
import json
from pillars.document_manager.services.mindscape_service import MindscapeService
from pillars.document_manager.models.mindscape import MindEdgeType
from shared.database import get_db_session

def test_duplicate_prevention_and_linking():
    with get_db_session() as db:
        service = MindscapeService(db)
        
        # 1. Simulate an existing Document Node
        doc_id = 999
        existing_doc = service.create_node(
            title="Epistle 1",
            type="document",
            metadata_payload={"document_id": doc_id}
        )
        
        # 2. Simulate Search Logic (finding the same doc_id)
        # Verify find helper
        found = service.find_node_by_document_id(doc_id)
        assert found is not None
        assert found.id == existing_doc.id
        
        # 3. Simulate creating Search Node and Linking
        search_node = service.create_node(title="Concept: Love", type="search_query")
        
        # Link: Doc -> Search (Parent -> Child)
        edge = service.link_nodes(found.id, search_node.id, "parent")
        
        assert edge.source_id == found.id
        assert edge.target_id == search_node.id
