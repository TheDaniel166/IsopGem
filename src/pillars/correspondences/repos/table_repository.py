from sqlalchemy.orm import Session
from pillars.correspondences.models.correspondence_models import CorrespondenceTable
from typing import List, Optional
from datetime import datetime

class TableRepository:
    """
    Guardian of the Emerald Tablets.
    Handles CRUD operations for Correspondence Tables.
    """
    def __init__(self, session: Session):
        self.session = session

    def create(self, name: str, content: dict) -> CorrespondenceTable:
        """Create a new table."""
        table = CorrespondenceTable(name=name, content=content)
        self.session.add(table)
        self.session.commit()
        self.session.refresh(table)
        return table

    def get_all(self) -> List[CorrespondenceTable]:
        """List all tables."""
        return self.session.query(CorrespondenceTable).all()

    def get_by_id(self, table_id: str) -> Optional[CorrespondenceTable]:
        """Retrieve a specific table."""
        return self.session.query(CorrespondenceTable).filter(CorrespondenceTable.id == table_id).first()

    def update(self, table: CorrespondenceTable) -> CorrespondenceTable:
        """Save changes to a table."""
        table.updated_at = datetime.utcnow()
        self.session.merge(table)
        self.session.commit()
        self.session.refresh(table)
        return table

    def delete(self, table_id: str):
        """Destroy a table."""
        table = self.get_by_id(table_id)
        if table:
            self.session.delete(table)
            self.session.commit()

    def update_content(self, table_id: str, content: dict):
        """Update just the content of a table."""
        table = self.get_by_id(table_id)
        if table:
            table.content = content
            table.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(table)
            return table
        return None

    def update_name(self, table_id: str, new_name: str):
        """Rename a table."""
        table = self.get_by_id(table_id)
        if table:
            table.name = new_name
            table.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(table)
            return table
        return None
