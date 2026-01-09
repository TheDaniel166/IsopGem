
import sys
import unittest
from pathlib import Path

# Add repo root and src to path
repo_root = Path.cwd()
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
if str(repo_root / "src") not in sys.path:
    sys.path.insert(0, str(repo_root / "src"))

try:
    from src.pillars.geometry.ui.advanced_scientific_calculator_window import _safe_math_eval
except ImportError as e:
    print(f"Import failed: {e}")
    # Try dropping into src if running from inside src (unlikely but safe)
    sys.path.insert(0, str(repo_root / "src"))
    from pillars.geometry.ui.advanced_scientific_calculator_window import _safe_math_eval

class TestCalculatorSecurity(unittest.TestCase):
    def test_basic_math(self):
        """Sun Trial: Does it calculate correctly?"""
        res = _safe_math_eval("1 + 1", allowed_funcs={}, allowed_consts={})
        self.assertEqual(res, 2)
        
    def test_exploit_injection(self):
        """Mars Trial: Does it block injection?"""
        payloads = [
            "__import__('os').system('ls')",
            "eval('1+1')",
            "open('/etc/passwd').read()",
            "compile('print(1)', '', 'exec')",
            "[x for x in (1,2,3)]", # List comp (should be blocked)
            "lambda x: x", # Lambda (should be blocked)
        ]
        
        allowed_funcs = {"sin": lambda x: x}
        allowed_consts = {"pi": 3.14}
        
        for p in payloads:
            print(f"Testing payload: {p}")
            with self.assertRaises(ValueError) as cm:
                _safe_math_eval(p, allowed_funcs=allowed_funcs, allowed_consts=allowed_consts)
            print(f" -> BLOCKED: {cm.exception}")

if __name__ == "__main__":
    unittest.main()
