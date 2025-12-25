import sys
import os
from PyQt6.QtWidgets import QApplication
from pillars.document_manager.ui.document_library import DocumentLibrary

# Add project root to path
sys.path.append(os.getcwd())

def main():
    app = QApplication(sys.argv)
    
    # Apply basic styling to ensure it looks as expected even without the full app theme
    # (Though the refactor included local styles)
    
    window = DocumentLibrary()
    window.show()
    
    print("Document Library launched as 'The Akaschic Record'. Please verify styles.")
    print("1. Background should be 'Ancient Papyrus' texture (Nano Banana).")
    print("2. Main content should be in a white 'Floating Panel' with shadow.")
    print("3. Table should show columns: ID, Title, Type, Author, Date.")
    print("4. Right-click header to toggle columns.")
    print("5. 'Import' button should be Gold.")
    print("6. Click headers to sort (Numeric for ID/Date).")
    print("7. Type in search box and hit ENTER to verify threaded search.")
    print("8. Right-click selection -> 'Export as Zip...' should work.")
    print("9. Select multiple -> Right-click -> 'Move to Collection' -> New/Existing.")
    print("4. 'Delete' and 'Purge' buttons should be Red.")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
