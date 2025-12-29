"""
Centralized logging configuration for IsopGem.
"""
import logging
import logging.handlers
import sys
from pathlib import Path

# Paths
LOG_DIR = Path.home() / ".gemini" / "logs"
LOG_FILE = LOG_DIR / "gemini.log"

def configure_logging(level=logging.INFO):
    """
    Configure root logger with Console and RotatingFile handlers.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # Formatters
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    )
    console_formatter = logging.Formatter(
        "%(levelname)s: %(message)s   [%(name)s]"
    )
    
    # 1. File Handler (Rotating)
    # 5 MB max size, keep 3 backups
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)
    
    # 2. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)
    
    logging.info("Logging initialized. Writing to %s", LOG_FILE)

# Auto-configure on import if desired, or let main call it
# We let main call it to allow flag overrides.
