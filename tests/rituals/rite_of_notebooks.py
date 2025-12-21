import sys
from sqlalchemy.orm import Session
from shared.database import get_db_session
from pillars.document_manager.services.notebook_service import NotebookService

def RiteOfNotebooks():
    print("Beginning Rite of Notebooks...")
    
    with get_db_session() as db:
        svc = NotebookService(db)
        
        suffix = "_RITE"
        
        # 1. Create Notebook
        nb = svc.create_notebook(title=f"Grimoire{suffix}")
        assert nb.id is not None
        print(f"Created Notebook: {nb.title} (ID: {nb.id})")
        
        # 2. Create Section
        sec = svc.create_section(nb.id, title="Spells")
        assert sec.id is not None
        assert sec.notebook_id == nb.id
        print(f"Created Section: {sec.title} (ID: {sec.id})")
        
        # 3. Create Page (Document)
        page = svc.create_page(sec.id, title="Fireball")
        assert page.id is not None
        assert page.section_id == sec.id
        print(f"Created Page: {page.title} (ID: {page.id})")
        
        # 4. Verify Hierarchy Reading
        notebooks = svc.get_notebooks_with_structure()
        found_nb = next((n for n in notebooks if n.id == nb.id), None)
        assert found_nb is not None
        
        found_sec = next((s for s in found_nb.sections if s.id == sec.id), None)
        assert found_sec is not None
        
        # Eager loading test? 
        # get_notebooks_with_structure eagerly loads sections.
        # But does it load pages?
        # My implementation only joined sections.
        # Let's check if pages are accessible (lazy load works generally).
        pages = svc.get_section_pages(sec.id)
        assert any(p.id == page.id for p in pages)
        print("Hierarchy verified.")
        
        # 5. Move Page
        sec2 = svc.create_section(nb.id, title="Potions")
        svc.move_page(page.id, sec2.id)
        
        pages_old = svc.get_section_pages(sec.id)
        assert not any(p.id == page.id for p in pages_old)
        
        pages_new = svc.get_section_pages(sec2.id)
        assert any(p.id == page.id for p in pages_new)
        print("Move verified.")
        
        # Cleanup
        # If I delete notebook, it should cascade delete sections.
        # But documents? 'relationship' on Section has no cascade, likely.
        # Document.section relies on FK. 
        # If I want cascade delete of docs, I need to configure it in model.
        # Code: pages = relationship("Document", backref="section", order_by="Document.id") 
        # No cascade specified. Usually safer NOT to cascade delete docs unless explicit.
        # But for 'Notebook' concept, deleting a section usually deletes pages.
        # For now, I'll delete manually or leave them (orphaned).
        # Let's manual clean.
        svc.db.delete(page)
        svc.delete_section(sec.id) # Already empty
        svc.delete_section(sec2.id) # Should be empty now
        svc.delete_notebook(nb.id)
        
        print("Rite Complete.")

if __name__ == "__main__":
    RiteOfNotebooks()
