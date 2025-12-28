"""Image extraction utilities for document processing."""
import re
import base64
import hashlib
from typing import List, Tuple, Callable


# Pattern to match base64 image data in src attributes while preserving other attributes
# Captures: prefix (before src value), mime, data, suffix (after src value)
SAFE_EXTRACT_PATTERN = re.compile(
    r'(?P<prefix><img\s+[^>]*?src=["\'])data:image/(?P<mime>[^;]+).*?;base64,(?P<data>[^"\']+)(?P<suffix>["\'][^>]*>)',
    re.IGNORECASE | re.DOTALL
)

# Pattern to restore images from docimg:// ids
SAFE_RESTORE_PATTERN = re.compile(
    r'(?P<prefix><img\s+[^>]*?src=["\'])docimg:///*(?P<id>\d+)(?P<suffix>["\'][^>]*>)',
    re.IGNORECASE
)


def extract_images_from_html(
    html: str,
    store_callback: Callable[[bytes, str], int]
) -> Tuple[str, List[dict]]:
    """
    Extract base64 images from HTML and replace with docimg:// references.
    Preserves all other HTML attributes (alt, class, style, etc).
    Includes deduplication via MD5 hashing.
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
        mime_subtype = match.group('mime')
        base64_data = match.group('data')
        suffix = match.group('suffix')
        
        # Decode base64 to bytes
        try:
            image_bytes = base64.b64decode(base64_data)
        except Exception as e:
            print(f"Failed to decode base64 image: {e}")
            return match.group(0)
        
        # Deduplication check
        img_hash = hashlib.md5(image_bytes).hexdigest()
        
        if img_hash in seen_hashes:
            image_id = seen_hashes[img_hash]
            is_new = False
        else:
            mime_type = f"image/{mime_subtype}"
            try:
                image_id = store_callback(image_bytes, mime_type)
                seen_hashes[img_hash] = image_id
                is_new = True
            except Exception as e:
                print(f"Failed to store image: {e}")
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
                mime_subtype = mime_type.split('/')[1]
            else:
                mime_subtype = mime_type
                
            return f'{prefix}data:image/{mime_subtype};base64,{base64_data}{suffix}'
            
        except Exception as e:
            print(f"Failed to fetch image {image_id_str}: {e}")
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