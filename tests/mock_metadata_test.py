
import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from pillars.document_manager.utils.parsers import DocumentParser

class TestParsers(unittest.TestCase):
    
    @patch('pillars.document_manager.utils.parsers.mammoth')
    @patch('pillars.document_manager.utils.parsers.docx')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data=b"data")
    def test_parse_docx_metadata(self, mock_file, mock_docx, mock_mammoth):
        # Setup mock document
        mock_file.return_value.tell.return_value = 100
        
        # Setup mammoth
        mock_mammoth.convert_to_html.return_value.value = "<html>Mock HTML</html>"
        
        mock_doc = MagicMock()
        mock_doc.core_properties.title = "Mock Title"
        mock_doc.core_properties.author = "Mock Author"
        mock_doc.paragraphs = [MagicMock(text="Paragraph 1")]
        
        mock_docx.Document.return_value = mock_doc
        
        # Test
        text, html, ext, metadata = DocumentParser._parse_docx(Path("dummy.docx"))
        
        self.assertEqual(metadata['title'], "Mock Title")
        self.assertEqual(metadata['author'], "Mock Author")
        self.assertEqual(ext, 'docx')

    @patch('pillars.document_manager.utils.parsers.pypdf')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data=b"data")
    def test_parse_pdf_metadata(self, mock_file, mock_pypdf):
        # Setup mock reader
        mock_reader = MagicMock()
        mock_reader.is_encrypted = False
        mock_reader.metadata.title = "PDF Title"
        mock_reader.metadata.author = "PDF Author"
        mock_reader.pages = [MagicMock()]
        mock_reader.pages[0].extract_text.return_value = "PDF Text"
        
        mock_pypdf.PdfReader.return_value = mock_reader
        
        # Disable fitz to force pypdf path
        with patch('pillars.document_manager.utils.parsers.fitz', None):
            # Test
            text, html, ext, metadata = DocumentParser._parse_pdf(Path("dummy.pdf"))
            
            self.assertEqual(metadata['title'], "PDF Title")
            self.assertEqual(metadata['author'], "PDF Author")
            self.assertEqual(ext, 'pdf')

if __name__ == '__main__':
    unittest.main()
