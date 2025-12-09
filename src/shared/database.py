"""Shared database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
from contextlib import contextmanager
import os

# Define Base for models
Base = declarative_base()

# Database path
# FIX: Use absolute path relative to this file to avoid CWD issues
# src/shared/database.py -> src/shared -> src -> PROJECT_ROOT
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_DIR = PROJECT_ROOT / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "isopgem.db"

# Create engine
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database tables."""
    # Import models lazily so SQLAlchemy registers all mappings before creating tables.
    import pillars.document_manager.models  # noqa: F401
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
