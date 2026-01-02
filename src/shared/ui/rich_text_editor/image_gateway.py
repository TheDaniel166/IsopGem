"""
Image Gateway: The Sovereign Substrate for Image Logic.

This component provides the foundational plumbing for image persistence,
resolution, and document insertion/replacement. It remains a thin layer,
delegating UX policy (dialogs, picking) to specific Features.
"""
from typing import Optional, Callable, Tuple
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QTextDocument, QImage, QTextImageFormat, QTextCursor
from PyQt6.QtCore import QUrl, QByteArray, QBuffer, QIODevice
import uuid
import logging

logger = logging.getLogger(__name__)

class ImageGateway:
    """
    Gateway for image resource management and document operations.
    
    Responsibilities:
    1. Persist image data (via saver callback)
    2. Resolve image URLs (via provider callback or cache)
    3. Register resources with the document (live cache)
    4. Provide primitives for inserting/replacing images in the text
    """
    
    def __init__(self, 
                 editor: QTextEdit,
                 resource_saver: Optional[Callable[[bytes, str], Optional[int]]] = None,
                 resource_provider: Optional[Callable[[int], Optional[Tuple[bytes, str]]]] = None):
        self.editor = editor
        self.resource_saver = resource_saver
        self.resource_provider = resource_provider

    def persist_image(self, data: bytes, mime_type: str = "PNG") -> Tuple[QUrl, str]:
        """
        Persist image data and return a canonical URL.
        
        If a resource_saver is available, uses it to get a persistent ID (docimg://<id>).
        Otherwise, falls back to an ephemeral named resource (image://<uuid>).
        """
        if self.resource_saver:
            img_id = self.resource_saver(data, mime_type)
            if img_id is not None:
                return QUrl(f"docimg://{img_id}"), f"docimg://{img_id}"
        
        # Fallback: ephemeral ID
        name = f"image://{uuid.uuid4()}"
        return QUrl(name), name

    def register_resource(self, url: QUrl, image: QImage) -> None:
        """Seed the document's resource cache so the image displays immediately."""
        doc = self.editor.document()
        if doc:
            doc.addResource(QTextDocument.ResourceType.ImageResource, url, image)

    def resolve_image(self, url: QUrl) -> Optional[QImage]:
        """
        Resolve a URL to a QImage.
        
        Checks:
        1. Document resource cache (already loaded)
        2. Resource provider (if docimg scheme)
        """
        doc = self.editor.document()
        if not doc:
            return None

        # Check internal cache first
        cached = doc.resource(QTextDocument.ResourceType.ImageResource, url)
        if isinstance(cached, QImage):
            return cached
        
        # If external provider needed
        if url.scheme() == "docimg" and self.resource_provider:
            try:
                # Parse ID from path or host (handling docimg://123 vs docimg:123)
                # Usually docimg://host/path -> we treat host/path as ID logic
                # For safety, simplistic parsing:
                img_id_str = url.toString().split("://")[-1]
                if img_id_str.isdigit():
                    img_id = int(img_id_str)
                    result = self.resource_provider(img_id)
                    if result:
                        data, _ = result
                        image = QImage()
                        image.loadFromData(data)
                        # Cache it for future
                        self.register_resource(url, image)
                        return image
            except Exception as e:
                logger.error(f"Failed to resolve docimg resource {url}: {e}")
                
        return None

    def insert_image_at_cursor(self, fmt: QTextImageFormat) -> None:
        """Insert the image format at the current cursor position."""
        cursor = self.editor.textCursor()
        cursor.insertImage(fmt)

    def replace_image_at_cursor(self, fmt: QTextImageFormat) -> None:
        """
        Replace the image at the current cursor selection.
        
        Assumes the cursor is already selecting an image or positioned at one.
        Uses insertImage which replaces selection.
        """
        cursor = self.editor.textCursor()
        # If we just have cursor at image but not selected, we might want to select it
        # But for now, assume Feature handles selection logic or cursor is ready
        cursor.insertImage(fmt)

    def get_selected_image(self) -> Tuple[Optional[QImage], Optional[str], Optional[QTextImageFormat]]:
        """
        Retrieve the image under or near the cursor.
        Returns (QImage, image_name_url, QTextImageFormat) or (None, None, None).
        """
        cursor = self.editor.textCursor()
        fmt = cursor.charFormat()
        
        # Check current position
        if not fmt.isImageFormat():
            # Check right
            temp = QTextCursor(cursor)
            temp.movePosition(QTextCursor.MoveOperation.Right)
            if temp.charFormat().isImageFormat():
                fmt = temp.charFormat()
                cursor = temp # Select that image context
            else:
                # Check left
                temp.movePosition(QTextCursor.MoveOperation.Left, n=2) # Back to start then 1 left
                if temp.charFormat().isImageFormat():
                    fmt = temp.charFormat()
                    cursor = temp
        
        if not fmt.isImageFormat():
            return None, None, None

        img_fmt = fmt.toImageFormat()
        name = img_fmt.name()
        
        # Resolve the image content
        qimg = self.resolve_image(QUrl(name))
        
        # If resolve_image fails (e.g. file path not in resource cache yet), try basic path
        if not qimg:
             doc = self.editor.document()
             if doc:
                 res = doc.resource(QTextDocument.ResourceType.ImageResource, QUrl(name))
                 if isinstance(res, QImage):
                     qimg = res
        
        return qimg, name, img_fmt

    @staticmethod
    def qimage_to_bytes(image: QImage, fmt: str = "PNG") -> bytes:
        """Helper to convert QImage to bytes."""
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, fmt)
        return byte_array.data()
