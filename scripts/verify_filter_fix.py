import sys
from unittest.mock import MagicMock

# Define mockup of the Document class as it exists in current SQLAlchemy model 
# (i.e., NO tags attribute)
class MockDocument:
    def __init__(self, id, title, collection):
        self.id = id
        self.title = title
        self.collection = collection
        # Intentionally no 'tags' attribute here to simulate the real object

def verify_filter_fix():
    print("Verifying Text Analysis Document Filter Logic...")
    
    # 1. Mock Documents
    docs = [
        MockDocument(1, "Book A", "Holy Books"),
        MockDocument(2, "Book B", "General"),
        MockDocument(3, "Book C", "Other"),
        MockDocument(4, "Book D", "My Holy Library")
    ]
    
    # 2. Simulate the logic inside _load_documents
    filtered_items = []
    
    print("-" * 40)
    for d in docs:
        try:
            # THIS IS THE FIXED LOGIC from main_window.py
            collection = (d.collection or "").lower()
            # tags = ... REMOVED
            
            if "holy" in collection:
                filtered_items.append(d.title)
                print(f"[PASS] Included: {d.title} (Collection: {d.collection})")
            else:
                print(f"[SKIP] Excluded: {d.title} (Collection: {d.collection})")
                
        except AttributeError as e:
            print(f"[ERROR] Crashed on {d.title}: {e}")
            sys.exit(1)
            
    print("-" * 40)
    
    # 3. Assertions
    expected = ["Book A", "Book D"]
    if filtered_items == expected:
        print("SUCCESS: Filter correctly identified Holy books without crashing.")
    else:
        print(f"FAILURE: Expected {expected}, got {filtered_items}")
        sys.exit(1)

if __name__ == "__main__":
    verify_filter_fix()
