"""Unit tests for General n-gonal solids."""
import math
import pytest
from src.pillars.geometry.services.general_prismatic_solids import (
    GeneralPrismSolidService,
    GeneralPrismSolidCalculator,
)
from src.pillars.geometry.services.general_pyramid_solids import (
    GeneralPyramidSolidService,
    GeneralPyramidSolidCalculator,
)

class TestGeneralPrism:
    def test_dynamic_build_heptagon(self):
        """Test building a 7-sided prism."""
        result = GeneralPrismSolidService.build_dynamic(sides=7, base_edge=2.0, height=5.0)
        assert result.metrics.sides == 7
        assert result.metrics.base_edge == 2.0
        assert result.metrics.height == 5.0
        assert len(result.payload.vertices) == 14  # 7 top + 7 bottom
        assert result.metrics.volume == pytest.approx(result.metrics.base_area * 5.0)

    def test_calculator_property_update(self):
        """Test updating properties in the calculator."""
        calc = GeneralPrismSolidCalculator(sides=5, base_edge=2.0, height=4.0)
        props = {p.key: p.value for p in calc.properties()}
        assert props['sides'] == 5
        
        # Change sides to 6
        assert calc.set_property('sides', 6)
        props = {p.key: p.value for p in calc.properties()}
        assert props['sides'] == 6
        assert props['volume'] > 0

class TestGeneralPyramid:
    def test_dynamic_build_septagon(self):
        """Test building a 7-sided pyramid."""
        result = GeneralPyramidSolidService.build_dynamic(sides=7, base_edge=2.0, height=6.0)
        assert result.metrics.sides == 7
        assert result.metrics.base_edge == 2.0
        assert result.metrics.height == 6.0
        # Vertices = 7 base + 1 apex = 8
        assert len(result.payload.vertices) == 8
        assert result.metrics.volume == pytest.approx((result.metrics.base_area * 6.0) / 3.0)

    def test_calculator_property_update(self):
        """Test updating properties in the calculator."""
        calc = GeneralPyramidSolidCalculator(sides=5, base_edge=2.0, height=4.0)
        props = {p.key: p.value for p in calc.properties()}
        assert props['sides'] == 5
        
        # Change sides to 8
        assert calc.set_property('sides', 8)
        props = {p.key: p.value for p in calc.properties()}
        assert props['sides'] == 8
        
        # Check derived volume
        expected_volume = (props['base_area'] * props['height']) / 3.0
        assert props['volume'] == pytest.approx(expected_volume)
