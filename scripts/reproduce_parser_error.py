
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.services.formula_engine import FormulaEngine

def reproduce_error():
    engine = FormulaEngine({})
    
    # 1. Test Empty Arguments
    # Expectation: Error 'Unexpected token: COMMA'
    formula_empty = '=TEXTJOIN(",",, "A", "B")'
    print(f"Testing: {formula_empty}")
    res = engine.evaluate(formula_empty)
    print(f"Result: {res}")
    
    if "Unexpected token" in str(res) and "COMMA" in str(res):
        print("REPRODUCED: Parser allows no empty args.")
    else:
        print("NOTE: Parser behaved unexpectedly (maybe passed?).")
        
    # 2. Test TRUE/FALSE constants
    # Expectation: Should be True/False, not 0.
    formula_bool = '=IF(TRUE, "Yes", "No")'
    print(f"Testing: {formula_bool}")
    res_bool = engine.evaluate(formula_bool)
    print(f"Result: {res_bool}")
    
    if res_bool == "Yes":
        print("PASS: TRUE constant supported.")
    else:
        print("FAIL: TRUE constant likely 0/False.")

if __name__ == "__main__":
    reproduce_error()
