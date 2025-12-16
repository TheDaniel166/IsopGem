import argparse
import os
import sys

sys.path.append(os.path.join(os.getcwd(), "src"))
from shared.database import get_db_session  # noqa: E402
from pillars.document_manager.models.mindscape import MindNode, MindEdge  # noqa: E402


def wipe(force: bool = False):
    if not force:
        print("Refusing to wipe Mindscape without --force. Aborting.")
        return

    print("Wiping Mindscape data...")
    with get_db_session() as db:
        try:
            db.query(MindEdge).delete()
            db.query(MindNode).delete()
            db.commit()
            print("Mindscape wiped. Canvas is blank.")
        except Exception as e:
            print(f"Error: {e}")
            db.rollback()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wipe all Mindscape data.")
    parser.add_argument("--force", action="store_true", help="Confirm irreversible deletion.")
    args = parser.parse_args()
    wipe(force=args.force)
