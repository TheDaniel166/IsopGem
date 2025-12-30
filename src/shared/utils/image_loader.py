"""
Image Loader Utility.

Handles loading of image assets, providing support for formats 
not natively supported by Qt (e.g., TIFF) via Pillow.
"""
from pathlib import Path
from typing import Optional
import sys

# Try to import PIL from the environment
try:
    from PIL import Image
    from PIL.ImageQt import ImageQt
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("Warning: Pillow not found. TIFF support disabled.", file=sys.stderr)

from PyQt6.QtGui import QPixmap, QImage


def load_pixmap(path: str) -> QPixmap:
    """
    Load an image from a path into a QPixmap.
    
    If the format is not supported by Qt (e.g. TIFF) and Pillow is available,
    uses Pillow to convert it.
    
    Args:
        path: Absolute or relative path to the image.
        
    Returns:
        QPixmap: The loaded pixmap, or a null pixmap if loading failed.
    """
    if not path:
        return QPixmap()

    # Try standard Qt load first (fastest for PNG, JPG)
    pixmap = QPixmap(path)
    if not pixmap.isNull():
        return pixmap
        
    # If standard load failed, and we have Pillow, try to rescue it
    if HAS_PILLOW:
        p = Path(path)
        # Check extensions common for Pillow but maybe not Qt
        if p.suffix.lower() in ['.tif', '.tiff', '.webp']:
            try:
                pil_image = Image.open(path)
                
                # Ensure RGBA for Qt
                if pil_image.mode != 'RGBA':
                    pil_image = pil_image.convert('RGBA')
                    
                # Convert to QImage then QPixmap
                q_image = ImageQt(pil_image)
                return QPixmap.fromImage(q_image)
                
            except Exception as e:
                # If Pillow fails, we can't do anything else
                print(f"Error loading image '{path}' with Pillow: {e}", file=sys.stderr)
                pass
                
    return QPixmap()
