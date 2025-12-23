"""ELS (Equidistant Letter Sequence) data models."""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict


@dataclass
class ELSInterveningSegment:
    """Represents the letters between two ELS hit letters."""
    from_letter: str
    to_letter: str
    letters: str  # The intervening letters (NOT including from/to)
    gematria_value: int = 0  # Calculated externally


@dataclass
class ELSResult:
    """Single ELS match result with gematria breakdown."""
    term: str
    skip: int
    start_pos: int  # Position in stripped text
    direction: str  # 'forward' | 'reverse'
    letter_positions: List[int] = field(default_factory=list)
    
    # Intervening letter analysis
    intervening_segments: List[ELSInterveningSegment] = field(default_factory=list)
    term_gematria: int = 0  # Gematria of the search term
    skip_gematria: int = 0  # Sum of all intervening letters' gematria
    
    @property
    def total_gematria(self) -> int:
        """Sum of term gematria + skip gematria."""
        return self.term_gematria + self.skip_gematria
    
    def get_row_col_coords(self, columns: int) -> List[Tuple[int, int]]:
        """Calculate (row, col) coordinates for current grid configuration."""
        if columns <= 0:
            return []
        return [(pos // columns, pos % columns) for pos in self.letter_positions]


@dataclass
class ELSSearchSummary:
    """Aggregated search results with metadata."""
    results: List[ELSResult] = field(default_factory=list)
    source_text_length: int = 0
    source_document: Optional[str] = None
    
    @property
    def total_hits(self) -> int:
        return len(self.results)
    
    @property
    def skip_distribution(self) -> dict:
        """Count of results per skip interval."""
        dist = {}
        for r in self.results:
            dist[r.skip] = dist.get(r.skip, 0) + 1
        return dist


@dataclass
class ChainStep:
    """Single step in a chain search path."""
    letter: str
    position: int
    interval: int  # Distance from previous letter (0 for first)
    intervening_letters: str = ""
    intervening_gematria: int = 0


@dataclass
class ChainResult:
    """Complete chain path through the text."""
    term: str
    steps: List[ChainStep] = field(default_factory=list)
    
    @property
    def positions(self) -> List[int]:
        return [s.position for s in self.steps]
    
    @property
    def total_length(self) -> int:
        """Total path length (last position - first position)."""
        if len(self.steps) < 2:
            return 0
        return self.steps[-1].position - self.steps[0].position
    
    @property
    def interval_sum(self) -> int:
        """Sum of all intervals."""
        return sum(s.interval for s in self.steps)
    
    @property
    def total_gematria(self) -> int:
        """Sum of all intervening letters' gematria."""
        return sum(s.intervening_gematria for s in self.steps)


@dataclass
class ChainSearchSummary:
    """Aggregated chain search results."""
    results: List[ChainResult] = field(default_factory=list)
    term: str = ""
    source_text_length: int = 0
