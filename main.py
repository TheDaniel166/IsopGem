"""
IsopGem main entry point
"""
import sys
import asyncio
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop
from core.ui.base.main_window import MainWindow

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s'
)

async def main():
    """Main application entry point"""
    # Set up logging
    logger = logging.getLogger(__name__)
    logger.info("Starting IsopGem")
    
    # Initialize config
    from core.base.config import ConfigManager
    config = ConfigManager()
    config.load()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start the application
    return window

if __name__ == "__main__":
    # Create application instance
    app = QApplication(sys.argv)
    
    # Create qasync loop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Run main async function
    window = loop.run_until_complete(main())
    
    with loop:
        loop.run_forever()
