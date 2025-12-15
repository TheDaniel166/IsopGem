
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.services.formula_engine import FormulaEngine

def verify_boolean():
    engine = FormulaEngine({})
    
    # 1. FALSE
    formula = '=IF(FALSE, "Yes", "No")'
    res = engine.evaluate(formula)
    print(f"Testing FALSE: '{formula}' -> '{res}'")
    
    if res == "No":
        print("PASS: FALSE constant works.")
    else:
        print(f"FAIL: Expected 'No', got '{res}'")
        
    # 2. Case Insensitivity
    formula2 = '=IF(false, "Yes", "No")'
    res2 = engine.evaluate(formula2)
    print(f"Testing false: '{formula2}' -> '{res2}'")
    
    if res2 == "No":
        print("PASS: false (lowercase) works.")
    else:
        print(f"FAIL: Expected 'No', got '{res}'")

if __name__ == "__main__":
    verify_boolean()  
