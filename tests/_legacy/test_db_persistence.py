
import pytest
from pillars.document_manager.services.mindscape_service import MindscapeService
from pillars.document_manager.models.mindscape import MindNode
from shared.database import get_db_session

def test_search_node_is_in_db():
    title = "Test Persistent Search"
    
    # 1. Create
    with get_db_session() as db:
        service = MindscapeService(db)
        node = service.create_node(title=title, type="search_query")
        node_id = node.id
        
    # 2. Re-open DB (Simulate Restart)
    with get_db_session() as db:
        # Direct SQL Query or Service
        fetched = db.query(MindNode).filter_by(id=node_id).first()
        assert fetched is not None
        assert fetched.title == title
        assert fetched.type == "search_query"
