
import os
import sys
from pathlib import Path
from pillars.document_manager.utils.parsers import DocumentParser

def create_dummy_docx(filename):
    try:
        import docx
    except ImportError:
        print("python-docx not installed, skipping docx creation")
        return

    doc = docx.Document()
    doc.core_properties.title = "Test Document Title"
    doc.core_properties.author = "Test Author"
    doc.add_paragraph("This is a test document.")
    doc.save(filename)
    print(f"Created {filename}")

def test_metadata_extraction():
    # Test DOCX
    docx_path = "test_metadata.docx"
    create_dummy_docx(docx_path)
    
    if os.path.exists(docx_path):
        try:
            print(f"Testing {docx_path}...")
            # Note: We haven't updated the parser return signature yet, so this will likely fail or return 3 values
            # This script is for AFTER we update the code, but we can write it now.
            try:
                result = DocumentParser.parse_file(docx_path)
                if len(result) == 4:
                    _, _, _, metadata = result
                    print(f"Metadata extracted: {metadata}")
                    if metadata.get('title') == "Test Document Title" and metadata.get('author') == "Test Author":
                        print("PASS: DOCX Metadata matched")
                    else:
                        print("FAIL: DOCX Metadata mismatch")
                else:
                    print(f"FAIL: Expected 4 values, got {len(result)}")
            except Exception as e:
                print(f"FAIL: Exception during parsing: {e}")
        finally:
            if os.path.exists(docx_path):
                os.remove(docx_path)

if __name__ == "__main__":
    # Add project root to path
    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
    test_metadata_extraction()
