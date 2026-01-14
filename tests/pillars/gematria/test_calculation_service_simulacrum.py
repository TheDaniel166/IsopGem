"""
The Discipline of the Simulacrum: Proof of Concept.
Tests for CalculationService adhering strictly to the 12 Rules of Mocking.
"""
import json
import pytest
import unittest.mock as mock
from datetime import datetime
from pillars.gematria.services.calculation_service import CalculationService
from pillars.gematria.repositories import CalculationRepository
from pillars.gematria.models import CalculationRecord
from shared.services.gematria.base_calculator import GematriaCalculator

# Rule 11: Pytest + Fixtures = Sanity
@pytest.fixture
def mock_repo():
    # Rule 5: Use spec or autospec aggressively
    # We mock the boundary (Repository), not internal helpers.
    return mock.create_autospec(CalculationRepository, instance=True)

@pytest.fixture
def mock_calculator():
    # Rule 1: Mock heavy subsystems or external logic
    calc = mock.create_autospec(GematriaCalculator, instance=True)
    calc.name = "TestCipher"
    # Setup default behavior for strict typing if needed
    calc.normalize_text.return_value = "NORMALIZED"
    return calc

@pytest.fixture
def service(mock_repo):
    # Rule 4: Dependency Injection over patching
    return CalculationService(repository=mock_repo)

# Rule 7: Freeze the River of Time
@pytest.fixture
def fixed_time():
    return datetime(2023, 1, 1, 12, 0, 0)

def test_save_calculation_persistence_interaction(service, mock_repo, mock_calculator):
    """
    Test that save_calculation delegates persistence to the repository.
    Rule 6: One assertion of interaction.
    """
    # Arrange
    text = "The Law"
    value = 93
    breakdown = [("T", 20), ("h", 8), ("e", 5)]
    
    # Setup mock return (Constraint)
    expected_record = CalculationRecord(text=text, value=value, language="Test", method="Test")
    mock_repo.save.return_value = expected_record

    # Act
    result = service.save_calculation(
        text=text,
        value=value,
        calculator=mock_calculator,
        breakdown=breakdown
    )

    # Assert
    # Rule 6: Assertion of Effect
    assert result == expected_record
    
    # Rule 6: Assertion of Interaction (Detailed check)
    mock_repo.save.assert_called_once()
    
    # Verify the object passed to save is correct (Logic check)
    # We use call_args to inspect the argument without brittle "assert_called_with" on every field
    args, _ = mock_repo.save.call_args
    saved_record = args[0]
    
    assert saved_record.text == text
    assert saved_record.value == value
    assert saved_record.breakdown is not None
    
    # Test serialization logic, not formatting
    breakdown_data = json.loads(saved_record.breakdown)
    expected_data = [
        {"char": "T", "value": 20},
        {"char": "h", "value": 8},
        {"char": "e", "value": 5}
    ]
    assert breakdown_data == expected_data

def test_get_calculation_delegation(service, mock_repo):
    """
    Test simple delegation for get_calculation.
    """
    # Arrange
    record_id = "test-uuid"
    expected = CalculationRecord(text="Test", value=1, language="Test", method="Test")
    mock_repo.get_by_id.return_value = expected

    # Act
    result = service.get_calculation(record_id)

    # Assert
    assert result == expected
    mock_repo.get_by_id.assert_called_once_with(record_id)

def test_update_calculation_timestamps(mock_repo, fixed_time):
    """
    Test that update_calculation updates the timestamp.
    Rule 7: Freeze the River of Time (using Clock injection, not patching).
    Rule 4: Dependency Injection over Patching.
    """
    from shared.services.time import FixedClock
    
    # Arrange
    record_id = "existing-id"
    existing_record = CalculationRecord(text="Old", value=1, language="Test", method="Test", date_modified=datetime(2000, 1, 1))
    mock_repo.get_by_id.return_value = existing_record
    mock_repo.save.return_value = existing_record # Return the mutated object

    # Inject a FixedClock instead of patching
    clock = FixedClock(fixed_time)
    service = CalculationService(repository=mock_repo, clock=clock)
    
    # Act
    result = service.update_calculation(record_id, notes="New Note")

    # Assert
    assert result is not None
    assert result.notes == "New Note"
    assert result.date_modified == fixed_time
    mock_repo.save.assert_called_once_with(existing_record)

def test_delete_calculations_not_found(service, mock_repo):
    """Test delete returns False when repo returns False."""
    mock_repo.delete.return_value = False
    assert service.delete_calculation("missing") is False

def test_breakdown_parsing_logic(service):
    """
    Test logic inside service (Rule 8: Fakes/Logic tests).
    This doesn't need a mock repository because it's pure logic method.
    """
    # Arrange
    json_data = '[{"char": "A", "value": 1}, ["B", 2]]'
    record = CalculationRecord(text="Test", value=3, language="Test", method="Test", breakdown=json_data)

    # Act
    result = service.get_breakdown_from_record(record)

    # Assert
    expected = [("A", 1), ("B", 2)]
    assert result == expected

def test_breakdown_parsing_robustness(service):
    """Test handling of malformed JSON."""
    record = CalculationRecord(text="Test", value=0, language="Test", method="Test", breakdown="{invalid}")
    result = service.get_breakdown_from_record(record)
    assert result == []
