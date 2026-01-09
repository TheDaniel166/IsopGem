
import sys
import os

# Ensure we can import modules
sys.path.append(os.path.join(os.getcwd(), "src"))

from pillars.document_manager.services.mindscape_service import mindscape_service_context

def verify_service():
    print("Verifying Mindscape Service...")
    try:
        with mindscape_service_context() as svc:
            # 1. Get Home
            home = svc.get_or_create_home_node()
            print(f"Home Node: {home.title} (ID: {home.id})")
            
            # 2. Create nodes if empty
            focus, parents, children, jumps = svc.get_local_graph(home.id)
            if not children and not jumps:
                print("Creating test data...")
                child = svc.create_node("Test Child")
                svc.link_nodes(home.id, child.id, "parent") # Home -> Parent of -> Child
                
                jump = svc.create_node("Test Jump")
                svc.link_nodes(home.id, jump.id, "jump") # Home <-> Jump
                
            # 3. Verify Graph
            focus, parents, children, jumps = svc.get_local_graph(home.id)
            # parents/children/jumps are tuples of (node_dto, edge_dto)
            print(f"Focus: {focus.title}")
            print(f"Parents: {[n.title for n, _ in parents]}")
            print(f"Children: {[n.title for n, _ in children]}")
            print(f"Jumps: {[n.title for n, _ in jumps]}")
            
            if len(children) >= 1 and len(jumps) >= 1:
                print("Service Verification SUCCESS.")
            else:
                print("Service Verification FAILED (Missing nodes).")

    except Exception as e:
        print(f"Service Verification ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_service()
