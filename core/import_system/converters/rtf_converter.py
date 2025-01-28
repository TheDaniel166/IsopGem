from striprtf.striprtf import rtf_to_text

class RTFConverter:
    def convert(self, file_path):
        """Convert RTF file to text"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                rtf_content = file.read()
                text = rtf_to_text(rtf_content)
            return text
        except Exception as e:
            raise ValueError(f"Failed to convert RTF: {str(e)}")

    def preview(self, file_path):
        """Generate preview of RTF file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                rtf_content = file.read()
                text = rtf_to_text(rtf_content)
            return text[:1000]  # First 1000 characters
        except Exception as e:
            raise ValueError(f"Failed to preview RTF: {str(e)}")
