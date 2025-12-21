import os
import logging
from pathlib import Path
from PyQt6.QtGui import QFontDatabase

logger = logging.getLogger(__name__)

def load_custom_fonts():
    """
    Load custom fonts from src/assets/fonts directory.
    Supports .ttf and .otf files.
    """
    # Determine path to assets/fonts relative to this file
    # This file is in src/shared/ui/
    # We want src/assets/fonts/
    
    current_dir = Path(__file__).resolve().parent
    src_root = current_dir.parent.parent
    fonts_dir = src_root / "assets" / "fonts"
    
    if not fonts_dir.exists():
        logger.debug(f"Font directory not found: {fonts_dir}")
        return

    logger.debug(f"Scanning for fonts in: {fonts_dir}")
    
    loaded_count = 0
    font_files = []
    
    # Scan for font files
    for ext in ['*.ttf', '*.otf', '*.TTF', '*.OTF']:
        font_files.extend(fonts_dir.glob(ext))
        
    for font_path in font_files:
        try:
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                logger.debug(f"Loaded font(s) from {font_path.name}: {families}")
                loaded_count += 1
            else:
                logger.warning(f"Failed to load font: {font_path.name}")
        except Exception as e:
            logger.error(f"Error loading font {font_path.name}: {e}")
            
    if loaded_count > 0:
        logger.info(f"Successfully loaded {loaded_count} custom fonts.")
    else:
        logger.debug("No custom fonts loaded.")
