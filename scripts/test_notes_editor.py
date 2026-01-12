"""
Test script for the full notes editor with auto-render.
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

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
    print("\n=== Realizing Vault of Hestia with side_length = 10 ===")
    payload = viewer.realize_from_canonical(10.0)

    if payload:
        print(f"✓ Payload created: {payload.form_type}")

        # Manually save to history
        print("\n=== Manually saving to history ===")
        viewer._on_save_to_history()

        # Open history to add notes
        print("\n=== Opening history panel ===")
        viewer._toggle_history_panel()

    viewer.show()

    print("\n=== Instructions ===")
    print("1. Click on the history item")
    print("2. Click the '📝 Notes' button")
    print("3. Click '📝 Open Full Editor'")
    print("4. Type some LaTeX: $\\varphi = \\frac{1 + \\sqrt{5}}{2}$")
    print("5. Wait 1.5 seconds - it should auto-render WITHOUT dialog")
    print("6. Type some Mermaid:")
    print("   ```mermaid")
    print("   graph TD")
    print("   A[Start] --> B[End]")
    print("   ```")
    print("7. Wait 1.5 seconds - it should auto-render WITHOUT dialog")
    print("8. Check console - should NOT see 'Failed to parse image ID' warnings")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
