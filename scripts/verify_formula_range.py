
import sys
import os
from typing import Any

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.services.formula_engine import FormulaEngine

# Mock Context
class MockContext:
    def __init__(self):
        self.data = {
            (0,0): 10, # A1
            (0,1): 20, # B1
            (1,0): 30, # A2
            (1,1): 40  # B2
        }
    def get_cell_value(self, r, c):
        return self.data.get((r, c), 0)

def verify_range_formula():
    context = MockContext()
    engine = FormulaEngine(context)
    
    # Test 1: Simple Sum
    # A1=10, A2=30. SUM(A1:A2) = 40.
    formula = "=SUM(A1:A2)"
    result = engine.evaluate(formula)
    print(f"Formula: '{formula}' -> {result}")
    
    if result == 40:
        print("PASS: Vertical Range Correct.")
    else:
        print(f"FAIL: Expected 40, got {result}")
        
    # Test 2: 2D Block
    # A1:B2 = 10+20+30+40 = 100
    formula2 = "=SUM(A1:B2)"
    result2 = engine.evaluate(formula2)
    print(f"Formula: '{formula2}' -> {result2}")
    
    if result2 == 100:
        print("PASS: 2D Range Correct.")
    else:
        print(f"FAIL: Expected 100, got {result2}")
        
    # Test 3: Standard Math + Range
    # SUM(A1:B1) + 5 = (10+20)+5 = 35
    formula3 = "=SUM(A1:B1) + 5"
    result3 = engine.evaluate(formula3)
    print(f"Formula: '{formula3}' -> {result3}")
    
    if result3 == 35:
        print("PASS: Math + Range Correct.")
    else:
        print(f"FAIL: Expected 35, got {result3}")

    # Test 4: Mixed Arguments
    # SUM(10, A1:A2) = 10 + (10+30) = 50
    formula4 = "=SUM(10, A1:A2)"
    result4 = engine.evaluate(formula4)
    print(f"Formula: '{formula4}' -> {result4}")
    
    if result4 == 50:
        print("PASS: Mixed Args Correct.")
    else:
        print(f"FAIL: Expected 50, got {result4}")

if __name__ == "__main__":
    verify_range_formula()
