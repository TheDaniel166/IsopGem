"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: Domain Logic (GRANDFATHERED - should move to pillars/tq)
- USED BY: Adyton, Tq (14 references)
- CRITERION: Violation (Single-pillar domain logic)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""Service for ternary conversions."""

class TernaryService:
    """Service for handling decimal-ternary conversions."""

    
    @staticmethod
    def decimal_to_ternary(n: int) -> str:
        """
        Convert a decimal integer to a ternary string.
        
        Args:
            n: Decimal integer
            
        Returns:
            Ternary string representation
        """
        if n == 0:
            return "0"
            
        nums = []
        is_negative = False
        
        if n < 0:
            is_negative = True
            n = abs(n)
            
        while n:
            n, r = divmod(n, 3)
            nums.append(str(r))
            
        result = ''.join(reversed(nums))
        return f"-{result}" if is_negative else result

    @staticmethod
    def ternary_to_decimal(t: str) -> int:
        """
        Convert a ternary string to a decimal integer.
        
        Args:
            t: Ternary string
            
        Returns:
            Decimal integer
            
        Raises:
            ValueError: If string contains invalid ternary characters
        """
        if not t:
            return 0
            
        # Handle negative numbers
        is_negative = False
        if t.startswith('-'):
            is_negative = True
            t = t[1:]
            
        # Validate input
        if not all(c in '012' for c in t):
            raise ValueError("Input string must only contain 0, 1, and 2")
            
        result = int(t, 3)
        return -result if is_negative else result

    @staticmethod
    def conrune_transform(t: str) -> str:
        """
        Apply Conrune transformation to a ternary string.
        0 -> 0
        1 -> 2
        2 -> 1
        
        Args:
            t: Ternary string
            
        Returns:
            Transformed ternary string
        """
        if not t:
            return ""
            
        # Handle negative sign - preserve it
        prefix = ""
        if t.startswith('-'):
            prefix = "-"
            t = t[1:]
            
        mapping = {'0': '0', '1': '2', '2': '1'}
        transformed = ''.join(mapping.get(c, c) for c in t)
        return prefix + transformed

    @staticmethod
    def reverse_ternary(t: str) -> str:
        """
        Reverse a ternary string.
        
        Args:
            t: Ternary string
            
        Returns:
            Reversed ternary string
        """
        if not t:
            return ""
            
        # Handle negative sign - preserve it at start? 
        # Or does reversal imply reversing the digits including sign logic?
        # Usually in number theory reversals, we reverse the magnitude.
        prefix = ""
        if t.startswith('-'):
            prefix = "-"
            t = t[1:]
            
        return prefix + t[::-1]