"""
Common panel registration
"""
from ..registry import get_registry
from .properties_panel import PropertiesPanel
from .document_viewer import DocumentViewer

def create_document_viewer():
    """Factory function for document viewer"""
    viewer = DocumentViewer()
    return viewer

def create_properties_panel():
    """Factory function for properties panel"""
    return PropertiesPanel()

# Register panel factories
registry = get_registry()
registry.register("Document Viewer", create_document_viewer)
registry.register("Properties", create_properties_panel)

__all__ = ['PropertiesPanel', 'DocumentViewer']
