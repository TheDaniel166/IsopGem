import os
import logging
from pathlib import Path
from PyQt6.QtGui import QFontDatabase

logger = logging.getLogger(__name__)

# Registry of loaded custom font families
LOADED_FONTS = []

def load_custom_fonts():
    """
    Load custom fonts from src/assets/fonts directory.
    Supports .ttf and .otf files.
    """
    global LOADED_FONTS
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
                # Register loaded families
                for family in families:
                    if family not in LOADED_FONTS:
                        LOADED_FONTS.append(family)
            else:
                logger.warning(f"Failed to load font: {font_path.name}")
        except Exception as e:
            logger.error(f"Error loading font {font_path.name}: {e}")
            
            
    if loaded_count > 0:
        logger.info(f"Successfully loaded {loaded_count} custom fonts.")
    else:
        logger.debug("No custom fonts loaded.")

def install_new_font(source_path: str) -> str:
    """
    Install a new font file: copy to assets and load it.
    Returns the loaded font family name or None if failed.
    """
    import shutil
    global LOADED_FONTS
    
    src_file = Path(source_path)
    if not src_file.exists():
        logger.error(f"Source font file not found: {source_path}")
        return None
        
    # Target directory
    current_dir = Path(__file__).resolve().parent
    src_root = current_dir.parent.parent
    fonts_dir = src_root / "assets" / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    
    target_file = fonts_dir / src_file.name
    
    try:
        # Copy file
        shutil.copy2(src_file, target_file)
        logger.info(f"Copied font to {target_file}")
        
        # Load it
        font_id = QFontDatabase.addApplicationFont(str(target_file))
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                family = families[0]
                if family not in LOADED_FONTS:
                    LOADED_FONTS.append(family)
                return family
        else:
            logger.warning("Failed to load installed font.")
            return None
            
    except Exception as e:
        logger.error(f"Error installing font: {e}")
        return None
