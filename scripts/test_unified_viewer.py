#!/usr/bin/env python3
"""
Test Script — Unified Geometry Viewer with Vault of Hestia

This script launches the UnifiedGeometryViewer with the Vault of Hestia
as the first Canon-compliant form to verify end-to-end functionality.

Usage:
    cd src && PYTHONPATH=. python ../scripts/test_unified_viewer.py

Reference: ADR-011: Unified Geometry Viewer
"""

import sys
import logging

# Must set Qt attributes before QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

# Set OpenGL sharing attribute before app creation
QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Launch the unified viewer with Vault of Hestia."""
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Unified Geometry Viewer Test")
    
    logger.info("═══ Unified Geometry Viewer Test ═══")
    
    # Import components
    try:
        from pillars.geometry.ui.unified import UnifiedGeometryViewer
        from pillars.geometry.canon import VaultOfHestiaSolver, VaultOfHestiaRealizer
        from canon_dsl import CanonEngine
        logger.info("✓ All imports successful")
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return 1
    
    # Create the unified viewer
    viewer = UnifiedGeometryViewer()
    logger.info("✓ UnifiedGeometryViewer created")
    
    # Create and configure Canon engine
    engine = CanonEngine()
    realizer = VaultOfHestiaRealizer()
    engine.register_realizer("VaultOfHestia", realizer)
    logger.info("✓ Canon engine configured with VaultOfHestiaRealizer")
    
    # Set the engine on the viewer
    viewer._canon_engine = engine
    
    # Create the solver
    solver = VaultOfHestiaSolver()
    logger.info(f"✓ Solver created: {solver.form_type} ({solver.dimensional_class}D)")
    
    # Set the solver on the viewer
    viewer.set_solver(solver)
    logger.info("✓ Solver set on viewer")
    
    # Realize with a default value
    default_side_length = 10.0
    logger.info(f"Realizing Vault of Hestia with side_length = {default_side_length}...")
    
    payload = viewer.realize_from_canonical(default_side_length)
    
    if payload:
        logger.info("✓ Realization successful!")
        logger.info(f"  Form type: {payload.form_type}")
        logger.info(f"  Dimension: {payload.dimensional_class}D")
        logger.info(f"  Stats: {payload.get_stats_summary()}")
        logger.info(f"  Signature: {payload.get_signature()}")
        logger.info(f"  Validation: {payload.validation_status}")
    else:
        logger.error("✗ Realization failed")
    
    # Show the viewer
    viewer.resize(1400, 900)
    viewer.show()
    logger.info("✓ Viewer shown")
    
    logger.info("═══════════════════════════════════════")
    logger.info("Test the following:")
    logger.info("  1. Property inputs update derived values")
    logger.info("  2. 3D viewport shows Vault of Hestia")
    logger.info("  3. Canon badge shows validation status")
    logger.info("  4. History tab shows calculation entry")
    logger.info("  5. Undo/Redo (Ctrl+Z/Ctrl+Y) works")
    logger.info("  6. Canon tab shows validation details")
    logger.info("═══════════════════════════════════════")
    
    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
