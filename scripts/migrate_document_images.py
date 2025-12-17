#!/usr/bin/env python3
"""
Migration script to extract embedded images from existing documents.

This script:
1. Creates the document_images table if it doesn't exist
2. Scans all documents for embedded base64 images
3. Extracts images to the document_images table
4. Updates raw_content with docimg:// references

Run from the project root:
    python scripts/migrate_document_images.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shared.database import engine, Base, get_db_session
from pillars.document_manager.models.document import Document, DocumentImage
from pillars.document_manager.repositories.image_repository import ImageRepository
from pillars.document_manager.utils.image_utils import (
    extract_images_from_html,
    has_embedded_images,
    count_embedded_images
)


def create_tables():
    """Ensure the document_images table exists."""
    print("Creating document_images table if needed...")
    Base.metadata.create_all(bind=engine)
    print("Done.")


def migrate_document(doc, image_repo, db):
    """Migrate a single document's images."""
    if not doc.raw_content:
        return 0, 0
    
    if not has_embedded_images(doc.raw_content):
        return 0, 0
    
    image_count = count_embedded_images(doc.raw_content)
    print(f"  Document {doc.id} '{doc.title[:40]}...' has {image_count} embedded images")
    
    original_size = len(doc.raw_content)
    
    def store_image(image_bytes, mime_type):
        img = image_repo.create(
            document_id=doc.id,
            data=image_bytes,
            mime_type=mime_type
        )
        return img.id
    
    # Extract images
    modified_html, images_info = extract_images_from_html(doc.raw_content, store_image)
    
    if images_info:
        # Update document
        doc.raw_content = modified_html
        db.commit()
        
        new_size = len(modified_html)
        saved = original_size - new_size
        print(f"    Extracted {len(images_info)} images, saved {saved:,} bytes ({saved/1024/1024:.1f} MB)")
        return len(images_info), saved
    
    return 0, 0


def migrate_all():
    """Migrate all documents with embedded images."""
    print("\n=== Document Image Migration ===\n")
    
    # First, create tables
    create_tables()
    
    print("\nScanning documents for embedded images...\n")
    
    total_images = 0
    total_saved = 0
    docs_processed = 0
    
    with get_db_session() as db:
        image_repo = ImageRepository(db)
        
        # Get all documents
        docs = db.query(Document).all()
        print(f"Found {len(docs)} documents to scan.\n")
        
        for doc in docs:
            try:
                images, saved = migrate_document(doc, image_repo, db)
                if images > 0:
                    total_images += images
                    total_saved += saved
                    docs_processed += 1
            except Exception as e:
                print(f"  ERROR processing document {doc.id}: {e}")
                db.rollback()
    
    print(f"\n=== Migration Complete ===")
    print(f"Documents processed: {docs_processed}")
    print(f"Images extracted: {total_images}")
    print(f"Space saved: {total_saved:,} bytes ({total_saved/1024/1024:.1f} MB)")


if __name__ == "__main__":
    migrate_all()
