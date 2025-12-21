"""
Verification script for Document Database Manager logic.
Tests:
1. get_database_stats()
2. cleanup_orphans()
"""
import sys
import os
import logging

# Add project root to path
sys.path.append(os.getcwd())

from src.shared.database import get_db_session
from src.pillars.document_manager.services.document_service import DocumentService
from src.pillars.document_manager.models.document import Document, DocumentImage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_db_manager():
    print("Starting Database Manager Verification...")
    
    with get_db_session() as db:
        service = DocumentService(db)
        
        # 1. Check initial stats
        initial_stats = service.get_database_stats()
        print(f"Initial Stats: {initial_stats}")
        
        # 2. Create a test document with images
        print("\nCreating test document with images...")
        img_data = b"fake_image_data"
        
        # Create doc manually to control ID and content easily
        doc = Document(
            title="Test Orphan Doc",
            content="Text content",
            file_type="txt",
            raw_content="<p>Image 1: docimg://PLACEHOLDER_1</p><p>Image 2: docimg://PLACEHOLDER_2</p>"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # Add 2 images
        img1 = DocumentImage(document_id=doc.id, data=img_data, mime_type="image/png")
        img2 = DocumentImage(document_id=doc.id, data=img_data, mime_type="image/png")
        db.add(img1)
        db.add(img2)
        db.commit()
        db.refresh(img1)
        db.refresh(img2)
        
        # Update content with real IDs
        doc.raw_content = f"<p>Image 1: docimg://{img1.id}</p><p>Image 2: docimg://{img2.id}</p>"
        db.commit()
        
        print(f"Created Doc ID: {doc.id}, Image IDs: {img1.id}, {img2.id}")
        
        # 3. Verify Stats updated
        new_stats = service.get_database_stats()
        print(f"Updated Stats: {new_stats}")
        assert new_stats['document_count'] == initial_stats['document_count'] + 1
        assert new_stats['image_count'] == initial_stats['image_count'] + 2
        
        # 4. Create an Orphan
        print("\nSimulating orphan creation (deleting reference to Image 2 from content)...")
        # Remove reference to img2 from content, but keep img2 in DB
        doc.raw_content = f"<p>Image 1: docimg://{img1.id}</p>"
        db.commit()
        
        # 5. Run Cleanup (Dry Run)
        print("Running cleanup (Dry Run)...")
        dry_result = service.cleanup_orphans(dry_run=True)
        print(f"Dry Run Result: {dry_result}")
        
        assert dry_result['orphan_count'] >= 1
        # Check if our specific image is counted (might be other orphans in the DB)
        
        # 6. Run Cleanup (Real)
        print("Running cleanup (Real)...")
        real_result = service.cleanup_orphans(dry_run=False)
        print(f"Cleanup Result: {real_result}")
        
        assert real_result['deleted_count'] >= 1
        
        # Verify Image 2 is gone
        deleted_img = db.query(DocumentImage).filter(DocumentImage.id == img2.id).first()
        assert deleted_img is None, "Image 2 should have been deleted"
        
        # Verify Image 1 is still there
        kept_img = db.query(DocumentImage).filter(DocumentImage.id == img1.id).first()
        assert kept_img is not None, "Image 1 should still exist"
        
        print("\nCleanup verified successfully.")
        
        # Cleanup test document
        print("Cleaning up test data...")
        service.delete_document(doc.id)
        
        final_stats = service.get_database_stats()
        print(f"Final Stats: {final_stats}")
        
        # Should be back to initial (or close, if other background things happened)
        # Note: 'initial' + created/deleted might vary if other tests run, but doc count should match
        assert final_stats['document_count'] == initial_stats['document_count']

if __name__ == "__main__":
    try:
        verify_db_manager()
        print("\n✅ VERIFICATION PASSED")
    except AssertionError as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ VERIFICATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
