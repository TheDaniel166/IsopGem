
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.services.formula_engine import FormulaEngine

def verify_textjoin_none():
    engine = FormulaEngine({})
    
    # 1. TEXTJOIN with empty args (None)
    # =TEXTJOIN(,, "a", "b")
    # Delim: None -> ""
    # Ignore: None -> True
    # "a", "b" -> "ab"
    formula = '=TEXTJOIN(,, "a", "b")'
    res = engine.evaluate(formula)
    print(f"Testing: '{formula}' -> '{res}'")
    
    if res == "ab":
        print("PASS: Handled empty args correctly.")
    else:
        print(f"FAIL: Expected 'ab', got '{res}'")
        
    # 2. LEN(None) -> 0?
    # Parser passes None for empty arg.
    # LEN() expects 1 arg. LEN() -> Error?
    # LEN(,) -> Error?
    # LEN("") -> 0.
    
    # Let's test TEXTJOIN(,,)
    

if __name__ == "__main__":
    verify_textjoin_none()
