import logging
import sqlite3
import os

DB_PATH = "data/isopgem.db"

logger = logging.getLogger(__name__)

def migrate_mindscape():
    """
    Migrate mindscape logic.
    
    """
    if not os.path.exists(DB_PATH):
        logger.error("Database not found at %s", DB_PATH)
        return

    logger.info("Migrating Mindscape Schema in %s...", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Helpers
    def column_exists(table, col):
        """
        Column exists logic.
        
        Args:
            table: Description of table.
            col: Description of col.
        
        """
        try:
            cursor.execute(f"SELECT {col} FROM {table} LIMIT 1")
            return True
        except sqlite3.OperationalError:
            return False

    def add_column(table, col, type_def):
        """
        Add column logic.
        
        Args:
            table: Description of table.
            col: Description of col.
            type_def: Description of type_def.
        
        """
        if not column_exists(table, col):
            logger.info("Adding %s to %s...", col, table)
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {type_def}")
                logger.info("  Success: Added %s", col)
            except Exception as e:
                logger.exception("  Error adding %s", col)
        else:
            logger.info("Skipping %s (already exists in %s)", col, table)

    # MindNodes Migration
    add_column("mind_nodes", "content", "TEXT")
    add_column("mind_nodes", "tags", "TEXT")
    add_column("mind_nodes", "appearance", "TEXT")
    add_column("mind_nodes", "metadata_payload", "TEXT")
    add_column("mind_nodes", "document_id", "INTEGER")

    # MindEdges Migration
    add_column("mind_edges", "appearance", "TEXT")

    conn.commit()
    conn.close()
    logger.info("Migration Complete.")

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO, format="%(message)s")
    migrate_mindscape()