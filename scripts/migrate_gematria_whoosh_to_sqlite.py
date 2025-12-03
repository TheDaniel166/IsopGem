"""Import existing Whoosh-stored gematria calculations into SQLite."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List

from datetime import datetime

from whoosh import index
from whoosh.query import Every

from pillars.gematria.models import CalculationRecord
from pillars.gematria.repositories.sqlite_calculation_repository import SQLiteCalculationRepository
from shared.database import init_db

DEFAULT_INDEX = Path.home() / ".isopgem" / "calculations"


def load_whoosh_records(index_dir: Path) -> Iterable[CalculationRecord]:
    """Yield every calculation stored inside the legacy Whoosh index."""
    if not index.exists_in(str(index_dir)):
        raise FileNotFoundError(f"Whoosh index not found at {index_dir}")

    ix = index.open_dir(str(index_dir))
    with ix.searcher() as searcher:
        results = searcher.search(Every(), limit=None)
        for hit in results:
            tags = [t.strip() for t in (hit.get("tags") or "").split(",") if t.strip()]
            related_ids = [r.strip() for r in (hit.get("related_ids") or "").split(",") if r.strip()]
            date_created = hit.get("date_created") or datetime.utcnow()
            date_modified = hit.get("date_modified") or date_created
            yield CalculationRecord(
                id=hit["id"],
                text=hit["text"],
                normalized_text=hit.get("normalized_text", ""),
                value=int(hit["value"]),
                language=hit.get("language", "Unknown"),
                method=hit.get("method", "Standard Value"),
                notes=hit.get("notes", ""),
                source=hit.get("source", ""),
                tags=tags,
                breakdown=hit.get("breakdown", ""),
                character_count=int(hit.get("character_count", 0)),
                user_rating=int(hit.get("user_rating", 0)),
                is_favorite=bool(hit.get("is_favorite", False)),
                category=hit.get("category", ""),
                related_ids=related_ids,
                date_created=date_created,
                date_modified=date_modified,
            )


def migrate(index_dir: Path) -> None:
    """Run the migration."""
    init_db()
    repo = SQLiteCalculationRepository()
    total = 0
    for record in load_whoosh_records(index_dir):
        repo.save(record)
        total += 1
    print(f"Imported {total} calculations into SQLite")


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate gematria calculations from Whoosh to SQLite.")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX, help="Path to the legacy Whoosh index directory")
    args = parser.parse_args()
    migrate(args.index)


if __name__ == "__main__":
    main()
