"""Service for Ternary Transition System."""
from typing import List, Tuple, Dict

class TernaryTransitionService:
    """
    Implements the Ternary Transition System.
    
    Mapping:
    (0,0) -> 0    (1,0) -> 2    (2,0) -> 1
    (0,1) -> 2    (1,1) -> 1    (2,1) -> 0
    (0,2) -> 1    (1,2) -> 0    (2,2) -> 2
    """
    
    TRANSITION_MAP = {
        ('0', '0'): '0', ('1', '0'): '2', ('2', '0'): '1',
        ('0', '1'): '2', ('1', '1'): '1', ('2', '1'): '0',
        ('0', '2'): '1', ('1', '2'): '0', ('2', '2'): '2'
    }
    
    PHILOSOPHY = {
        '0': {'role': 'Zero / None', 'meaning': 'Tao (Pyx)', 'force': 'Equilibrium / Rest'},
        '1': {'role': 'One / Single', 'meaning': 'Yang (Vertex)', 'force': 'Outward motion'},
        '2': {'role': 'Two / Pair', 'meaning': 'Yin (Nexus)', 'force': 'Inward motion'}
    }

    @staticmethod
    def transition(t1: str, t2: str) -> str:
        """
        Apply transition between two ternary numbers.
        Pads with leading zeros to match length.
        """
        # Remove potential negative signs for the transition logic itself
        # (The philosophy seems to deal with raw digit patterns)
        t1_clean = t1.lstrip('-')
        t2_clean = t2.lstrip('-')
        
        max_len = max(len(t1_clean), len(t2_clean))
        t1_pad = t1_clean.zfill(max_len)
        t2_pad = t2_clean.zfill(max_len)
        
        result = []
        for d1, d2 in zip(t1_pad, t2_pad):
            # Default to '0' if invalid chars found, though input should be validated
            res_digit = TernaryTransitionService.TRANSITION_MAP.get((d1, d2), '0')
            result.append(res_digit)
            
        return "".join(result)

    @staticmethod
    def generate_sequence(start_t: str, modifier_t: str, iterations: int = 10) -> List[Tuple[str, str, str]]:
        """
        Generate a sequence of transitions.
        Returns list of (current, modifier, result).
        The result of one step becomes the current of the next.
        """
        sequence = []
        current = start_t
        
        for _ in range(iterations):
            result = TernaryTransitionService.transition(current, modifier_t)
            sequence.append((current, modifier_t, result))
            current = result
            
        return sequence

    @staticmethod
    def get_digit_info(digit: str) -> Dict[str, str]:
        """Get philosophical info for a digit."""
        return TernaryTransitionService.PHILOSOPHY.get(digit, {})
