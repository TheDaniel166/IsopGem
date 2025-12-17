"""Image extraction utilities for document processing."""
import re
import base64
from typing import List, Tuple, Callable


# Pattern to match base64 image data in src attributes
BASE64_IMG_PATTERN = re.compile(
    r'<img\s+[^>]*src=["\']data:image/([^;]+);base64,([^"\']+)["\'][^>]*>',
    re.IGNORECASE | re.DOTALL
)

# Pattern to match docimg:// references
DOCIMG_PATTERN = re.compile(
    r'<img\s+[^>]*src=["\']docimg://(\d+)["\'][^>]*>',
    re.IGNORECASE
)


def extract_images_from_html(
    html: str,
    store_callback: Callable[[bytes, str], int]
) -> Tuple[str, List[dict]]:
    """
    Extract base64 images from HTML and replace with docimg:// references.
    
    Args:
        html: The HTML content with embedded base64 images
        store_callback: Function that takes (image_bytes, mime_type) and returns image_id
        
    Returns:
        Tuple of (modified_html, list of image info dicts)
    """
    images_info = []
    
    def replace_image(match):
        mime_subtype = match.group(1)  # png, jpeg, gif, etc.
        base64_data = match.group(2)
        
        # Decode base64 to bytes
        try:
            image_bytes = base64.b64decode(base64_data)
        except Exception as e:
            print(f"Failed to decode base64 image: {e}")
            return match.group(0)  # Keep original if decode fails
        
        mime_type = f"image/{mime_subtype}"
        
        # Store the image and get its ID
        try:
            image_id = store_callback(image_bytes, mime_type)
        except Exception as e:
            print(f"Failed to store image: {e}")
            return match.group(0)  # Keep original if store fails
        
        images_info.append({
            'id': image_id,
            'mime_type': mime_type,
            'size': len(image_bytes)
        })
        
        # Return the img tag with docimg:// reference
        # Preserve other attributes by reconstructing
        original = match.group(0)
        
        # Try to extract width/height if present
        width_match = re.search(r'width=["\']?(\d+)', original, re.IGNORECASE)
        height_match = re.search(r'height=["\']?(\d+)', original, re.IGNORECASE)
        
        attrs = f'src="docimg://{image_id}"'
        if width_match:
            attrs += f' width="{width_match.group(1)}"'
        if height_match:
            attrs += f' height="{height_match.group(1)}"'
            
        return f'<img {attrs} />'
    
    modified_html = BASE64_IMG_PATTERN.sub(replace_image, html)
    
    return modified_html, images_info


def restore_images_in_html(
    html: str,
    fetch_callback: Callable[[int], Tuple[bytes, str]]
) -> str:
    """
    Replace docimg:// references with actual base64 data for display.
    
    Args:
        html: HTML content with docimg:// references
        fetch_callback: Function that takes image_id and returns (image_bytes, mime_type)
        
    Returns:
        HTML with base64 images restored
    """
    def replace_docimg(match):
        image_id = int(match.group(1))
        
        try:
            image_bytes, mime_type = fetch_callback(image_id)
            base64_data = base64.b64encode(image_bytes).decode('utf-8')
            
            # Extract mime subtype
            if '/' in mime_type:
                mime_subtype = mime_type.split('/')[1]
            else:
                mime_subtype = mime_type
            
            # Preserve other attributes
            original = match.group(0)
            width_match = re.search(r'width=["\']?(\d+)', original, re.IGNORECASE)
            height_match = re.search(r'height=["\']?(\d+)', original, re.IGNORECASE)
            
            attrs = f'src="data:image/{mime_subtype};base64,{base64_data}"'
            if width_match:
                attrs += f' width="{width_match.group(1)}"'
            if height_match:
                attrs += f' height="{height_match.group(1)}"'
                
            return f'<img {attrs} />'
            
        except Exception as e:
            print(f"Failed to fetch image {image_id}: {e}")
            return match.group(0)  # Keep reference if fetch fails
    
    return DOCIMG_PATTERN.sub(replace_docimg, html)


def has_embedded_images(html: str) -> bool:
    """Check if HTML contains embedded base64 images."""
    return bool(BASE64_IMG_PATTERN.search(html))


def has_docimg_references(html: str) -> bool:
    """Check if HTML contains docimg:// references."""
    return bool(DOCIMG_PATTERN.search(html))


def count_embedded_images(html: str) -> int:
    """Count the number of embedded base64 images in HTML."""
    return len(BASE64_IMG_PATTERN.findall(html))
