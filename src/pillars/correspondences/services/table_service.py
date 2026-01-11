"""
Table Service - The Steward of the Tablets.
Service layer mediating between UI and TableRepository for correspondence table operations.
"""
from sqlalchemy.orm import Session
from pillars.correspondences.repos.table_repository import TableRepository
from pillars.correspondences.models.correspondence_models import CorrespondenceTable
from typing import List, Optional, Dict, Any

class TableService:
    """
    The Steward of the Tablets.
     mediates between the Realm of Form (UI) and the Memory (Repository).
    """

    def __init__(self, session: Session):
        """
          init   logic.
        
        Args:
            session: Description of session.
        
        """
        self.session = session
        self.repo = TableRepository(session)

    def create_table(self, name: str, content: Dict[str, Any]) -> CorrespondenceTable:
        """Create a new correspondence table."""
        return self.repo.create(name, content)

    def list_tables(self) -> List[CorrespondenceTable]:
        """Retrieve all scrolls from the library."""
        return self.repo.get_all()

    def get_table(self, table_id: str) -> Optional[CorrespondenceTable]:
        """Retrieve a specific scroll."""
        return self.repo.get_by_id(table_id)

    def save_content(self, table_id: str, content: Dict[str, Any]) -> Optional[CorrespondenceTable]:
        """Update the content of a scroll."""
        return self.repo.update_content(table_id, content)

    def rename_table(self, table_id: str, new_name: str) -> Optional[CorrespondenceTable]:
        """Rename a scroll."""
        return self.repo.update_name(table_id, new_name)

    def destroy_table(self, table_id: str):
        """Destroy a scroll forever."""
        self.repo.delete(table_id)