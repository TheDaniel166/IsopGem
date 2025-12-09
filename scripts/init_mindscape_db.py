
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "src"))
from shared.database import engine, Base
from pillars.document_manager.models import MindNode, MindEdge

def init_db():
    print("Creating Mindscape tables...")
    MindNode.__table__.create(bind=engine, checkfirst=True)
    MindEdge.__table__.create(bind=engine, checkfirst=True)
    print("Tables created.")

if __name__ == "__main__":
    init_db()
