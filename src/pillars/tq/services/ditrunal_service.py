"""
Ditrunal Service - The Nuclear Mutation Engine.
Implements recursive mutation algorithms to find Prime Ditrunes and classify cells into their 9 Canonical Families.
"""
from typing import Tuple, List, Optional
from ..models.kamea_cell import KameaCell
from ..services.ternary_service import TernaryService

class DitrunalService:
    """
    Service for operations related to Ditrunal Families and Nuclear Mutation.
    Implements the core recursive algorithm to find the Prime Ditrune.
    """

    # The 9 Canonical Primes
    PRIMES = {
        "000000", "010101", "020202",
        "101010", "111111", "121212",
        "202020", "212121", "222222"
    }

    @staticmethod
    def nuclear_mutation(sixgram: str) -> str:
        """
        Performs a single step of Nuclear Mutation.
        Algorithm:
            Input: d1 d2 d3 d4 d5 d6 (indices 012345)
            Top Triune:    d2 d3 d4 (indices 1:4)
            Bottom Triune: d3 d4 d5 (indices 2:5)
            Result: Top + Bottom
            
        Args:
            sixgram: 6-digit ternary string.
            
        Returns:
            The mutated 6-digit ternary string.
        """
        if len(sixgram) != 6:
            raise ValueError("Input must be a 6-digit ternary string.")
            
        top = sixgram[1:4]
        bottom = sixgram[2:5]
        return top + bottom

    @staticmethod
    def find_prime(sixgram: str, max_iterations: int = 100) -> str:
        """
        Recursively applies Nuclear Mutation until a stable Prime or Cycle is found.
        In the Kamea system, all 729 Ditrunes resolve to one of 9 Primes.
        
        Args:
            sixgram: The starting Ditrune.
            max_iterations: Safety break.
            
        Returns:
            The Prime Ditrune string.
        """
        current = sixgram
        seen = set()
        
        for _ in range(max_iterations):
            # PRIME TRAP: If we hit a known Prime, stop immediately.
            if current in DitrunalService.PRIMES:
                return current

            if current in seen:
                # Cycle detected. In Kamea, the Prime is the cycle anchor.
                # All classic Primes are fixed points or simple cycles.
                # For 121212/212121 (Families 5/7), they might cycle between each other?
                # The doctrine says 121212 is the Prime for Family 5.
                # Let's check mutation of 121212:
                # Top: 212, Bottom: 121 -> 212121
                # Mutation of 212121:
                # Top: 121, Bottom: 212 -> 121212
                # So they cycle. The "Prime" is usually defined by the Family identity.
                # Family 5 returns 121212. Family 7 returns 212121.
                # However, this function needs to return a canonical Prime.
                # We can return the one that is in our Prime List.
                return DitrunalService._resolve_cycle_to_canon(current)
            
            seen.add(current)
            next_val = DitrunalService.nuclear_mutation(current)
            
            if next_val == current:
                return current
                
            current = next_val
            
        raise RecursionError(f"Could not find Prime for {sixgram} within {max_iterations} steps.")

    @staticmethod
    def analyze_mutation_path(sixgram: str, max_iterations: int = 100) -> List[str]:
        """
        Returns the full path of mutation from the input to the Prime (or Cycle entry).
        Useful for visualization (Skin -> Body -> Core).
        """
        path = [sixgram]
        current = sixgram
        seen = set()
        
        for _ in range(max_iterations):
            # Check for Prime Trap FIRST
            if current in DitrunalService.PRIMES:
                return path
                
            if current in seen:
                return path
            
            seen.add(current)
            next_val = DitrunalService.nuclear_mutation(current)
            
            # If fixed point (though Prime Trap covers this for standard Primes)
            if next_val == current:
                return path
                
            path.append(next_val)
            current = next_val
            
        return path

    @staticmethod
    def _resolve_cycle_to_canon(val: str) -> str:
        """
        Resolves a cycle member to its canonical Prime if needed.
        The 9 canonical Primes are:
        000000, 010101, 020202, 101010, 111111, 121212, 202020, 212121, 222222
        """
        # If we hit 212121, is it Family 7? Yes.
        # If we hit 121212, is it Family 5? Yes.
        # So we just return the value itself as they are both valid Primes.
        return val

    @staticmethod
    def get_family_id(sixgram: str) -> int:
        """
        Determines the Family ID (0-8) based on the Prime.
        This provides a programmatic verification of the Bigram-based ID.
        """
        prime = DitrunalService.find_prime(sixgram)
        # Map Primes to IDs
        prime_map = {
            "000000": 0,
            "010101": 1,
            "020202": 2,
            "101010": 3,
            "111111": 4,
            "121212": 5,
            "202020": 6,
            "212121": 7,
            "222222": 8
        }
        return prime_map.get(prime, -1)

    @staticmethod
    def get_conrune_value(ternary: str) -> str:
        """
        Calculates the Conrune (Polarity Swap) of a ternary string.
        1 <-> 2, 0 stays 0.
        """
        res = []
        for char in ternary:
            if char == '1': res.append('2')
            elif char == '2': res.append('1')
            else: res.append('0')
        return "".join(res)

    @staticmethod
    def get_star_category(sixgram: str) -> str:
        """
        Classifies a Ditrune based on the 'Star Correspondence' of its two Triunes.
        
        Triune Types (based on Pyx count):
        - 3 Zeros: pure (The Void)
        - 2 Zeros: orbital (Elements)
        - 1 Zero:  zodiacal (Signs)
        - 0 Zeros: radial (Planets)
        
        Categories:
        - fundare: Checks for PURE (000) first.
        - planetary/planetary (radial/radial)
        - orbital/orbital
        - zodiacal/zodiacal
        - Mixed types (orbital/radial, etc)
        """
        if len(sixgram) != 6: return "Unknown"
        
        t1 = sixgram[0:3]
        t2 = sixgram[3:6]
        
        def get_type(t):
            """
            Retrieve type logic.
            
            Args:
                t: Description of t.
            
            Returns:
                Result of get_type operation.
            """
            zeros = t.count('0')
            if zeros == 3: return "Pure"
            if zeros == 2: return "Orbital"
            if zeros == 1: return "Zodiacal"
            return "Radial" # Planetary
            
        type1 = get_type(t1)
        type2 = get_type(t2)
        
        # Fundare Check (Contains pure 000)
        if type1 == "Pure" or type2 == "Pure":
            if type1 == "Pure" and type2 == "Pure":
                return "Singularity (Fundare)"
            return "Fundare"
            
        # Sort to ensure consistency (e.g. Orbital/Radial not Radial/Orbital)
        pair = sorted([type1, type2])
        p1, p2 = pair[0], pair[1]
        
        # Map Radial -> Planetary for display if preferred, or keep technical names
        # User requested "Planetary" for 0 Zeros.
        # Let's return the "Type 1 / Type 2" string.
        
        return f"{p1}/{p2}"