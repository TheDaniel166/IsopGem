"""
Debug script to test vertex visibility in Unified Geometry Viewer.
"""
import sys
import logging
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

from PyQt6.QtWidgets import QApplication
from pillars.geometry.ui.unified.unified_viewer import UnifiedGeometryViewer
from pillars.geometry.canon.vault_of_hestia_solver import VaultOfHestiaSolver

def main():
    app = QApplication(sys.argv)

    # Create viewer
    viewer = UnifiedGeometryViewer()

    # Set solver
    solver = VaultOfHestiaSolver()
    viewer.set_solver(solver)

    # Realize with side_length = 10
    print("\n=== Realizing with side_length = 10 ===")
    payload = viewer.realize_from_canonical(10.0)

    if payload:
        print(f"✓ Payload created: {payload.form_type}")
        print(f"  Dimension: {payload.dimensional_class}")
        print(f"  Has solid_payload: {payload.solid_payload is not None}")

        if payload.solid_payload:
            print(f"  Vertices count: {len(payload.solid_payload.vertices)}")

    # Check 3D view state
    print("\n=== Checking 3D View ===")
    viewport = viewer._viewport
    print(f"  3D view initialized: {viewport._view_3d is not None}")

    if viewport._view_3d:
        print(f"  3D view _show_vertices: {viewport._view_3d._show_vertices}")

    # Check checkbox
    print("\n=== Checking Checkbox ===")
    print(f"  Vertices checkbox exists: {hasattr(viewer, '_vertices_checkbox')}")
    if hasattr(viewer, '_vertices_checkbox'):
        print(f"  Vertices checkbox checked: {viewer._vertices_checkbox.isChecked()}")

    # Now toggle it ON
    print("\n=== Toggling Vertices ON ===")
    viewer._vertices_checkbox.setChecked(True)

    # Check again
    if viewport._view_3d:
        print(f"  3D view _show_vertices after toggle: {viewport._view_3d._show_vertices}")

    viewer.show()

    print("\n=== Window shown - check if vertices are visible ===")
    print("Instructions:")
    print("1. The window should show a Vault of Hestia")
    print("2. Check the 'Show Vertices' checkbox")
    print("3. Vertices should appear as spheres at corners")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
