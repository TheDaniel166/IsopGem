from PyQt6.QtWidgets import QApplication, QTextEdit
from PyQt6.QtPrintSupport import QPrinter
import sys
import os

def verify_pdf_export():
    app = QApplication(sys.argv)
    
    # Create dummy editor with content
    editor = QTextEdit()
    editor.setHtml("<h1>Hello PDF</h1><p>This is a test.</p>")
    
    output_path = "test_export.pdf"
    
    try:
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(output_path)
        
        editor.print(printer)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print("SUCCESS: PDF created successfully")
        else:
            print("FAIL: PDF not created or empty")
            
    except Exception as e:
        print(f"FAIL: Exception during export: {e}")
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    verify_pdf_export()
