
from pillars.correspondences.services.formula_engine import FormulaEngine, Tokenizer, Parser
import sys

# Mock Context
class MockContext:
    def get_cell_value(self, r, c):
        # Maps 0,0 (A1) -> 10
        # Maps 0,1 (B1) -> 20
        if r == 0 and c == 0: return 10
        if r == 0 and c == 1: return 20
        return 0

engine = FormulaEngine(MockContext())

def check(formula, expected):
    res = engine.evaluate("=" + formula)
    print(f"'{formula}' -> {res} (Exp: {expected})")
    if str(res) != str(expected):
        print("FAIL")
        return False
    return True

print("--- Arithmetic ---")
check("1 + 2", 3.0)
check("2 * 3 + 4", 10.0)
check("2 * (3 + 4)", 14.0)

print("--- Functions ---")
check("SUM(1, 2, 3)", 6.0)
check("MAX(1, 10, 5)", 10.0)

print("--- Logic ---")
check("IF(10 > 5, 'Big', 'Small')", "Big")
check("IF(10 < 5, 'Big', 'Small')", "Small")

print("--- Cell Refs ---")
check("A1 + B1", 30.0) # 10+20
check("SUM(A1, B1)", 30.0)

print("--- Range ---")
# Range A1:B1 -> [10, 20]
check("SUM(A1:B1)", 30.0)
check("COUNT(A1:B1)", 2)

print("--- Standard Math ---")
check("ABS(-5)", 5.0)
check("ROUND(3.14159, 2)", 3.14)
check("FLOOR(3.9)", 3)
check("CEILING(3.1)", 4)
check("SQRT(16)", 4.0)
check("POWER(2, 3)", 8.0)
check("MOD(10, 3)", 1.0)
check("PI()", 3.141592653589793)
check("SIN(0)", 0.0)
check("COS(0)", 1.0)
check("TAN(0)", 0.0)
check("LOG10(100)", 2.0)
