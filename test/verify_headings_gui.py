import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer
from pillars.document_manager.ui.rich_text_editor import RichTextEditor

def run_test():
    app = QApplication(sys.argv)
    editor = RichTextEditor()
    editor.show()
    
    def step1():
        print("STEP 1: Setting Text")
        editor.set_text("This is a test paragraph.\nThis is another paragraph.")
        
    def step2():
        print("STEP 2: Moving Cursor to first paragraph")
        # Move cursor to start
        cursor = editor.editor.textCursor()
        cursor.setPosition(5) # Inside "This is..."
        editor.editor.setTextCursor(cursor)
        
    def step3():
        print("STEP 3: Applying Heading 1")
        # Simulate selecting from combo box
        editor.style_combo.setCurrentText("Heading 1")
        # This triggers _apply_style via signal
        
    def step4():
        print("STEP 4: Verifying Format")
        cursor = editor.editor.textCursor()
        # Move back 3 chars to be safely inside the text
        cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.MoveAnchor, 3)
        editor.editor.setTextCursor(cursor)
        
        fmt = cursor.charFormat()
        print(f"VERIFY: Size={fmt.fontPointSize()} Weight={fmt.fontWeight()} Family={fmt.fontFamily()}")
        
        if int(fmt.fontPointSize()) != 24:
            print("FAILURE: Size is not 24")
            # app.exit(1)
        else:
            print("SUCCESS: Size is 24")
            # app.exit(0)
            
        app.quit()

    QTimer.singleShot(100, step1)
    QTimer.singleShot(500, step2)
    QTimer.singleShot(1000, step3)
    QTimer.singleShot(3000, step4)
    
    app.exec()

if __name__ == "__main__":
    run_test()
