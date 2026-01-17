"""Simple diagnostic script to exercise WebViewMermaidRenderer and inspect cleanup behavior.

Run with: PYTHONPATH=src ./.venv/bin/python scripts/debug_mermaid_cleanup.py
"""
import logging
import time
from PyQt6.QtWidgets import QApplication

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from pillars.document_manager.ui.features.webview_mermaid_renderer import WebViewMermaidRenderer

app = QApplication([])

logger.info("Creating 3 views (simulate leaks)")
# Create views and intentionally do not return them to pool to simulate leak
views = [WebViewMermaidRenderer._get_view_from_pool() for _ in range(3)]

logger.info("Dumping state after creation")
WebViewMermaidRenderer.debug_dump_state()

logger.info("Returning one view to pool")
WebViewMermaidRenderer._return_view_to_pool(views.pop())
WebViewMermaidRenderer.debug_dump_state()

logger.info("Sleeping briefly to let event loop settle")
app.processEvents()
time.sleep(0.25)

logger.info("Invoking cleanup")
WebViewMermaidRenderer._cleanup_view_pool()
WebViewMermaidRenderer.debug_dump_state()

logger.info("Exiting")
app.quit()