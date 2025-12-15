
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.services.formula_engine import FormulaEngine

def verify_string_functions():
    engine = FormulaEngine({}) # Empty context
    
    # 1. LEN
    chk(engine, '=LEN("Hello")', 5)
    chk(engine, '=LEN("")', 0)
    
    # 2. Case
    chk(engine, '=UPPER("Hello")', "HELLO")
    chk(engine, '=LOWER("Hello")', "hello")
    chk(engine, '=PROPER("hello world")', "Hello World")
    
    # 3. Concatenation Operator
    chk(engine, '="A" & "B"', "AB")
    chk(engine, '="Age: " & 10', "Age: 10")
    
    # 4. Substring
    chk(engine, '=LEFT("Abcde", 2)', "Ab")
    chk(engine, '=RIGHT("Abcde", 2)', "de")
    chk(engine, '=MID("Abcde", 2, 3)', "bcd")
    
    # 5. Trim
    chk(engine, '=TRIM("  A   B  ")', "A B")
    
    # 6. Replace/Substitute
    chk(engine, '=REPLACE("abcdef", 3, 2, "XY")', "abXYef") # c,d replaced by XY
    chk(engine, '=SUBSTITUTE("banana", "a", "o")', "bonono")
    chk(engine, '=SUBSTITUTE("banana", "a", "o", 2)', "banona") # 2nd instance
    
    # 7. TextJoin
    chk(engine, '=TEXTJOIN(",", 1, "A", "", "B")', "A,B") # skip empty
    chk(engine, '=TEXTJOIN(",", 0, "A", "", "B")', "A,,B") # keep empty

def chk(engine, formula, expected):
    result = engine.evaluate(formula)
    if result == expected:
        print(f"PASS: {formula} -> '{result}'")
    else:
        print(f"FAIL: {formula} -> Expected '{expected}', got '{result}'")

if __name__ == "__main__":
    verify_string_functions()
