
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "src"))

from shared.database import get_db_session
from pillars.document_manager.services.document_service import DocumentService
from pillars.document_manager.models.document import DocumentImage

def test_database_manager():
    print("Starting Database Manager Verification...")
    
    with get_db_session() as db:
        service = DocumentService(db)
        
        # 1. Initial Stats
        initial_stats = service.get_database_stats()
        print(f"Initial Stats: {initial_stats}")
        
        # 2. Create a Document with a used image and an orphan image
        print("\nCreating test data...")
        
        # Create Dummy Image 1 (Used)
        img1 = DocumentImage(
            hash="test_hash_1",
            data=b"fake_image_data_1",
            mime_type="image/png"
        )
        db.add(img1)
        db.flush() # get ID
        
        # Create Dummy Image 2 (Orphan)
        img2 = DocumentImage(
            hash="test_hash_2",
            data=b"fake_image_data_2",
            mime_type="image/png"
        )
        db.add(img2)
        db.flush()
        
        # Create Document using img1 but NOT img2
        doc = service.repo.create(
            title="Test Doc for Database Manager",
            content="Text content",
            file_type="txt",
            raw_content=f"<p>Test <img src='docimg://{img1.id}'></p>"
        )
        
        img1.document_id = doc.id
        img2.document_id = doc.id # Technically associated via FK, but not in HTML
        db.commit()
        
        print(f"Created Doc ID: {doc.id}, Used Img ID: {img1.id}, Orphan Img ID: {img2.id}")
        
        # 3. Verify Stats Update
        new_stats = service.get_database_stats()
        print(f"New Stats: {new_stats}")
        assert new_stats['document_count'] == initial_stats['document_count'] + 1
        assert new_stats['image_count'] == initial_stats['image_count'] + 2
        
        # 4. Test Dry Run Cleanup
        print("\nTesting Orphan Cleanup (Dry Run)...")
        results_dry = service.cleanup_orphans(dry_run=True)
        print(f"Dry Run Results: {results_dry}")
        
        assert results_dry['orphan_count'] >= 1
        assert results_dry['deleted_count'] == 0
        
        # 5. Test Actual Cleanup
        print("\nTesting Orphan Cleanup (Execution)...")
        results_exec = service.cleanup_orphans(dry_run=False)
        print(f"Execution Results: {results_exec}")
        
        assert results_exec['deleted_count'] >= 1
        
        # 6. Verify Results
        # Img1 should exist
        assert service.get_image(img1.id) is not None, "Used image was incorrectly deleted!"
        # Img2 should be gone
        assert service.get_image(img2.id) is None, "Orphan image was not deleted!"
        
        # Cleanup Document
        service.delete_document(doc.id)
        # Verify Img1 is cascaded deleted (standard behavior) or manual cleanup?
        # The schema has cascade="all, delete-orphan", so deleting doc should delete img1
        # providing img1 is in doc.images list. 
        # But we added manually. Let's check.
        
        print("\nTest passed successfully!")

if __name__ == "__main__":
    try:
        test_database_manager()
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()
