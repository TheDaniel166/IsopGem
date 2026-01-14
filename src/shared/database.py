"""
SHARED JUSTIFICATION:
- RATIONALE: Core Infrastructure
- USED BY: Astrology, Correspondences, Document_manager, Gematria, Tq, Tq_lexicon (34 references)
- CRITERION: 2 (Essential for app to function)
"""

"""Shared database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
from contextlib import contextmanager
import os

# Define Base for models
Base = declarative_base()

from shared.config import get_config

# Database path - centralized via config
# Database path - centralized via config
config = get_config()
DB_PATH = config.paths.main_db

# Ensure directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Create engine
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# Register REGEXP function for SQLite
from sqlalchemy import event
import re

@event.listens_for(engine, "connect")
def sqlite_regexp(dbapi_connection, connection_record):
    """
    Sqlite regexp logic.
    
    Args:
        dbapi_connection: Description of dbapi_connection.
        connection_record: Description of connection_record.
    
    """
    def regexp(expr, item):
        """
        Regexp logic.
        
        Args:
            expr: Description of expr.
            item: Description of item.
        
        """
        if item is None:
            return False
        try:
            reg = re.compile(expr, re.IGNORECASE)
            return reg.search(item) is not None
        except Exception:
            return False
    dbapi_connection.create_function("REGEXP", 2, regexp)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database tables."""
    # Import models lazily so SQLAlchemy registers all mappings before creating tables.
    import pillars.document_manager.models  # noqa: F401
    import pillars.correspondences.models.correspondence_models  # noqa: F401
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """Context manager wrapper around get_db() that always closes the session."""
    generator = get_db()
    db = next(generator)
    try:
        yield db
    finally:
        # Ensure generator cleanup runs even if user forgets
        try:
            generator.close()
        except StopIteration:
            pass