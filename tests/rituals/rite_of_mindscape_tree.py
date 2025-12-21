import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.database import Base, get_db_session
from pillars.document_manager.services.mindscape_service import MindscapeService, MindEdgeType

def rite_of_mindscape_tree():
    print("Beginning Rite of the Mindscape Tree...")
    
    with get_db_session() as db:
        svc = MindscapeService(db)
        
        # 1. Clean Slate (Caution!)
        # svc.wipe_database() # Let's not wipe actual DB, just testing locally? 
        # Actually this runs against user DB. Let's create unique naming to avoid collision or cleanup after.
        
        suffix = "_TEST_RITE"
        
        # 2. Create Root
        root = svc.create_node(title=f"Root{suffix}", type="notebook")
        assert root.id is not None
        print(f"Created Root: {root.title}")
        
        # 3. Create Child
        child = svc.create_node(title=f"Child{suffix}", parent_id=root.id)
        print(f"Created Child: {child.title} linked to {root.id}")
        
        # 4. Verify Hierarchy
        roots = svc.get_roots()
        # Filter for our test root
        my_root = next((r for r in roots if r.id == root.id), None)
        assert my_root is not None, "Root not found in get_roots"
        
        children = svc.get_children(root.id)
        my_child = next((c for c in children if c.id == child.id), None)
        assert my_child is not None, "Child not found in get_children"
        print("Hierarchy verified.")
        
        # 5. Move Child
        # Create another root
        root2 = svc.create_node(title=f"Root2{suffix}")
        svc.move_node_to_parent(child.id, root2.id)
        
        children_old = svc.get_children(root.id)
        assert not any(c.id == child.id for c in children_old), "Child still attached to old root"
        
        children_new = svc.get_children(root2.id)
        assert any(c.id == child.id for c in children_new), "Child not attached to new root"
        print("Move verified.")
        
        # Cleanup
        svc.delete_node(root.id)
        svc.delete_node(root2.id)
        svc.delete_node(child.id) # Should be gone if cascaded? delete_node deletes edges. Child node remains? 
        # existing delete_node implementation deletes the node and edges.
        # But here child was child of root2. if I delete root2, does it cascade?
        # delete_node implementation:
        # 1. deletes edges
        # 2. deletes node
        # It does NOT recursively delete children. 
        # So I need to delete child manually to be clean.
        svc.delete_node(child.id)
        
        print("Rite Complete.")

if __name__ == "__main__":
    rite_of_mindscape_tree()
