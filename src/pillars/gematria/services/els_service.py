"""ELS (Equidistant Letter Sequence) Search Service.

Implements the Bible Code search algorithm for finding hidden words
by sampling every n-th letter from sacred texts.
"""
import logging
from typing import List, Tuple, Optional
import re

from ..models.els_models import (
    ELSResult, ELSSearchSummary, ELSInterveningSegment,
    ChainResult, ChainStep, ChainSearchSummary
)


logger = logging.getLogger(__name__)


class ELSSearchService:
    """Equidistant Letter Sequence (Bible Code) search engine."""
    
    def prepare_text(self, text: str, keep_spaces: bool = False) -> Tuple[str, List[int]]:
        """
        Strip text of non-letters, return stripped text and position map.
        
        Args:
            text: Raw source text
            keep_spaces: If True, preserve spaces (usually False for ELS)
            
        Returns:
            Tuple of (stripped_text, original_position_map) where
            original_position_map[i] = position in original text
        """
        stripped = []
        position_map = []
        
        for i, char in enumerate(text):
            if char.isalpha():
                stripped.append(char)
                position_map.append(i)
            elif keep_spaces and char == ' ':
                stripped.append(char)
                position_map.append(i)
        
        return ''.join(stripped), position_map
    
    def get_grid_factors(self, n: int, include_common: bool = True) -> List[Tuple[int, int]]:
        """
        Calculate grid dimensions, handling primes and sparse factor counts.
        
        For prime or sparsely-factorable counts, includes common widths
        which will result in incomplete last rows (which is fine for ELS).
        
        Args:
            n: Total letter count
            include_common: Include common widths (10, 20, 50, etc.) even if not factors
            
        Returns:
            List of (columns, rows) tuples, sorted by squareness
        """
        if n <= 1:
            return [(1, n)] if n == 1 else []
        
        # Find exact factors
        factors = set()
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                factors.add((i, n // i))
                if i != n // i:
                    factors.add((n // i, i))
        
        # If no factors (prime) or very few factors, add common widths
        common_widths = [10, 20, 22, 26, 30, 40, 50, 64, 72, 80, 100]
        # For small texts, add smaller widths
        if n < 20:
            common_widths = list(range(2, min(n, 10))) + common_widths
        
        if include_common and len(factors) < 4:
            for w in common_widths:
                if 2 <= w < n:
                    rows = (n + w - 1) // w  # Ceiling division
                    factors.add((w, rows))
        
        # Always ensure at least some options exist
        if not factors:
            # Fallback: suggest widths that give reasonable row counts
            for w in common_widths:
                if 2 <= w < n:
                    rows = (n + w - 1) // w
                    factors.add((w, rows))
        
        # Sort by "squareness" (prefer grids closer to square shape)
        result = sorted(factors, key=lambda x: abs(x[0] - x[1]))  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType, reportUnknownVariableType]
        return result
    
    def suggest_better_counts(self, n: int, search_range: int = 10) -> List[Tuple[int, int]]:
        """
        Suggest nearby letter counts with better factorization.
        
        Useful when current count is prime - suggests padding or trimming.
        
        Args:
            n: Current letter count
            search_range: How far to search (+/- this many letters)
            
        Returns:
            List of (nearby_count, factor_count) sorted by factor_count desc
        """
        suggestions = []
        for offset in range(-search_range, search_range + 1):
            candidate = n + offset
            if candidate <= 1:
                continue
            
            # Count factors
            factor_count = 0
            for i in range(2, int(candidate**0.5) + 1):
                if candidate % i == 0:
                    factor_count += 2 if i != candidate // i else 1
            
            if factor_count > 0:
                suggestions.append((candidate, factor_count, offset))
        
        # Sort by factor count (descending), then by closeness to original
        suggestions.sort(key=lambda x: (-x[1], abs(x[2])))  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType, reportUnknownMemberType]
        return [(s[0], s[1]) for s in suggestions[:5]]  # Top 5
    
    def search_els(
        self,
        text: str,
        term: str,
        skip: Optional[int] = None,
        min_skip: int = 1,
        max_skip: int = 100,
        direction: str = 'both'
    ) -> ELSSearchSummary:
        """
        Search for ELS patterns in text.
        
        Args:
            text: Source text (already stripped or will be stripped)
            term: Word/sequence to search for
            skip: Exact skip interval (if set, ignores min/max)
            min_skip: Minimum skip interval for range search
            max_skip: Maximum skip interval for range search
            direction: 'forward', 'reverse', or 'both'
            
        Returns:
            ELSSearchSummary with all matches
        """
        if not text or not term:
            return ELSSearchSummary()
        
        # Prepare text (strip non-letters)
        stripped, _ = self.prepare_text(text)
        term_upper = term.upper()
        stripped_upper = stripped.upper()
        
        results = []
        
        # Determine skip range
        if skip is not None:
            skip_range = [skip]
        else:
            skip_range = range(min_skip, max_skip + 1)
        
        # Forward search
        if direction in ('forward', 'both'):
            for s in skip_range:
                results.extend(self._search_direction(
                    stripped_upper, term_upper, s, 'forward'
                ))
        
        # Reverse search
        if direction in ('reverse', 'both'):
            for s in skip_range:
                results.extend(self._search_direction(
                    stripped_upper, term_upper, s, 'reverse'
                ))
        
        logger.info(f"ELS search for '{term}' found {len(results)} matches")
        
        return ELSSearchSummary(
            results=results,
            source_text_length=len(stripped)
        )
    
    def _search_direction(
        self,
        text: str,
        term: str,
        skip: int,
        direction: str
    ) -> List[ELSResult]:
        """Search in a single direction with given skip."""
        results = []
        n = len(text)
        term_len = len(term)
        
        if skip <= 0 or term_len == 0:
            return results
        
        # Calculate max starting position
        # Need: start + (term_len - 1) * skip < n
        max_start = n - (term_len - 1) * skip - 1
        
        if max_start < 0:
            return results
        
        search_text = text if direction == 'forward' else text[::-1]
        
        for start in range(max_start + 1):
            # Extract characters at skip intervals
            positions = [start + i * skip for i in range(term_len)]
            extracted = ''.join(search_text[p] for p in positions)
            
            if extracted == term:
                # Convert positions back if reverse
                if direction == 'reverse':
                    actual_positions = [n - 1 - p for p in positions]
                else:
                    actual_positions = positions
                
                results.append(ELSResult(
                    term=term,
                    skip=skip,
                    start_pos=actual_positions[0],
                    direction=direction,
                    letter_positions=actual_positions
                ))
        
        return results
    
    def extract_intervening_letters(
        self,
        text: str,
        positions: List[int],
        term: str
    ) -> List[ELSInterveningSegment]:
        """
        Extract the letters between each pair of ELS hit positions.
        
        For term "AMUN" with positions [0, 50, 100, 150], extracts:
        - A-M: letters at positions 1-49 (not including 0 and 50)
        - M-U: letters at positions 51-99
        - U-N: letters at positions 101-149
        
        Args:
            text: The stripped source text
            positions: List of positions where each term letter was found
            term: The search term (for labeling)
            
        Returns:
            List of ELSInterveningSegment
        """
        segments = []
        
        for i in range(len(positions) - 1):
            start_pos = positions[i]
            end_pos = positions[i + 1]
            from_letter = term[i] if i < len(term) else '?'
            to_letter = term[i + 1] if i + 1 < len(term) else '?'
            
            # Extract letters between (exclusive of start and end)
            if end_pos > start_pos:
                # Forward direction
                intervening = text[start_pos + 1:end_pos]
            else:
                # Reverse direction
                intervening = text[end_pos + 1:start_pos]
            
            segments.append(ELSInterveningSegment(
                from_letter=from_letter,
                to_letter=to_letter,
                letters=intervening,
                gematria_value=0  # Calculated by UI/calculator
            ))
        
        return segments

    
    def build_matrix(self, text: str, columns: int) -> List[List[str]]:
        """
        Arrange stripped text into a grid for visualization.
        
        Args:
            text: Stripped text (letters only)
            columns: Number of columns in grid
            
        Returns:
            2D list of characters, row-major order
        """
        if columns <= 0:
            return []
        
        matrix = []
        row = []
        
        for char in text:
            row.append(char)
            if len(row) == columns:
                matrix.append(row)
                row = []
        
        # Add partial last row if any
        if row:
            matrix.append(row)
        
        return matrix
    
    # === Arithmetical Sequence Search ===
    
    def generate_triangular_positions(self, start: int, term_len: int, max_pos: int) -> List[int]:
        """Generate positions using triangular numbers: 0, 1, 3, 6, 10..."""
        positions = [start]
        for i in range(1, term_len):
            next_pos = start + (i * (i + 1)) // 2
            if next_pos >= max_pos:
                return []  # Doesn't fit
            positions.append(next_pos)
        return positions
    
    def generate_square_positions(self, start: int, term_len: int, max_pos: int) -> List[int]:
        """Generate positions using square numbers: 0, 1, 4, 9, 16..."""
        positions = [start]
        for i in range(1, term_len):
            next_pos = start + i * i
            if next_pos >= max_pos:
                return []
            positions.append(next_pos)
        return positions
    
    def generate_fibonacci_positions(self, start: int, term_len: int, max_pos: int) -> List[int]:
        """Generate positions using cumulative Fibonacci skips: 0, 1, 2, 4, 7, 12, 20..."""
        # Build Fibonacci sequence for skip distances
        fib = [1, 1]
        while len(fib) < term_len:
            fib.append(fib[-1] + fib[-2])
        
        # Create cumulative positions
        positions = [start]
        cumulative = 0
        for i in range(1, term_len):
            cumulative += fib[i - 1]
            pos = start + cumulative
            if pos >= max_pos:
                return []
            positions.append(pos)
        return positions
    
    def search_sequence(
        self,
        text: str,
        term: str,
        sequence_type: str = 'triangular',
        direction: str = 'both'
    ) -> ELSSearchSummary:
        """
        Search for patterns using arithmetical sequences.
        
        Args:
            text: Source text
            term: Word to search for
            sequence_type: 'triangular', 'square', or 'fibonacci'
            direction: 'forward', 'reverse', or 'both'
            
        Returns:
            ELSSearchSummary with matches
        """
        if not text or not term:
            return ELSSearchSummary()
        
        stripped, _ = self.prepare_text(text)
        term_upper = term.upper()
        stripped_upper = stripped.upper()
        n = len(stripped_upper)
        term_len = len(term_upper)
        
        results = []
        
        # Choose sequence generator
        if sequence_type == 'triangular':
            gen_func = self.generate_triangular_positions
        elif sequence_type == 'square':
            gen_func = self.generate_square_positions
        elif sequence_type == 'fibonacci':
            gen_func = self.generate_fibonacci_positions
        else:
            return ELSSearchSummary()
        
        # Search forward
        if direction in ('forward', 'both'):
            for start in range(n):
                positions = gen_func(start, term_len, n)
                if positions and len(positions) == term_len:
                    extracted = ''.join(stripped_upper[p] for p in positions)
                    if extracted == term_upper:
                        results.append(ELSResult(
                            term=term_upper,
                            skip=0,  # Not applicable for sequences
                            start_pos=start,
                            direction='forward',
                            letter_positions=positions
                        ))
        
        # Search reverse
        if direction in ('reverse', 'both'):
            reversed_text = stripped_upper[::-1]
            for start in range(n):
                positions = gen_func(start, term_len, n)
                if positions and len(positions) == term_len:
                    extracted = ''.join(reversed_text[p] for p in positions)
                    if extracted == term_upper:
                        # Convert to original positions
                        actual_positions = [n - 1 - p for p in positions]
                        results.append(ELSResult(
                            term=term_upper,
                            skip=0,
                            start_pos=actual_positions[0],
                            direction='reverse',
                            letter_positions=actual_positions
                        ))
        
        logger.info(f"Sequence search ({sequence_type}) for '{term}' found {len(results)} matches")
        
        return ELSSearchSummary(
            results=results,
            source_text_length=len(stripped)
        )
    
    # === Chain Search ===
    
    def search_chain(
        self,
        text: str,
        term: str,
        reverse: bool = False,
        max_results: int = 0  # 0 = unlimited
    ) -> ChainSearchSummary:
        """
        Search for term by finding nearest occurrence of each letter in sequence.
        
        For 'ABCD' (forward):
        1. Find each 'A' as starting point
        2. From each A, find the next 'B' (closest forward)
        3. From B, find the next 'C'
        4. Continue until term complete
        
        For reverse: search backwards from each starting position.
        
        Args:
            text: Source text
            term: Word to search for
            reverse: If True, search backwards (find previous occurrence)
            max_results: Maximum results to return (for performance)
            
        Returns:
            ChainSearchSummary with all paths found
        """
        if not text or not term:
            return ChainSearchSummary()
        
        stripped, _ = self.prepare_text(text)
        term_upper = term.upper()
        stripped_upper = stripped.upper()
        n = len(stripped_upper)
        term_len = len(term_upper)
        
        results = []
        
        # Find all starting positions (first letter)
        first_letter = term_upper[0]
        start_positions = [i for i, c in enumerate(stripped_upper) if c == first_letter]
        
        for start_pos in start_positions:
            if max_results > 0 and len(results) >= max_results:
                break
                
            # Try to build a complete chain from this start
            steps = []
            current_pos = start_pos
            
            for letter_idx, letter in enumerate(term_upper):
                if letter_idx == 0:
                    # First letter
                    steps.append(ChainStep(
                        letter=letter,
                        position=current_pos,
                        interval=0,
                        intervening_letters="",
                        intervening_gematria=0
                    ))
                else:
                    # Find next/previous occurrence of this letter
                    next_pos = None
                    
                    if reverse:
                        # Search backwards
                        for i in range(current_pos - 1, -1, -1):
                            if stripped_upper[i] == letter:
                                next_pos = i
                                break
                    else:
                        # Search forwards
                        for i in range(current_pos + 1, n):
                            if stripped_upper[i] == letter:
                                next_pos = i
                                break
                    
                    if next_pos is None:
                        # Can't complete chain from this start
                        break
                    
                    interval = abs(next_pos - current_pos)
                    if reverse:
                        intervening = stripped_upper[next_pos + 1:current_pos]
                    else:
                        intervening = stripped_upper[current_pos + 1:next_pos]
                    
                    steps.append(ChainStep(
                        letter=letter,
                        position=next_pos,
                        interval=interval,
                        intervening_letters=intervening,
                        intervening_gematria=0  # Calculated by UI
                    ))
                    current_pos = next_pos
            
            # Only add complete chains
            if len(steps) == term_len:
                results.append(ChainResult(
                    term=term_upper,
                    steps=steps
                ))
        
        direction_str = "reverse" if reverse else "forward"
        logger.info(f"Chain search ({direction_str}) for '{term}' found {len(results)} paths")
        
        return ChainSearchSummary(
            results=results,
            term=term_upper,
            source_text_length=len(stripped)
        )


# Singleton instance for convenience
els_service = ELSSearchService()
