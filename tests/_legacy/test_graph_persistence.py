
import pytest
import json
from pillars.document_manager.services.mindscape_service import MindscapeService
from pillars.document_manager.models.mindscape import MindNode
from shared.database import get_db_session

def test_node_position_persistence():
    with get_db_session() as db:
        service = MindscapeService(db)
        
        # 1. Create a node
        node = service.create_node(title="Persist Me")
        node_id = node.id
        
        # 2. Update Position
        service.update_node_position(node_id, 100.5, -50.2)
        
        # 3. Verify it's saved in JSON
        stored_node = db.query(MindNode).get(node_id)
        data = json.loads(stored_node.appearance)
        
        assert "pos" in data
        assert data["pos"] == [100.5, -50.2]
        
        # 4. Clean up
        service.delete_node(node_id)
