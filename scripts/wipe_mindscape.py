import sys
import os
sys.path.append(os.path.join(os.getcwd(), "src"))
from shared.database import get_db_session
from pillars.document_manager.models.mindscape import MindNode, MindEdge

def wipe():
    print("Wiping Mindscape data...")
    with get_db_session() as db:
        # Delete all edges first due to FK
        try:
            db.query(MindEdge).delete()
            db.query(MindNode).delete()
            db.commit()
            print("Mindscape wiped. Canvas is blank.")
        except Exception as e:
            print(f"Error: {e}")
            db.rollback()

if __name__ == "__main__":
    wipe()
