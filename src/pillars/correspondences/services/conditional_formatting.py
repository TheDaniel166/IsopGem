"""
Conditional Formatting - The Rule Engine.
Applies conditional cell styles based on value comparisons (GT, LT, EQ, CONTAINS).
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QColor

@dataclass
class ConditionalRule:
    rule_type: str # "GT", "LT", "EQ", "CONTAINS", "BETWEEN"
    value: Any # Threshold
    format_style: Dict[str, Any] # e.g., {"bg": "#FF0000", "fg": "#FFFFFF"}
    ranges: List[tuple] # List of (top, left, bottom, right) tuples defining where applied

class ConditionalManager:
    """
    Evaluates rules against cell values.
    """
    def __init__(self):
        self.rules: List[ConditionalRule] = []

    def add_rule(self, rule: ConditionalRule):
        self.rules.append(rule)

    def clear_all_rules(self):
        self.rules = []

    def get_style(self, row, col, value) -> Optional[Dict[str, Any]]:
        """Returns format dict if any rule matches, else None."""
        # Check rules in order (or reverse? Excel applies top-down stop if true?)
        # We apply all, last one wins? Or first match?
        # Standard: LIFO or FIFO? Usually priority list.
        # We'll check all applicable rules and merge styles? 
        # MVP: First match wins.
        
        for rule in self.rules:
            # 1. Check Range
            in_range = False
            for (t, l, b, r) in rule.ranges:
                if t <= row <= b and l <= col <= r:
                    in_range = True
                    break
            if not in_range: continue
            
            # 2. Check Condition
            if self._check_condition(rule, value):
                return rule.format_style
        return None

    def _check_condition(self, rule, value):
        try:
            # Value conversion (similar to sorting)
            # Both rule.value and cell value might be strings
            
            # Handle Empty
            if value is None or value == "":
                # Some rules match empty?
                return False

            # Convert to float if possible for GT/LT
            v_num = None
            t_num = None
            try:
                v_num = float(value)
                t_num = float(rule.value)
            except: pass

            rt = rule.rule_type.upper()
            
            if rt == "GT":
                if v_num is not None and t_num is not None:
                    return v_num > t_num
            elif rt == "LT":
                if v_num is not None and t_num is not None:
                    return v_num < t_num
            elif rt == "EQ":
                # Strict equality? string equality?
                return str(value).lower() == str(rule.value).lower()
            elif rt == "CONTAINS":
                return str(rule.value).lower() in str(value).lower()
                
        except:
            return False
        return False
