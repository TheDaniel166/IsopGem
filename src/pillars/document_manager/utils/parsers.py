"""File parsing utilities for document import."""
import os
from pathlib import Path
import base64

# Optional imports for file support
try:
    import docx
except ImportError:
    docx = None

try:
    import mammoth
except ImportError:
    mammoth = None

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from striprtf.striprtf import rtf_to_text
except ImportError:
    rtf_to_text = None

try:
    from pdf2docx import Converter
except ImportError:
    Converter = None

class DocumentParser:
    """Parses various file formats to extract text and HTML."""
    
    @staticmethod
    def parse_file(file_path: str) -> tuple[str, str, str]:
        """
        Parse a file and return (content_text, raw_html, file_type).
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Tuple of (extracted_text, raw_html, file_extension)
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == '.txt':
            text = DocumentParser._parse_txt(path)
            return text, f"<pre>{text}</pre>", 'txt'
        elif ext == '.html' or ext == '.htm':
            html = DocumentParser._parse_html(path)
            # TODO: Extract text from HTML properly
            return html, html, 'html'
        elif ext == '.docx':
            return DocumentParser._parse_docx(path)
        elif ext == '.pdf':
            return DocumentParser._parse_pdf(path)
        elif ext == '.rtf':
            text = DocumentParser._parse_rtf(path)
            return text, f"<pre>{text}</pre>", 'rtf'
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    @staticmethod
    def _parse_txt(path: Path) -> str:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    @staticmethod
    def _parse_html(path: Path) -> str:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    @staticmethod
    def _parse_docx(path: Path) -> tuple[str, str, str]:
        # Try mammoth first for HTML conversion
        if mammoth:
            with open(path, "rb") as docx_file:
                result = mammoth.convert_to_html(docx_file)
                html = result.value
                
                # Post-process HTML to ensure tables have borders
                # QTextEdit needs border="1" to show grid lines
                html = html.replace("<table>", '<table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; width: 100%;">')
        else:
            html = None

        # Use python-docx for text extraction (reliable)
        if docx:
            doc = docx.Document(str(path))
            text = "\n".join([para.text for para in doc.paragraphs])
        else:
            if not mammoth:
                 raise ImportError("python-docx or mammoth is required for .docx files")
            text = "" # Fallback if only mammoth

        if not html:
            html = f"<pre>{text}</pre>"

        return text, html, 'docx'

    @staticmethod
    def _parse_pdf(path: Path) -> tuple[str, str, str]:
        text = ""
        html = ""
        
        # Try pdf2docx -> mammoth pipeline for better table/layout preservation
        if Converter and mammoth and docx:
            import tempfile
            
            # Create temp file for DOCX
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
                docx_path = tmp.name
            
            try:
                # Convert PDF to DOCX
                cv = Converter(str(path))
                cv.convert(docx_path, start=0)
                cv.close()
                
                # Parse the generated DOCX using our existing method
                # This gives us clean HTML with tables from mammoth
                text, html, _ = DocumentParser._parse_docx(Path(docx_path))
                
                # Clean up
                os.unlink(docx_path)
                return text, html, 'pdf'
                
            except Exception as e:
                print(f"pdf2docx conversion failed, falling back to fitz: {e}")
                if os.path.exists(docx_path):
                    os.unlink(docx_path)
                # Fall through to fitz/pypdf fallback

        # Use PyMuPDF (fitz) for HTML with images
        if fitz:
            doc = fitz.open(path)
            for page in doc:
                # Get text
                text += str(page.get_text("text"))
                # Get HTML
                html += str(page.get_text("html"))
                
            doc.close()
        elif pypdf:
            # Fallback to text only
            with open(path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            html = f"<pre>{text}</pre>"
        else:
             raise ImportError("PyMuPDF or pypdf is required for .pdf files")

        return text, html, 'pdf'

    @staticmethod
    def _parse_rtf(path: Path) -> str:
        if not rtf_to_text:
            raise ImportError("striprtf is required for .rtf files")
            
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            return rtf_to_text(content)
