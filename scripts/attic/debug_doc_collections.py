import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from pillars.document_manager.services.document_service import document_service_context

def main():
    try:
        with document_service_context() as service:
            docs = service.get_all_documents()
            print(f"Found {len(docs)} documents.")
            print("-" * 60)
            print(f"{'ID':<5} | {'Title':<30} | {'Collection':<20} | {'Tags'}")
            print("-" * 60)
            
            holy_matches = 0
            for d in docs:
                collection = str(d.collection) if d.collection else "None"
                tags = str(d.tags) if hasattr(d, 'tags') and d.tags else "None"
                
                # Check filter logic
                coll_lower = (d.collection or "").lower()
                tags_lower = tags.lower()
                is_match = "holy" in coll_lower or "holy" in tags_lower
                
                match_mark = "*" if is_match else " "
                
                print(f"{match_mark} {d.id:<3} | {d.title[:28]:<30} | {collection[:18]:<20} | {tags[:20]}")
                
                if is_match:
                    holy_matches += 1
            
            print("-" * 60)
            print(f"Total Matches for 'holy': {holy_matches}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
