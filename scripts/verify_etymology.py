
import sys
import os
sys.path.append(os.getcwd())
try:
    from src.pillars.document_manager.services.etymology_service import get_etymology_service
except ImportError:
    # Handle running from root
    from src.pillars.document_manager.services.etymology_service import get_etymology_service

def verify_etymology():
    service = get_etymology_service()
    
    print("Testing 'robot'...")
    result = service.get_word_origin("robot")
    print(f"Result (robot): {result}")
    
    print("\nTesting 'four' (Scraper Fallback)...")
    res_four = service.get_word_origin("four")
    print(f"Result (four) Origin Length: {len(res_four.get('origin', ''))}")
    print(f"Result (four) Raw Origin: {res_four.get('origin', '')[:500]}...") # Print first 500 chars

    print("\nTesting 'λόγος' (Greek)...")
    res_logos = service.get_word_origin("λόγος")
    print(f"Result (logos): {res_logos.get('origin', '')[:300]}...")
    
    print("\nTesting 'שלום' (Hebrew - Sefaria)...")
    res_shalom = service.get_word_origin("שלום")
    print(f"Result (shalom) source: {res_shalom.get('source', '')}")
    print(f"Result (shalom): {res_shalom.get('origin', '')[:300]}...")
    
    assert "source" in result
    assert "origin" in res_four
    assert "origin" in res_logos
    assert "origin" in res_shalom
    assert "Definitions" in res_logos["origin"]
    assert "Definitions" in res_four["origin"]
    assert res_four["origin"] != "No etymology found."
    
    if result["source"] == "Offline (ety)":
        print("Success: Offline mode works.")
    elif "Online" in result["source"]:
        print("Success: Online fallback works.")
    else:
        print(f"Warning: neither offline nor online worked. Result: {result}")

    # Test empty
    print("\nTesting empty...")
    res_empty = service.get_word_origin("")
    assert res_empty["source"] == "None"

    print("\nVerification Complete.")

if __name__ == "__main__":
    verify_etymology()
