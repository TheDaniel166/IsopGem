
import sys
import os
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.document_manager.utils.parsers import DocumentParser

def test_list_detection():
    print("Testing List Detection...")
    
    # Mock Paragraph with numPr
    para = MagicMock()
    para.style.name = "List Paragraph"
    
    # Case 1: Standard List with numPr (Bullet/Number)
    para._p.pPr.numPr.ilvl.val = "0"
    para._p.pPr.numPr.numId.val = "1"
    
    list_type, level = DocumentParser._get_list_properties(para)
    print(f"Case 1 (numPr, level 0): Type={list_type}, Level={level}")
    assert list_type == 'ul' # Default to ul if style doesn't say otherwise
    assert level == 0
    
    # Case 2: Nested List
    para._p.pPr.numPr.ilvl.val = "2"
    list_type, level = DocumentParser._get_list_properties(para)
    print(f"Case 2 (numPr, level 2): Type={list_type}, Level={level}")
    assert level == 2
    
    # Case 3: Explicit Numbering Style
    para.style.name = "List Number"
    list_type, level = DocumentParser._get_list_properties(para)
    print(f"Case 3 (Style 'List Number'): Type={list_type}, Level={level}")
    assert list_type == 'ol'
    
    # Case 4: No numPr, but style name
    para._p.pPr.numPr = None
    para.style.name = "List Bullet"
    list_type, level = DocumentParser._get_list_properties(para)
    print(f"Case 4 (No numPr, Style 'List Bullet'): Type={list_type}, Level={level}")
    assert list_type == 'ul'
    assert level == 0
    
    # Case 5: Normal Paragraph
    para.style.name = "Normal"
    para._p.pPr.numPr = None
    list_type, level = DocumentParser._get_list_properties(para)
    print(f"Case 5 (Normal): Type={list_type}, Level={level}")
    assert list_type is None
    
    print("\nSUCCESS: All list detection cases passed.")

if __name__ == "__main__":
    try:
        test_list_detection()
    except Exception as e:
        print(f"\nFAILURE: {e}")
        exit(1)
