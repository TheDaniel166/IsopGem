import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

from shared.database import init_db, SessionLocal
from pillars.gematria.repositories.sqlite_calculation_repository import SQLiteCalculationRepository
from pillars.gematria.models import CalculationRecord

def run_rite():
    print("Beginning the Rite of Search...")
    init_db()
    repo = SQLiteCalculationRepository(SessionLocal)
    
    # Create test data
    test_id = "test-search-ritual"
    record = CalculationRecord(
        id=test_id,
        text="The Philosophers Stone",
        value=1000,
        method="English",
        language="English",
        notes="A legendary alchemical substance."
    )
    repo.save(record)
    print("Test record inscribed.")
    
    try:
        # Test 1: General (Contains)
        results = repo.search(query_str="Philosophers", search_mode="General")
        assert any(r.id == test_id for r in results), "General search failed to find 'Philosophers'"
        print("[✓] General Search: Verified")
        
        # Test 2: Exact
        results = repo.search(query_str="The Philosophers Stone", search_mode="Exact")
        assert any(r.id == test_id for r in results), "Exact search failed"
        results_fail = repo.search(query_str="Philosophers", search_mode="Exact")
        assert not any(r.id == test_id for r in results_fail), "Exact search matched partial string incorrectly"
        print("[✓] Exact Search: Verified")
        
        # Test 3: Wildcard (LIKE)
        results = repo.search(query_str="%Philo%Stone", search_mode="Wildcard")
        assert any(r.id == test_id for r in results), "Wildcard search failed"
        print("[✓] Wildcard Search: Verified")
        
        # Test 4: Regex
        # Find 'Stone' at the end
        results = repo.search(query_str="Stone$", search_mode="Regex")
        assert any(r.id == test_id for r in results), "Regex search failed to find end anchor"
        # Find 'The' at start
        results = repo.search(query_str="^The", search_mode="Regex")
        assert any(r.id == test_id for r in results), "Regex search failed to find start anchor"
        print("[✓] Regex Search: Verified")
        
    finally:
        repo.delete(test_id)
        print("Test record expunged.")

if __name__ == "__main__":
    try:
        run_rite()
        print("The Rite of Search is complete. The Eye sees all.")
    except Exception as e:
        print(f"The Rite Failed: {e}")
        sys.exit(1)
