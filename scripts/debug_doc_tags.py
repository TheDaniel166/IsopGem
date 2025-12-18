import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'src'))
from pillars.document_manager.services.document_service import document_service_context

def main():
    try:
        with document_service_context() as service:
            docs = service.get_all_documents()
            if not docs:
                print("No documents found.")
                return

            d = docs[0]
            print(f"Testing document: {d.title}")
            
            try:
                print(f"Tags attribute: {d.tags}")
            except AttributeError:
                print("CRITICAL: 'Document' object has no attribute 'tags'")
            except Exception as e:
                print(f"Other error accessing tags: {e}")

    except Exception as e:
        print(f"Service error: {e}")

if __name__ == "__main__":
    main()
