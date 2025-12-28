"""Repository for DocumentImage model."""
import hashlib
import zlib
from typing import List, Optional
from sqlalchemy.orm import Session
from shared.models.document_manager.document import DocumentImage


class ImageRepository:
    """Repository for managing document images."""
    
    def __init__(self, db: Session):
        """
          init   logic.
        
        Args:
            db: Description of db.
        
        """
        self.db = db

    def get(self, image_id: int) -> Optional[DocumentImage]:
        """Get an image by ID."""
        return self.db.query(DocumentImage).filter(DocumentImage.id == image_id).first()

    def get_by_document(self, document_id: int) -> List[DocumentImage]:
        """Get all images for a document."""
        return self.db.query(DocumentImage).filter(
            DocumentImage.document_id == document_id
        ).all()

    def get_by_hash(self, document_id: int, hash: str) -> Optional[DocumentImage]:
        """Get an image by hash within a document (for deduplication)."""
        return self.db.query(DocumentImage).filter(
            DocumentImage.document_id == document_id,
            DocumentImage.hash == hash
        ).first()

    def create(
        self,
        document_id: int,
        data: bytes,
        mime_type: str,
        original_filename: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        compress: bool = True
    ) -> DocumentImage:
        """
        Create a new image entry.
        
        Args:
            document_id: ID of the parent document
            data: Raw image binary data
            mime_type: MIME type (e.g., 'image/png')
            original_filename: Optional original filename
            width: Optional image width
            height: Optional image height
            compress: Whether to compress the data (default True)
            
        Returns:
            The created DocumentImage
        """
        # Calculate hash for deduplication
        hash = hashlib.sha256(data).hexdigest()
        
        # Check if this exact image already exists for this document
        existing = self.get_by_hash(document_id, hash)
        if existing:
            return existing
        
        # Compress if requested
        if compress:
            data = zlib.compress(data, level=6)
        
        image = DocumentImage(
            document_id=document_id,
            hash=hash,
            data=data,
            mime_type=mime_type,
            original_filename=original_filename,
            width=width,
            height=height
        )
        self.db.add(image)
        self.db.flush()  # Get the ID without committing
        return image

    def get_decompressed_data(self, image: DocumentImage) -> bytes:
        """Get decompressed image data."""
        try:
            return zlib.decompress(image.data)
        except zlib.error:
            # Data wasn't compressed
            return image.data

    def delete_by_document(self, document_id: int) -> int:
        """Delete all images for a document."""
        count = self.db.query(DocumentImage).filter(
            DocumentImage.document_id == document_id
        ).delete()
        return count

    def delete(self, image_id: int) -> bool:
        """Delete a specific image."""
        image = self.get(image_id)
        if image:
            self.db.delete(image)
            return True
        return False