from PyPDF2 import PdfReader

class PDFConverter:
    def convert(self, file_path):
        """Convert PDF file to text"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Failed to convert PDF: {str(e)}")

    def preview(self, file_path):
        """Generate preview of PDF file"""
        try:
            reader = PdfReader(file_path)
            if len(reader.pages) > 0:
                preview = reader.pages[0].extract_text()
                return preview[:1000]  # First 1000 characters
            return ""
        except Exception as e:
            raise ValueError(f"Failed to preview PDF: {str(e)}")

    def convert_to_rtf(self, file_path):
        """Convert PDF to RTF format"""
        try:
            # First get text content
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Convert to RTF
            rtf_header = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Arial;}}\n"
            rtf_footer = r"}"
            escaped_text = text.replace('\\', '\\\\').replace('{', r'\{').replace('}', r'\}')
            return f"{rtf_header}{escaped_text}{rtf_footer}"
            
        except Exception as e:
            raise ValueError(f"Failed to convert PDF: {str(e)}")
