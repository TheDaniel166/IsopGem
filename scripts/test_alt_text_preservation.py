"""
Test if alt text is preserved through HTML serialization/deserialization.
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication, QTextEdit
from PyQt6.QtGui import QTextImageFormat, QTextCursor, QImage, QTextDocument
from PyQt6.QtCore import QUrl
import uuid

def main():
    app = QApplication(sys.argv)

    editor = QTextEdit()

    # Create a dummy image
    image = QImage(100, 100, QImage.Format.Format_RGB32)
    image.fill(0xFF0000)  # Red

    # Add to document resources
    img_id = str(uuid.uuid4())
    url_str = f"docimg://math/{img_id}"
    doc = editor.document()
    doc.addResource(QTextDocument.ResourceType.ImageResource, QUrl(url_str), image)

    # Create image format with alt text
    fmt = QTextImageFormat()
    fmt.setName(url_str)
    fmt.setWidth(100)
    fmt.setHeight(100)
    fmt.setProperty(QTextImageFormat.Property.ImageAltText, "LATEX:\\varphi = \\frac{1 + \\sqrt{5}}{2}")

    # Insert image
    cursor = editor.textCursor()
    cursor.insertText("Before ")
    cursor.insertImage(fmt)
    cursor.insertText(" After")

    # Get HTML
    html = editor.toHtml()
    print("=== Generated HTML ===")
    print(html)
    print()

    # Create new editor and load HTML
    editor2 = QTextEdit()
    editor2.setHtml(html)

    # Try to extract alt text
    print("=== Checking if alt text preserved ===")
    cursor2 = editor2.textCursor()
    cursor2.movePosition(QTextCursor.MoveOperation.Start)

    found_image = False
    while not cursor2.atEnd():
        cursor2.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)
        fmt2 = cursor2.charFormat()

        if fmt2.isImageFormat():
            found_image = True
            img_fmt2 = QTextImageFormat(fmt2)
            alt = img_fmt2.property(QTextImageFormat.Property.ImageAltText)
            print(f"Image found!")
            print(f"  Name: {img_fmt2.name()}")
            print(f"  Alt text: {alt}")
            break

        cursor2.clearSelection()

    if not found_image:
        print("No image found in loaded HTML!")

    app.quit()

if __name__ == "__main__":
    main()
