import argparse

from shared.database import engine, Base
from sqlalchemy import text


def reset_mindscape(force: bool = False):
    if not force:
        print("Refusing to reset Mindscape without --force. Aborting.")
        return

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
    parser = argparse.ArgumentParser(description="Drop and recreate Mindscape tables.")
    parser.add_argument("--force", action="store_true", help="Confirm irreversible reset.")
    args = parser.parse_args()
    reset_mindscape(force=args.force)
