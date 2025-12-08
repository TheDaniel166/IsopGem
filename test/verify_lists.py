import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from pillars.document_manager.ui.rich_text_editor import RichTextEditor

def run_test():
    app = QApplication(sys.argv)
    editor = RichTextEditor()
    editor.show()
    
    def step1():
        print("STEP 1: Setting Text")
        editor.set_text("Item 1\nItem 2")
        
    def step2():
        # Select all first
        cursor = editor.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        editor.editor.setTextCursor(cursor)
        
        # Trigger list button
        editor.action_list_bullet.trigger()
        
    def step3():
        print("STEP 3: Indenting Item 2")
        # Move to Item 2
        cursor = editor.editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        editor.editor.setTextCursor(cursor)
        
        # Trigger Indent
        editor.action_indent.trigger()
        
    def step4():
        print("STEP 4: Verifying Indent Level")
        cursor = editor.editor.textCursor()
        current_list = cursor.currentList()
        if not current_list:
            print("FAIL: No list found")
            app.exit(1)
            return

        fmt = current_list.format()
        indent = fmt.indent()
        print(f"VERIFY: Indent Level = {indent}")
        
        if indent > 1:
            print("SUCCESS: Indent Level increased")
            # app.exit(0)
        else:
            print(f"FAILURE: Indent Level is {indent}, expected > 1")
            # app.exit(1)
            
        app.quit()

    QTimer.singleShot(100, step1)
    QTimer.singleShot(500, step2)
    QTimer.singleShot(1000, step3)
    QTimer.singleShot(2000, step4)
    
    app.exec()

if __name__ == "__main__":
    run_test()
