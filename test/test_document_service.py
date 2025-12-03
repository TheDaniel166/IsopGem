"""Tests for DocumentService database operations."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Generator
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, close_all_sessions

from shared import database
from shared.database import get_db_session
from pillars.document_manager.services.document_service import DocumentService


@pytest.fixture(autouse=True)
def isolated_database(tmp_path):
    """Provide an isolated SQLite database for each test run."""
    test_db = tmp_path / "isopgem_test.db"
    engine = create_engine(f"sqlite:///{test_db}")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Point the shared database module at the temporary database
    database.engine.dispose()
    database.engine = engine
    database.SessionLocal = TestingSessionLocal
    database.DB_DIR = tmp_path
    database.DB_PATH = test_db

    database.Base.metadata.drop_all(bind=engine)
    database.Base.metadata.create_all(bind=engine)

    yield

    close_all_sessions()
    database.Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(autouse=True)
def in_memory_search_repo(monkeypatch) -> Generator[Dict[int, Dict[str, Any]], None, None]:
    """Stub out the Whoosh-backed repository with an in-memory store."""
    storage: Dict[int, Dict[str, Any]] = {}

    class InMemorySearchRepository:
        def __init__(self, *_, **__):
            self._storage = storage

        def index_document(self, doc):
            self._storage[doc.id] = {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content or "",
                "tags": doc.tags or "",
                "file_type": doc.file_type,
                "created_at": doc.created_at,
            }

        def index_documents(self, docs):
            for doc in docs:
                self.index_document(doc)

        def delete_document(self, doc_id: int):
            self._storage.pop(doc_id, None)

        def search(self, query: str, limit: int | None = None):
            term = query.lower()
            results = [
                {
                    "id": data["id"],
                    "title": data["title"],
                    "file_type": data["file_type"],
                    "created_at": data["created_at"],
                    "highlights": data["content"],
                }
                for data in self._storage.values()
                if term in data["title"].lower()
                or term in data["content"].lower()
                or term in data["tags"].lower()
            ]
            if limit is not None:
                results = results[:limit]
            return results

        def rebuild_index(self, documents):
            self.clear_index()
            self.index_documents(documents)

        def clear_index(self):
            self._storage.clear()

    monkeypatch.setattr(
        "pillars.document_manager.services.document_service.DocumentSearchRepository",
        InMemorySearchRepository,
    )

    yield storage

    storage.clear()


def _write_sample_file(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / f"{name}.txt"
    path.write_text(content, encoding="utf-8")
    return path


def test_import_and_fetch_document(tmp_path):
    sample = _write_sample_file(tmp_path, "alpha_doc", "Alpha body with [[Link]]")

    with get_db_session() as db:
        service = DocumentService(db)
        created = service.import_document(str(sample), tags="research", collection="Library")
        doc_id = created.id

        fetched = service.get_document(doc_id)
        assert fetched.title == "alpha_doc"
        assert fetched.tags == "research"
        assert fetched.collection == "Library"
        assert "Alpha body" in fetched.content

        assert len(service.get_all_documents()) == 1
        assert len(service.get_all_documents_metadata()) == 1


def test_search_documents_returns_matching_rows(tmp_path):
    first = _write_sample_file(tmp_path, "sun", "Bright alpha rays")
    second = _write_sample_file(tmp_path, "moon", "Lunar notes and reflections")

    with get_db_session() as db:
        service = DocumentService(db)
        doc_a = service.import_document(str(first), tags="astronomy", collection="Sky")
        service.import_document(str(second), tags="journal", collection="Night")

        hits = service.search_documents("alpha")
        assert [doc.id for doc in hits] == [doc_a.id]

        raw_hits = service.search_documents_with_highlights("alpha")
        assert raw_hits and raw_hits[0]["id"] == doc_a.id

        limited = service.search_documents("notes", limit=1)
        assert len(limited) == 1


def test_update_and_delete_document(tmp_path, in_memory_search_repo):
    sample = _write_sample_file(tmp_path, "draft", "Original text")

    with get_db_session() as db:
        service = DocumentService(db)
        doc = service.import_document(str(sample), tags="draft", collection="Inbox")
        updated = service.update_document(doc.id, tags="final", content="Rewritten body")
        assert updated.tags == "final"
        assert "Rewritten" in updated.content

        service.delete_document(doc.id)
        assert doc.id not in in_memory_search_repo
        assert service.get_document(doc.id) is None


def test_batch_update_documents(tmp_path):
    first = _write_sample_file(tmp_path, "note1", "First memo")
    second = _write_sample_file(tmp_path, "note2", "Second memo")

    with get_db_session() as db:
        service = DocumentService(db)
        doc_one = service.import_document(str(first), collection="Initial")
        doc_two = service.import_document(str(second), collection="Initial")

        updated_docs = service.update_documents([int(doc_one.id), int(doc_two.id)], collection="Archive", tags="processed")
        assert len(updated_docs) == 2
        assert {doc.collection for doc in updated_docs} == {"Archive"}
        assert {doc.tags for doc in updated_docs} == {"processed"}


def test_delete_all_documents_clears_index(tmp_path, in_memory_search_repo):
    first = _write_sample_file(tmp_path, "alpha", "Alpha content")
    second = _write_sample_file(tmp_path, "beta", "Beta content")

    with get_db_session() as db:
        service = DocumentService(db)
        service.import_document(str(first))
        service.import_document(str(second))

        removed = service.delete_all_documents()
        assert removed == 2
        assert service.get_all_documents() == []
        assert len(in_memory_search_repo) == 0


def test_rebuild_search_index_repopulates_entries(tmp_path, in_memory_search_repo):
    sample = _write_sample_file(tmp_path, "gamma", "Gamma rays")

    with get_db_session() as db:
        service = DocumentService(db)
        service.import_document(str(sample))
        assert len(in_memory_search_repo) == 1

        # Simulate a cleared index and rebuild it from the DB
        in_memory_search_repo.clear()
        assert len(in_memory_search_repo) == 0

        service.rebuild_search_index()
        assert len(in_memory_search_repo) == 1