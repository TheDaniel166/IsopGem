"""
Notebook Service - The Mindscape Navigator.
Service layer for managing Notebooks, Sections, and Pages with transactional database operations.
"""
import logging
from typing import List, Optional, Iterator, Generator
from sqlalchemy.orm import Session, joinedload
from shared.database import get_db_session
from contextlib import contextmanager

from pillars.document_manager.models.notebook import Notebook, Section
from pillars.document_manager.models.document import Document
from sqlalchemy import or_
from dataclasses import dataclass

@dataclass
class SearchResult:
    page_id: int
    title: str
    snippet: str
    notebook_name: str
    section_name: str

logger = logging.getLogger(__name__)

class NotebookService:
    def __init__(self, db: Session) -> None:
        self.db = db
        
    def get_notebooks_with_structure(self) -> List[Notebook]:
        """Fetch all notebooks with sections eagerly loaded."""
        return (
            self.db.query(Notebook)
            .options(joinedload(Notebook.sections))
            .order_by(Notebook.title.asc())
            .all()
        )

    def get_notebook(self, notebook_id: int) -> Optional[Notebook]:
        return self.db.get(Notebook, notebook_id)
        
    def create_notebook(self, title: str, description: str = None) -> Notebook:
        nb = Notebook(title=title, description=description)
        self.db.add(nb)
        self.db.commit()
        self.db.refresh(nb)
        logger.info(f"Created Notebook: {title}")
        return nb
        
    def delete_notebook(self, notebook_id: int) -> None:
        nb = self.get_notebook(notebook_id)
        if nb:
            self.db.delete(nb)
            self.db.commit()
            
    def create_section(self, notebook_id: int, title: str, color: str = None) -> Section:
        section = Section(notebook_id=notebook_id, title=title, color=color)
        self.db.add(section)
        self.db.commit()
        self.db.refresh(section)
        logger.info(f"Created Section '{title}' in Notebook {notebook_id}")
        return section
        
    def delete_section(self, section_id: int) -> None:
        section = self.db.get(Section, section_id)
        if section:
            self.db.delete(section)
            self.db.commit()

    def get_section_pages(self, section_id: int) -> List[Document]:
        """Get all pages (Documents) in a section."""
        return (
            self.db.query(Document)
            .filter(Document.section_id == section_id)
            .order_by(Document.id.asc())
            .all()
        )
        
    def create_page(self, section_id: int, title: str, content: str = "", raw_content: str = "") -> Document:
        """Create a new document linked to a section."""
        doc = Document(title=title, section_id=section_id, content=content, raw_content=raw_content, file_type="html")
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        logger.info(f"Created Page '{title}' in Section {section_id}")
        return doc
        
    def move_page(self, page_id: int, new_section_id: int) -> None:
        """Move a page to a different section."""
        doc = self.db.get(Document, page_id)
        if doc:
            doc.section_id = new_section_id
            self.db.commit()
            logger.info(f"Moved Page {page_id} to Section {new_section_id}")

    def delete_page(self, page_id: int) -> None:
        """Delete a page (Document)."""
        doc = self.db.get(Document, page_id)
        if doc:
            self.db.delete(doc)
            self.db.commit()
            logger.info(f"Deleted Page {page_id}")

    # --- Renaming ---
    def rename_notebook(self, nb_id: int, new_title: str) -> None:
        nb = self.get_notebook(nb_id)
        if nb:
            nb.title = new_title
            self.db.commit()
            logger.info(f"Renamed Notebook {nb_id} to '{new_title}'")

    def rename_section(self, section_id: int, new_title: str) -> None:
        section = self.db.get(Section, section_id)
        if section:
            section.title = new_title
            self.db.commit()
            logger.info(f"Renamed Section {section_id} to '{new_title}'")

    def rename_page(self, page_id: int, new_title: str) -> None:
        doc = self.db.get(Document, page_id)
        if doc:
            doc.title = new_title
            self.db.commit()
            logger.info(f"Renamed Page {page_id} to '{new_title}'")

    def adopt_document(self, document_id: int, section_id: int) -> Document:
        """
        Adopts an existing library document into a notebook section.
        Ensures the raw_content is wrapped in Canvas JSON format.
        """
        import json
        doc = self.db.get(Document, document_id)
        if not doc:
            raise ValueError(f"Document {document_id} not found")
            
        # Update section linkage
        doc.section_id = section_id
        
        # Check if content needs wrapping for Canvas
        # Use a heuristic: if it doesn't look like JSON starting with version, wrap it
        needs_wrap = True
        if doc.raw_content and doc.raw_content.strip().startswith('{"version"'):
             needs_wrap = False
             
        if needs_wrap:
            # Wrap standard HTML/Text content into a Note Container
            content_to_wrap = doc.raw_content if doc.raw_content else doc.content
            # If still empty, use placeholder
            if not content_to_wrap: content_to_wrap = ""
            
            raw_data = {
                "version": 2,
                "items": [
                    {
                        "x": 50,
                        "y": 50,
                        "width": 800,
                        "content": content_to_wrap
                    }
                ],
                "shapes": []
            }
            doc.raw_content = json.dumps(raw_data)
            
        self.db.commit()
        self.db.refresh(doc)
        logger.info(f"Adopted Document {document_id} into Section {section_id}")
        return doc

    def search_global(self, query: str) -> List[SearchResult]:
        """
        Search across all notebooks, sections, and pages for text.
        Returns a list of SearchResult objects with context.
        """
        if not query or len(query) < 2:
            return []
            
        search_term = f"%{query}%"
        
        # Query Documents, join Sections and Notebooks
        results = (
            self.db.query(Document, Section, Notebook)
            .join(Section, Document.section_id == Section.id)
            .join(Notebook, Section.notebook_id == Notebook.id)
            .filter(
                or_(
                    Document.title.ilike(search_term),
                    # We search 'content' (extracted text) or 'raw_content' if needed. 
                    # Assuming 'content' field is best for this.
                    Document.content.ilike(search_term) 
                )
            )
            .limit(50)
            .all()
        )
        
        search_results = []
        for doc, section, notebook in results:
            snippet = ""
            # Simple snippet generation
            # TODO: Smarter snippet extraction around the match
            if doc.content:
                # Find index of match (case insensitive)
                try:
                    idx = doc.content.lower().find(query.lower())
                    if idx != -1:
                        start = max(0, idx - 20)
                        end = min(len(doc.content), idx + 60)
                        prefix = "..." if start > 0 else ""
                        suffix = "..." if end < len(doc.content) else ""
                        snippet = f"{prefix}{doc.content[start:end]}{suffix}"
                    else:
                        # Match likely in title, just show start of content
                        snippet = doc.content[:80] + "..." if len(doc.content) > 80 else doc.content
                except:
                    snippet = "..."
            
            search_results.append(SearchResult(
                page_id=doc.id,
                title=doc.title,
                snippet=snippet,
                notebook_name=notebook.title,
                section_name=section.title
            ))
            
        return search_results

@contextmanager
def notebook_service_context() -> Generator[NotebookService, None, None]:
    """Provide a transactional scope for Notebook operations."""
    with get_db_session() as db:
        yield NotebookService(db)
