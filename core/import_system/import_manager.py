from .converters.pdf_converter import PDFConverter
from .converters.rtf_converter import RTFConverter
from .converters.word_converter import WordConverter
import os

class ImportManager:
    def __init__(self):
        self.converters = {
            '.pdf': PDFConverter(),
            '.rtf': RTFConverter(),
            '.doc': WordConverter(),
            '.docx': WordConverter(),
            '.txt': None  # No conversion needed for text files
        }

    def import_document(self, file_path, category):
        """
        Import a document with the appropriate converter
        """
        try:
            # Get file extension
            ext = os.path.splitext(file_path)[1].lower()
            
            # Check if file type is supported
            if ext not in self.converters:
                raise ValueError(f"Unsupported file type: {ext}")

            # Get the appropriate converter
            converter = self.converters[ext]
            
            # Convert if needed, otherwise read directly
            if converter:
                content = converter.convert_to_rtf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                content = self.wrap_text_in_rtf(text)

            # Create metadata
            metadata = {
                'original_file': file_path,
                'file_type': ext,
                'category': category,
                'import_date': None  # You might want to add datetime here
            }

            return {
                'content': content,
                'metadata': metadata
            }

        except Exception as e:
            raise ImportError(f"Failed to import document: {str(e)}")

    def wrap_text_in_rtf(self, text):
        """Wrap plain text in basic RTF format"""
        rtf_header = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Arial;}}\n"
        rtf_footer = r"}"
        escaped_text = text.replace('\\', '\\\\').replace('{', r'\{').replace('}', r'\}')
        return f"{rtf_header}{escaped_text}{rtf_footer}"

    def preview_document(self, file_path):
        """
        Generate a preview of the document
        """
        try:
            ext = os.path.splitext(file_path)[1].lower()
            converter = self.converters.get(ext)
            
            if converter:
                preview = converter.preview(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    preview = f.read(1000)  # First 1000 characters
            
            return preview

        except Exception as e:
            raise ImportError(f"Failed to generate preview: {str(e)}")
