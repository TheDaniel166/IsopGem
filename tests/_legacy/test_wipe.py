
import pytest
from pillars.document_manager.services.mindscape_service import MindscapeService
from pillars.document_manager.models.mindscape import MindNode, MindEdge
from shared.database import get_db_session

def test_wipe_database():
    with get_db_session() as db:
        service = MindscapeService(db)
        
        # 1. Populate
        n1 = service.create_node(title="To Be Deleted")
        n2 = service.create_node(title="Also Deleted")
        service.link_nodes(n1.id, n2.id, "parent")
        
        assert db.query(MindNode).count() >= 2
        assert db.query(MindEdge).count() >= 1
        
        # 2. Wipe
        service.wipe_database()
        
        # 3. Verify Empty
        assert db.query(MindNode).count() == 0
        assert db.query(MindEdge).count() == 0
