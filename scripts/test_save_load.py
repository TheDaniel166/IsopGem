"""
Quick test for save/load of LaTeX and Mermaid in geometry notes.
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
    print("\n=== Realizing Vault of Hestia ===")
    payload = viewer.realize_from_canonical(10.0)

    if payload:
        print(f"✓ Payload created")

        # Save to history
        print("\n=== Saving to history ===")
        viewer._on_save_to_history()

        # Get the history entry
        entry = viewer._history.get_entry(0)
        if entry:
            # Set some test notes with LaTeX and Mermaid
            test_notes = """
            <p>Test notes with LaTeX: <img src="docimg://math/test-uuid" alt="LATEX:\\varphi = \\frac{1 + \\sqrt{5}}{2}" width="100" height="30" /></p>
            <p>And Mermaid: <img src="docimg://mermaid/test-uuid2" alt="MERMAID:graph TD\nA[Start] --&gt; B[End]" width="200" height="150" /></p>
            """

            print("\n=== Setting test HTML ===")
            viewer._history.set_notes_by_signature(entry.signature, test_notes)

            # Now reload
            print("\n=== Reloading notes ===")
            loaded_notes = viewer._history.get_notes_by_signature(entry.signature)
            print(f"Loaded notes length: {len(loaded_notes)}")

            # Open notes window to trigger setHtml
            print("\n=== Opening notes window (will trigger setHtml) ===")
            viewer._show_notes_window(entry, None)

    viewer.show()

    print("\n=== Check console output above for debugging info ===")
    print("The notes window should show the LaTeX and Mermaid images.")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
