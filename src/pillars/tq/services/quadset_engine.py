"""
Engine for Quadset calculations.
Orchestrates the transformation pipeline and generates the result model.
"""
from ..models import QuadsetResult, QuadsetMember
from ..services.ternary_service import TernaryService
from ..services.ternary_transition_service import TernaryTransitionService
from ..services.number_properties import NumberPropertiesService
from ..services.pattern_analyzer import PatternAnalyzer

class QuadsetEngine:
    """Orchestrates Quadset calculations."""

    def __init__(self):
        self.ternary_service = TernaryService()
        self.transition_service = TernaryTransitionService()
        self.pattern_analyzer = PatternAnalyzer()

    def calculate(self, decimal_input: int) -> QuadsetResult:
        """
        Perform a full Quadset analysis on a decimal number.
        
        Args:
            decimal_input: The starting decimal integer.
            
        Returns:
            A fully populated QuadsetResult object.
        """
        # 1. Original
        t_orig = self.ternary_service.decimal_to_ternary(decimal_input)
        m_original = self._create_member("Original", decimal_input, t_orig)

        # 2. Conrune
        t_conrune = self.ternary_service.conrune_transform(t_orig)
        d_conrune = self.ternary_service.ternary_to_decimal(t_conrune)
        m_conrune = self._create_member("Conrune", d_conrune, t_conrune)

        # 3. Reversal
        t_rev = self.ternary_service.reverse_ternary(t_orig)
        d_rev = self.ternary_service.ternary_to_decimal(t_rev)
        m_reversal = self._create_member("Reversal", d_rev, t_rev)

        # 4. Conrune of Reversal
        t_conrune_rev = self.ternary_service.conrune_transform(t_rev)
        d_conrune_rev = self.ternary_service.ternary_to_decimal(t_conrune_rev)
        m_conrune_rev = self._create_member("Conrune Reversal", d_conrune_rev, t_conrune_rev)

        # 5. Differentials
        diff_upper_val = abs(decimal_input - d_conrune)
        t_diff_upper = self.ternary_service.decimal_to_ternary(diff_upper_val)
        m_upper_diff = self._create_member("Upper Diff", diff_upper_val, t_diff_upper)

        diff_lower_val = abs(d_rev - d_conrune_rev)
        t_diff_lower = self.ternary_service.decimal_to_ternary(diff_lower_val)
        m_lower_diff = self._create_member("Lower Diff", diff_lower_val, t_diff_lower)

        # 6. Transgram & Totals
        quadset_sum = decimal_input + d_conrune + d_rev + d_conrune_rev
        
        t_transgram = self.transition_service.transition(t_diff_upper, t_diff_lower)
        d_transgram = self.ternary_service.ternary_to_decimal(t_transgram)
        m_transgram = self._create_member("Transgram", d_transgram, t_transgram)
        
        septad_total = quadset_sum + diff_upper_val + diff_lower_val + d_transgram

        # 7. Pattern Analysis
        members = [m_original, m_conrune, m_reversal, m_conrune_rev]
        pattern_report = self.pattern_analyzer.analyze(members)

        return QuadsetResult(
            original=m_original,
            conrune=m_conrune,
            reversal=m_reversal,
            conrune_reversal=m_conrune_rev,
            upper_diff=m_upper_diff,
            lower_diff=m_lower_diff,
            transgram=m_transgram,
            quadset_sum=quadset_sum,
            septad_total=septad_total,
            pattern_summary=pattern_report
        )

    def _create_member(self, name: str, decimal: int, ternary: str) -> QuadsetMember:
        """Helper to create a QuadsetMember with calculated properties."""
        props = NumberPropertiesService.get_properties(decimal)
        return QuadsetMember(name=name, decimal=decimal, ternary=ternary, properties=props)
