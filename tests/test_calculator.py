"""Unit tests for the Dynasty FIRE calculator module"""

import pytest
import math
from omegaconf import OmegaConf

from dynasty_fire.calculator import DynastyFIRE


class TestDynastyFIRE:
    """Test cases for the main DynastyFIRE calculator class"""

    def test_initialization(self, default_config):
        """Test that calculator initializes correctly with configuration"""
        calculator = DynastyFIRE(default_config)
        
        assert calculator.M == default_config.financial.target_amount
        assert calculator.R == default_config.financial.roi_rate
        assert calculator.Y == default_config.financial.retirement_age
        assert calculator.Y_c == default_config.financial.generation_gap

    def test_single_child_investment_calculation(self, dynasty_calculator):
        """Test basic single child investment calculation"""
        result = dynasty_calculator.calculate_single_child_investment()
        
        # Should be positive
        assert result > 0
        
        # Manual calculation: 10M / (1.07)^72
        expected = 10_000_000 / (1.07 ** 72)
        assert abs(result - expected) < 1e-6

    def test_single_child_investment_edge_cases(self):
        """Test single child calculation with edge case parameters"""
        # Very high ROI
        config = OmegaConf.create({
            "financial": {"target_amount": 1000000, "roi_rate": 0.5, "retirement_age": 10, "generation_gap": 25}
        })
        calculator = DynastyFIRE(config)
        result = calculator.calculate_single_child_investment()
        assert result > 0
        assert result < 1000000  # Should be much less than target due to high ROI

        # Very low ROI
        config.financial.roi_rate = 0.001
        calculator = DynastyFIRE(config)
        result = calculator.calculate_single_child_investment()
        assert result > 0
        assert result < 1000000  # Should still be less than target

    def test_dynasty_investment_single_generation(self, dynasty_calculator):
        """Test dynasty investment calculation for single generation"""
        total, breakdown = dynasty_calculator.calculate_dynasty_investment(1, 2.0)
        
        # For single generation (generation 0), we fund 2.0^0 = 1 person (the original)
        single_child = dynasty_calculator.calculate_single_child_investment()
        expected_first_generation = single_child * 1.0  # 2.0^0 = 1
        
        assert abs(total - expected_first_generation) < 1e-6
        assert len(breakdown) == 1
        assert abs(breakdown[0] - expected_first_generation) < 1e-6

    def test_dynasty_investment_multiple_generations(self, dynasty_calculator):
        """Test dynasty investment calculation for multiple generations"""
        total, breakdown = dynasty_calculator.calculate_dynasty_investment(3, 2.0)
        
        # Should have 3 generations
        assert len(breakdown) == 3
        
        # Total should be sum of breakdown
        assert abs(total - sum(breakdown)) < 1e-6
        
        # Later generations should require less investment (more time to compound)
        assert breakdown[0] > breakdown[1] > breakdown[2]

    def test_dynasty_investment_fractional_children(self, dynasty_calculator):
        """Test dynasty investment with fractional children"""
        total_int, _ = dynasty_calculator.calculate_dynasty_investment(2, 2.0)
        total_frac, _ = dynasty_calculator.calculate_dynasty_investment(2, 2.5)
        
        # More children should require more investment
        assert total_frac > total_int

    def test_convergence_analysis_convergent_case(self, dynasty_calculator):
        """Test convergence analysis for a case that should converge"""
        result = dynasty_calculator.convergence_analysis(children_per_generation=2.0)
        
        # Should converge with default parameters (2 children, 7% ROI, 25-year gap)
        assert result["converges"] is True
        assert result["convergence_ratio"] < 1
        assert result["infinite_sum"] is not None
        assert result["infinite_sum"] > 0
        
        # Check that convergence ratio matches manual calculation
        expected_ratio = 2.0 / ((1.07) ** 25)
        assert abs(result["convergence_ratio"] - expected_ratio) < 1e-6

    def test_convergence_analysis_divergent_case(self, dynasty_calculator):
        """Test convergence analysis for a case that should diverge"""
        result = dynasty_calculator.convergence_analysis(children_per_generation=10.0)
        
        # Should diverge with 10 children per generation
        assert result["converges"] is False
        assert result["convergence_ratio"] > 1
        assert result["infinite_sum"] is None

    def test_convergence_analysis_boundary_case(self):
        """Test convergence analysis at the exact boundary"""
        # Create config where convergence ratio is very close to 1
        config = OmegaConf.create({
            "financial": {"target_amount": 1000000, "roi_rate": 0.03, "retirement_age": 50, "generation_gap": 15}
        })
        calculator = DynastyFIRE(config)
        
        # Calculate the exact boundary
        boundary_children = (1.03) ** 15  # Should be around 1.56
        
        # Just below boundary should converge
        result_converge = calculator.convergence_analysis(children_per_generation=boundary_children - 0.01)
        assert result_converge["converges"] is True
        
        # Just above boundary should diverge
        result_diverge = calculator.convergence_analysis(children_per_generation=boundary_children + 0.01)
        assert result_diverge["converges"] is False

    def test_convergence_analysis_edge_cases(self, dynasty_calculator):
        """Test convergence analysis with edge case inputs"""
        # Single child should always converge
        result = dynasty_calculator.convergence_analysis(children_per_generation=1.0)
        assert result["converges"] is True
        assert result["convergence_ratio"] < 1

        # Fractional children less than 1 should converge
        result = dynasty_calculator.convergence_analysis(children_per_generation=0.5)
        assert result["converges"] is True

    def test_sensitivity_analysis_structure(self, dynasty_calculator):
        """Test that sensitivity analysis returns correct structure"""
        result = dynasty_calculator.sensitivity_analysis()
        
        # Check required keys exist
        assert "base_investment" in result
        assert "roi_sensitivity" in result
        assert "gap_sensitivity" in result
        
        # Check ROI sensitivity structure
        roi_sens = result["roi_sensitivity"]
        assert "rates" in roi_sens
        assert "investments" in roi_sens
        assert len(roi_sens["rates"]) == len(roi_sens["investments"])
        
        # Check gap sensitivity structure
        gap_sens = result["gap_sensitivity"]
        assert "gaps" in gap_sens
        assert "convergence" in gap_sens
        assert len(gap_sens["gaps"]) == len(gap_sens["convergence"])

    def test_sensitivity_analysis_roi_relationship(self, dynasty_calculator):
        """Test that ROI sensitivity shows correct relationship"""
        result = dynasty_calculator.sensitivity_analysis()
        
        roi_rates = result["roi_sensitivity"]["rates"]
        investments = result["roi_sensitivity"]["investments"]
        
        # Higher ROI should require lower initial investment
        for i in range(len(roi_rates) - 1):
            if roi_rates[i] < roi_rates[i + 1]:
                assert investments[i] > investments[i + 1]

    def test_calculate_convergence_boundary(self, dynasty_calculator):
        """Test convergence boundary calculation"""
        # For 1 child, boundary should be 0
        boundary = dynasty_calculator.calculate_convergence_boundary(1.0)
        assert boundary == 0.0
        
        # For less than 1 child, boundary should be 0
        boundary = dynasty_calculator.calculate_convergence_boundary(0.5)
        assert boundary == 0.0
        
        # For more than 1 child, boundary should be positive
        boundary = dynasty_calculator.calculate_convergence_boundary(2.0)
        assert boundary > 0
        
        # Manual calculation for 2 children with 25-year gap
        # 2 = (1 + R)^25, so R = 2^(1/25) - 1
        expected = 2.0**(1/25) - 1
        assert abs(boundary - expected) < 1e-6

    def test_calculate_max_children_for_convergence(self, dynasty_calculator):
        """Test maximum children calculation"""
        # With 7% ROI and 25-year gap
        max_children = dynasty_calculator.calculate_max_children_for_convergence(0.07)
        
        # Should equal (1.07)^25
        expected = (1.07) ** 25
        assert abs(max_children - expected) < 1e-6
        
        # Higher ROI should allow more children
        max_children_high = dynasty_calculator.calculate_max_children_for_convergence(0.10)
        assert max_children_high > max_children

    def test_overflow_protection(self):
        """Test that calculator handles potential overflow gracefully"""
        config = OmegaConf.create({
            "financial": {"target_amount": 1e50, "roi_rate": 0.01, "retirement_age": 200, "generation_gap": 10}
        })
        calculator = DynastyFIRE(config)
        
        # Should not crash with extreme parameters
        result = calculator.convergence_analysis(children_per_generation=50.0, max_generations=1000)
        
        # Should detect divergence due to overflow protection
        assert result["converges"] is False or len(result["investments"]) < 1000

    def test_numerical_stability(self):
        """Test numerical stability with parameters close to boundary"""
        config = OmegaConf.create({
            "financial": {"target_amount": 1000000, "roi_rate": 0.0001, "retirement_age": 50, "generation_gap": 50}
        })
        calculator = DynastyFIRE(config)
        
        # Very close to convergence boundary
        boundary = calculator.calculate_max_children_for_convergence(0.0001)
        
        # Test convergence analysis near boundary
        result = calculator.convergence_analysis(children_per_generation=boundary - 1e-10)
        
        # Should handle numerical precision issues gracefully
        assert isinstance(result["converges"], bool)
        if result["converges"]:
            assert result["infinite_sum"] is None or result["infinite_sum"] > 0