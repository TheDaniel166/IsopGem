from shared.database import engine, Base
from pillars.document_manager.models.mindscape import MindNode, MindEdge
from sqlalchemy import text

def reset_mindscape():
    print("Resetting Mindscape Tables...")
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        conn.execute(text("DROP TABLE IF EXISTS mind_edges"))
        conn.execute(text("DROP TABLE IF EXISTS mind_nodes"))
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.commit()
    
    # Recreate
    Base.metadata.create_all(bind=engine)
    print("Mindscape Tables Recreated.")

if __name__ == "__main__":
    reset_mindscape()
