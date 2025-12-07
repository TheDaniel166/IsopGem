import json
from typing import Dict, List, Optional

import pytest

from pillars.gematria.models.calculation_record import CalculationRecord
from pillars.gematria.services.base_calculator import GematriaCalculator
from pillars.gematria.services.calculation_service import CalculationService


class DummyCalculator(GematriaCalculator):
    def _initialize_mapping(self) -> Dict[str, int]:
        return {"A": 1, "B": 2, "C": 3}

    @property
    def name(self) -> str:
        return "Dummy"


class FakeCalculationRepository:
    def __init__(self):
        self.records: Dict[str, CalculationRecord] = {}

    def save(self, record: CalculationRecord) -> CalculationRecord:
        if not record.id:
            record.id = f"record-{len(self.records) + 1}"
        self.records[record.id] = record
        return record

    def get_by_id(self, record_id: str) -> Optional[CalculationRecord]:
        return self.records.get(record_id)

    def delete(self, record_id: str) -> bool:
        return bool(self.records.pop(record_id, None))

    def search(self, **kwargs) -> List[CalculationRecord]:
        return list(self.records.values())

    def get_all(self, limit: int = 1000) -> List[CalculationRecord]:
        return self.search()

    def get_by_value(self, value: int) -> List[CalculationRecord]:
        return [r for r in self.records.values() if r.value == value]

    def get_favorites(self) -> List[CalculationRecord]:
        return [r for r in self.records.values() if r.is_favorite]


@pytest.fixture
def repo_and_service():
    repo = FakeCalculationRepository()
    service = CalculationService(repository=repo)
    return service, repo


def test_save_calculation_serializes_breakdown(repo_and_service):
    service, repo = repo_and_service
    calculator = DummyCalculator()

    record = service.save_calculation(
        text="AB",
        value=3,
        calculator=calculator,
        breakdown=[("A", 1), ("B", 2)],
        notes="note",
        tags=["tag"],
    )

    saved = repo.records[record.id]
    assert saved.language == calculator.name
    assert json.loads(saved.breakdown) == [
        {"char": "A", "value": 1},
        {"char": "B", "value": 2},
    ]
    assert saved.normalized_text == calculator.normalize_text("AB")


def test_update_calculation_only_changes_provided_fields(repo_and_service):
    service, repo = repo_and_service
    calculator = DummyCalculator()

    original = service.save_calculation(
        text="ABC",
        value=6,
        calculator=calculator,
        breakdown=[("A", 1), ("B", 2), ("C", 3)],
    )

    updated = service.update_calculation(
        record_id=original.id,
        notes="updated",
        tags=["alpha", "beta"],
        user_rating=4,
    )

    assert updated is not None
    assert updated.notes == "updated"
    assert updated.tags == ["alpha", "beta"]
    assert updated.user_rating == 4
    assert repo.records[original.id].tags == ["alpha", "beta"]


def test_toggle_favorite_flips_state(repo_and_service):
    service, repo = repo_and_service
    calculator = DummyCalculator()

    record = service.save_calculation(
        text="B",
        value=2,
        calculator=calculator,
        breakdown=[("B", 2)],
    )

    first_toggle = service.toggle_favorite(record.id)
    assert first_toggle is not None
    assert first_toggle.is_favorite

    second_toggle = service.toggle_favorite(record.id)
    assert second_toggle is not None
    assert not second_toggle.is_favorite


def test_get_breakdown_from_record_handles_malformed_json(repo_and_service):
    service, repo = repo_and_service
    record = CalculationRecord(
        text="C",
        value=3,
        language="Dummy",
        method="Standard",
        breakdown="[not valid json]",
    )

    assert service.get_breakdown_from_record(record) == []
