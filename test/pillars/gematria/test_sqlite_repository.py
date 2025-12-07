from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pillars.gematria.models.calculation_record import CalculationRecord
from pillars.gematria.repositories.sqlite_calculation_repository import SQLiteCalculationRepository
from shared.database import Base


@pytest.fixture
def sqlite_repo(tmp_path: Path):
    db_path = tmp_path / "gematria.db"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine)
    return SQLiteCalculationRepository(session_factory=factory)


def build_record(text: str, value: int, favorite: bool = False, tags=None) -> CalculationRecord:
    return CalculationRecord(
        text=text,
        value=value,
        language="Hebrew",
        method="Standard Value",
        is_favorite=favorite,
        tags=tags or [],
        date_created=datetime.utcnow(),
        date_modified=datetime.utcnow(),
    )


def test_sqlite_repository_save_and_retrieve(sqlite_repo: SQLiteCalculationRepository):
    record = build_record("aleph", 1)

    saved = sqlite_repo.save(record)
    fetched = sqlite_repo.get_by_id(saved.id)

    assert fetched is not None
    assert fetched.text == "aleph"
    assert fetched.value == 1
    assert fetched.id == saved.id


def test_sqlite_repository_search_filters(sqlite_repo: SQLiteCalculationRepository):
    first = sqlite_repo.save(build_record("alpha", 5, favorite=True, tags=["letter"]))
    second = sqlite_repo.save(build_record("beta", 9, tags=["number"]))

    favorites = sqlite_repo.get_favorites()
    assert len(favorites) == 1
    assert favorites[0].id == first.id

    by_value = sqlite_repo.get_by_value(9)
    assert len(by_value) == 1
    assert by_value[0].text == "beta"

    tagged = sqlite_repo.get_by_tags(["letter"])
    assert len(tagged) == 1
    assert tagged[0].id == first.id

    summary = sqlite_repo.search(query_str="a", summary_only=True)
    assert summary
    assert summary[0].notes == ""
    assert summary[0].breakdown == ""