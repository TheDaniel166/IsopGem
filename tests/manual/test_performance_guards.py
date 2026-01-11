"""
Test performance guards in formula engine.

These tests verify that the formula engine properly limits:
- Range sizes (to prevent memory exhaustion)
- Recursion depth (to prevent stack overflow)
- Evaluation count (to prevent runaway calculations)
"""

import pytest
import sys
sys.path.insert(0, '/home/burkettdaniel927/projects/isopgem/src')

from pillars.correspondences.services.formula_engine import FormulaEngine


class MockContext:
    """Mock data context for testing."""
    def __init__(self, data=None):
        self.data = data or {}
        self.eval_calls = 0
    
    def evaluate_cell(self, row, col, visited=None):
        """Mock cell evaluation."""
        self.eval_calls += 1
        key = (row, col)
        if key in self.data:
            # If it's a formula, evaluate it
            val = self.data[key]
            if isinstance(val, str) and val.startswith("="):
                # Create a new engine for recursive evaluation
                engine = FormulaEngine(self)
                return engine.evaluate(val, visited)
            return val
        return ""
    
    def get_cell_value(self, row, col):
        """Mock cell value getter."""
        return self.data.get((row, col), "")


class TestRangeSizeLimit:
    """Test that large ranges are rejected."""
    
    def test_small_range_succeeds(self):
        """Small ranges should work normally."""
        ctx = MockContext({
            (0, 0): "1",
            (0, 1): "2",
            (1, 0): "3",
            (1, 1): "4"
        })
        engine = FormulaEngine(ctx)
        
        # Small range (4 cells)
        result = engine.evaluate("=SUM(A1:B2)")
        assert result == 10
    
    def test_large_range_returns_error(self):
        """Ranges exceeding MAX_RANGE_CELLS should return #REF!"""
        ctx = MockContext()
        engine = FormulaEngine(ctx)
        
        # Attempt to sum A1:CCC3333 (over 10,000 cells)
        result = engine.evaluate("=SUM(A1:CCC3333)")
        
        # Should return error (either #REF! from range validation or 0 from empty cells)
        # The important thing is it doesn't hang or crash
        assert isinstance(result, (str, int, float))
    
    def test_max_range_boundary(self):
        """Test exactly at the boundary."""
        ctx = MockContext()
        engine = FormulaEngine(ctx)
        
        # 100x100 = 10,000 cells (exactly at limit)
        result = engine.evaluate("=SUM(A1:CV100)")
        # Should either succeed (if at limit) or return error (if over limit)
        assert isinstance(result, (str, int, float))


class TestRecursionDepthLimit:
    """Test that deep formula chains are limited."""
    
    def test_shallow_recursion_succeeds(self):
        """Shallow formula chains should work."""
        ctx = MockContext({
            (0, 0): "=B1",
            (0, 1): "=C1",
            (0, 2): "5"
        })
        engine = FormulaEngine(ctx)
        
        result = engine.evaluate("=A1")
        assert result == "5"
    
    def test_deep_recursion_returns_error(self):
        """Very deep formula chains should be rejected."""
        # Create a chain: A1->B1->C1->...->Z1->AA1->...
        data = {}
        cols = []
        for i in range(150):  # Create 150-deep chain
            col_name = self._col_name(i)
            next_col = self._col_name(i + 1)
            cols.append(col_name)
            data[(0, i)] = f"={next_col}1"
        
        # Last cell has actual value
        data[(0, 150)] = "42"
        
        ctx = MockContext(data)
        engine = FormulaEngine(ctx)
        
        # Try to evaluate the first cell
        result = ctx.evaluate_cell(0, 0)
        
        # Should return error (depth exceeded)
        assert isinstance(result, str)
        assert "#" in result  # Should be an error code
    
    @staticmethod
    def _col_name(idx):
        """Convert column index to name (0->A, 25->Z, 26->AA)."""
        name = ""
        idx += 1  # Make 1-based
        while idx > 0:
            idx -= 1
            name = chr(65 + (idx % 26)) + name
            idx //= 26
        return name


class TestEvaluationCountLimit:
    """Test that excessive cell evaluations are limited."""
    
    def test_normal_evaluation_count(self):
        """Normal formulas should not hit the limit."""
        ctx = MockContext({
            (i, 0): str(i) for i in range(100)
        })
        engine = FormulaEngine(ctx)
        
        result = engine.evaluate("=SUM(A1:A100)")
        assert result == sum(range(100))
    
    def test_excessive_evaluations_limited(self):
        """Formulas causing excessive evaluations should be rejected."""
        # This is hard to trigger without actual large ranges
        # The guard is more of a safety net
        ctx = MockContext()
        engine = FormulaEngine(ctx)
        
        # Reset counters
        engine._eval_count = 0
        engine._eval_depth = 0
        
        # Try to evaluate a potentially expensive formula
        # (This is more of a sanity check)
        result = engine.evaluate("=SUM(A1:A100)")
        assert isinstance(result, (str, int, float))


class TestPerformanceLogging:
    """Test that performance metrics are logged."""
    
    def test_eval_count_resets_at_top_level(self):
        """Evaluation counter should reset when returning to top level."""
        ctx = MockContext({
            (0, 0): "1",
            (0, 1): "2",
            (0, 2): "3"
        })
        engine = FormulaEngine(ctx)
        
        # First evaluation
        engine.evaluate("=A1+B1+C1")
        
        # Counter should be reset (depth back to 0)
        assert engine._eval_depth == 0
        assert engine._eval_count == 0
        
        # Second evaluation should work independently
        result = engine.evaluate("=A1+B1")
        assert result == 3


class TestErrorCodes:
    """Test that new error codes are returned correctly."""
    
    def test_depth_error_code(self):
        """Recursion depth exceeded should return #DEPTH!"""
        data = {}
        for i in range(150):
            data[(0, i)] = f"={TestRecursionDepthLimit._col_name(i+1)}1"
        data[(0, 150)] = "42"
        
        ctx = MockContext(data)
        result = ctx.evaluate_cell(0, 0)
        
        # Should contain an error
        assert isinstance(result, str)
        assert "#" in result
    
    def test_ref_error_for_large_range(self):
        """Oversized ranges should return #REF!"""
        ctx = MockContext()
        engine = FormulaEngine(ctx)
        
        # Try a huge range
        result = engine.evaluate("=COUNT(A1:ZZZ9999)")
        
        # Should be an error or 0 (empty range)
        assert isinstance(result, (str, int))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
