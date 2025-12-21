
import sys
import os
import base64
from unittest.mock import MagicMock

sys.path.append(os.path.abspath("src"))

from pillars.document_manager.utils.image_utils import extract_images_from_html, restore_images_in_html

def test_image_utils():
    print("Testing Image Utils Refinement...")
    
    # Mock Data
    dummy_bytes = b"fake_image_data"
    dummy_b64 = base64.b64encode(dummy_bytes).decode('utf-8')
    mime = "image/png"
    
    # 1. Non-Destructive Regex Test
    # Input HTML with extra attributes (alt, class, style) and parameters in data URI
    html_input = f'<img alt="Logo" class="center" src="data:{mime};charset=utf-8;base64,{dummy_b64}" style="width:100px;">'
    
    print(f"\n[Test 1] Input HTML: {html_input}")
    
    # Mock Store Callback for deduplication test (returns ID 1 for first call)
    store_mock = MagicMock(side_effect=[1, 2]) 
    
    # Call Extract
    modified_html, images = extract_images_from_html(html_input, store_mock)
    
    print(f"[Test 1] Modified HTML: {modified_html}")
    
    # Assertions
    assert 'docimg://1' in modified_html, "Image ID 1 not found in modified HTML"
    assert 'alt="Logo"' in modified_html, "Attribute 'alt' lost!"
    assert 'class="center"' in modified_html, "Attribute 'class' lost!"
    assert 'style="width:100px;"' in modified_html, "Attribute 'style' lost!"
    
    print("SUCCESS: Non-destructive extraction verified.")
    
    # 2. Deduplication Test
    # Use same image data twice
    html_input_dup = (
        f'<img src="data:{mime};base64,{dummy_b64}">'
        f'<div class="spacer"></div>'
        f'<img src="data:{mime};base64,{dummy_b64}">'
    )
    
    # Reset mock to return ID 100 for the first call
    store_mock = MagicMock(return_value=100)
    
    modified_html_dup, images_dup = extract_images_from_html(html_input_dup, store_mock)
    
    print(f"\n[Test 2] Deduplication HTML: {modified_html_dup}")
    
    # Assertions
    # store_callback should be called ONLY ONCE despite 2 images
    assert store_mock.call_count == 1, f"Store callback called {store_mock.call_count} times, expected 1 (deduplication failed)"
    assert modified_html_dup.count('docimg://100') == 2, "Both images should use ID 100"
    
    print("SUCCESS: Deduplication verified.")
    
    # 3. Restore Test
    # Restore the modified HTML from Test 1
    fetch_mock = MagicMock(return_value=(dummy_bytes, mime))
    
    restored_html = restore_images_in_html(modified_html, fetch_mock)
    print(f"\n[Test 3] Restored HTML: {restored_html}")
    
    assert f'data:image/png;base64,{dummy_b64}' in restored_html, "Base64 data not restored correctly"
    assert 'alt="Logo"' in restored_html, "Attribute 'alt' lost during restore!"
    
    print("SUCCESS: Restoration verified.")

if __name__ == "__main__":
    try:
        test_image_utils()
    except Exception as e:
        print(f"\nFAILURE: {e}")
        exit(1)
