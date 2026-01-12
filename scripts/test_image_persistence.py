"""
Test script to verify LaTeX and Mermaid images persist through HTML save/load.
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from shared.ui.rich_text_editor import RichTextEditor

def main():
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Test Image Persistence")
    window.resize(900, 700)

    layout = QVBoxLayout(window)

    # Create editor 1
    label1 = QLabel("Editor 1 (Type LaTeX and Mermaid, then click Save):")
    layout.addWidget(label1)

    editor1 = RichTextEditor(parent=window, show_ui=True)
    layout.addWidget(editor1)

    # Instructions
    instructions = QLabel(
        "1. Type LaTeX: $\\varphi = \\frac{1 + \\sqrt{5}}{2}$\n"
        "2. Click 'Render All Equations' in Math tab\n"
        "3. Type Mermaid:\n"
        "   ```mermaid\n"
        "   graph TD\n"
        "   A[Start] --> B[End]\n"
        "   ```\n"
        "4. Click 'Render All Diagrams' in Diagram tab\n"
        "5. Click 'Save HTML' button below"
    )
    layout.addWidget(instructions)

    # Save/Load buttons
    saved_html = [""]

    def save_html():
        html = editor1.editor.toHtml()
        saved_html[0] = html
        print("\n=== SAVED HTML ===")
        print(html[:500])
        print("...")
        print("\n✓ HTML saved to memory")
        load_btn.setEnabled(True)

    def load_html():
        print("\n=== LOADING HTML ===")
        editor1.editor.setHtml(saved_html[0])
        print("✓ HTML loaded - check if images render!")

    save_btn = QPushButton("💾 Save HTML")
    save_btn.clicked.connect(save_html)
    layout.addWidget(save_btn)

    load_btn = QPushButton("📂 Load HTML (should restore images)")
    load_btn.clicked.connect(load_html)
    load_btn.setEnabled(False)
    layout.addWidget(load_btn)

    window.show()

    print("\n=== Test Instructions ===")
    print("1. Add LaTeX and Mermaid content")
    print("2. Render them using ribbon buttons")
    print("3. Click 'Save HTML'")
    print("4. Click 'Load HTML'")
    print("5. Images should reappear (not blobs)!")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
