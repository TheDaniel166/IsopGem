
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "src"))

from pillars.document_manager.services.mindscape_service import mindscape_service_context

def repro():
    print("Reproducing DetachedInstanceError...")
    node_to_access = None
    
    # 1. Fetch in context
    with mindscape_service_context() as svc:
        home = svc.get_or_create_home_node()
        # This returns SQLAlchemy objects attached to the session
        focus, parents, children, jumps = svc.get_local_graph(home.id)
        if children:
            node_to_access = children[0]
        else:
            print("No children found, cannot repro.")
            return

    # 2. Context exit -> Session closes -> Objects expire (if expire_on_commit=True)
    
    # 3. Access outside context
    try:
        print(f"Accessing node: {node_to_access.id}") # PK usually fine
        print(f"Accessing title: {node_to_access.title}") # Should trigger refresh -> CRASH
        print("Attribute access successful (Failed to Repro?)")
    except Exception as e:
        print(f"Caught Expected Error: {e}")

if __name__ == "__main__":
    repro()
