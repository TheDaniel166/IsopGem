"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: GRANDFATHERED - Unclear if infrastructure or pillar
- USED BY: Document_manager (2 references)
- CRITERION: 2 (if global) OR Violation (if pillar-specific)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""


"""Image extraction utilities for document processing."""
import re
import base64
import hashlib
import logging
import mimetypes
from typing import List, Tuple, Callable

# Configure logger
logger = logging.getLogger(__name__)

MAX_IMG_SIZE = 20 * 1024 * 1024  # 20MB limit for base64 data
ALLOWED_MIME_SUBTYPES = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}


# Pattern to match base64 image data in src attributes while preserving other attributes
# Captures: prefix (before src value), mime, data, suffix (after src value)
# Improved allows attributes before src
SAFE_EXTRACT_PATTERN = re.compile(
    r'(?P<prefix><img\b(?=[^>]*?\bsrc=["\']data:image/)(?:[^>]+?)\bsrc=["\'])'
    r'data:image/(?P<mime>[^;]+).*?;base64,(?P<data>[^"\']+)'
    r'(?P<suffix>["\'][^>]*>)',
    re.IGNORECASE | re.DOTALL
)

# Pattern to restore images from docimg:// ids (tolerant of attribute order/spacing/newlines)
SAFE_RESTORE_PATTERN = re.compile(
    r'(?P<prefix><img\b(?=[^>]*?\bsrc=["\']docimg://)(?:[^>]+?)\bsrc=["\'])'
    r'docimg:///*(?P<id>\d+)'
    r'(?P<suffix>["\'][^>]*>)',
    re.IGNORECASE | re.DOTALL
)


def extract_images_from_html(
    html: str,
    store_callback: Callable[[bytes, str], int]
) -> Tuple[str, List[dict]]:
    """
    Extract base64 images from HTML and replace with docimg:// references.
    Preserves all other HTML attributes (alt, class, style, etc).
    Includes deduplication via SHA-256 hashing.
    """
    images_info = []
    seen_hashes = {}  # Map hash -> image_id
    
    def replace_image(match):
        """
        Replace image logic.
        
        Args:
            match: Description of match.
        
        """
        prefix = match.group('prefix')
        mime_subtype = match.group('mime').lower()
        base64_data = match.group('data')
        cleaned_data = re.sub(r"\s+", "", base64_data)
        suffix = match.group('suffix')

        if mime_subtype not in ALLOWED_MIME_SUBTYPES:
            logger.warning("Blocked unsupported image mime subtype: %s", mime_subtype)
            return match.group(0)
        
        if len(base64_data) > (MAX_IMG_SIZE * 1.33):
            logger.warning("Image too large, skipping extraction")
            return match.group(0)

        # Decode base64 to bytes
        try:
            image_bytes = base64.b64decode(cleaned_data, validate=True)
        except Exception as e:
            logger.error(f"Failed to decode base64 image: {e}")
            return match.group(0)

        if len(image_bytes) > MAX_IMG_SIZE:
            logger.warning("Decoded image exceeds size cap; skipping extraction")
            return match.group(0)
        
        # Deduplication check
        img_hash = hashlib.sha256(image_bytes).hexdigest()
        
        if img_hash in seen_hashes:
            image_id = seen_hashes[img_hash]
            is_new = False
        else:
            # Use mimetypes to normalize if needed, though we get subtype from regex
            mime_type = f"image/{mime_subtype}"
            try:
                image_id = store_callback(image_bytes, mime_type)
                seen_hashes[img_hash] = image_id
                is_new = True
            except Exception as e:
                logger.error(f"Failed to store image: {e}")
                return match.group(0)
        
        if is_new:
            images_info.append({
                'id': image_id,
                'mime_type': f"image/{mime_subtype}",
                'size': len(image_bytes),
                'hash': img_hash
            })
            
        # Reconstruct tag preserving original attributes
        return f'{prefix}docimg://{image_id}{suffix}'
    
    modified_html = SAFE_EXTRACT_PATTERN.sub(replace_image, html)
    
    return modified_html, images_info


def restore_images_in_html(
    html: str,
    fetch_callback: Callable[[int], Tuple[bytes, str]]
) -> str:
    """
    Replace docimg:// references with actual base64 data for display.
    Preserves all other HTML attributes.
    """
    def replace_docimg(match):
        """
        Replace docimg logic.
        
        Args:
            match: Description of match.
        
        """
        prefix = match.group('prefix')
        image_id_str = match.group('id')
        suffix = match.group('suffix')
        
        try:
            image_id = int(image_id_str)
            image_bytes, mime_type = fetch_callback(image_id)
            
            if not image_bytes:
                return match.group(0)

            base64_data = base64.b64encode(image_bytes).decode('utf-8')
            
            # Extract mime subtype (handle cases like "image/png" vs "png")
            if '/' in mime_type:
                mime_subtype = mime_type.split('/')[1].lower()
            else:
                mime_subtype = mime_type.lower()

            if mime_subtype not in ALLOWED_MIME_SUBTYPES:
                logger.warning("Blocked unsupported image mime subtype during restore: %s", mime_subtype)
                return match.group(0)
                
            return f'{prefix}data:image/{mime_subtype};base64,{base64_data}{suffix}'
            
        except Exception as e:
            logger.error(f"Failed to fetch image {image_id_str}: {e}")
            return match.group(0)
    
    return SAFE_RESTORE_PATTERN.sub(replace_docimg, html)


def has_embedded_images(html: str) -> bool:
    """Check if HTML contains embedded base64 images."""
    return bool(SAFE_EXTRACT_PATTERN.search(html))


def has_docimg_references(html: str) -> bool:
    """Check if HTML contains docimg:// references."""
    return bool(SAFE_RESTORE_PATTERN.search(html))


def count_embedded_images(html: str) -> int:
    """Count the number of embedded base64 images in HTML."""
    return len(SAFE_EXTRACT_PATTERN.findall(html))