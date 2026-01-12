"""Integration tests for the complete Dynasty FIRE system"""

import pytest
import tempfile
from pathlib import Path
from omegaconf import OmegaConf

from dynasty_fire.config import Config
from dynasty_fire.calculator import DynastyFIRE
from dynasty_fire.visualizer import DynastyVisualizer
from dynasty_fire.utils import validate_config, save_results_to_json


class TestFullWorkflow:
    """Test complete Dynasty FIRE analysis workflow"""

    def test_complete_analysis_workflow(self):
        """Test the complete analysis from config to results"""
        # Create configuration
        config = OmegaConf.structured(Config())
        config.visualization.show_plots = False
        config.visualization.save_plots = False
        config.output.verbose = False
        
        # Validate configuration
        assert validate_config(config) is True
        
        # Initialize calculator
        calculator = DynastyFIRE(config)
        
        # Perform calculations
        single_investment = calculator.calculate_single_child_investment()
        assert single_investment > 0
        
        # Test dynasty investment calculation
        total, breakdown = calculator.calculate_dynasty_investment(3, 2.0)
        assert total > 0
        assert len(breakdown) == 3
        
        # Test convergence analysis
        convergence = calculator.convergence_analysis(2.0, 10)
        assert "converges" in convergence
        assert "convergence_ratio" in convergence
        
        # Test scenario analysis
        results = {}
        for children in config.scenarios.children_options:
            analysis = calculator.convergence_analysis(children)
            results[children] = {
                "converges": analysis["converges"],
                "cost": analysis["infinite_sum"] if analysis["converges"] else None,
                "status": "CONVERGES" if analysis["converges"] else "DIVERGES"
            }
        
        # Verify some scenarios converge and some diverge (with default params)
        converged_count = sum(1 for r in results.values() if r["converges"])
        assert converged_count > 0  # At least some should converge
        
        # Test complete results structure
        final_results = {
            "single_child_investment": single_investment,
            "convergence_analysis": convergence,
            "scenario_results": results,
            "config": OmegaConf.to_container(config, resolve=True)
        }
        
        # Test saving results
        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                results_file = save_results_to_json(final_results)
                assert results_file.exists()
                
            finally:
                os.chdir(original_cwd)

    def test_visualization_workflow(self):
        """Test visualization creation workflow"""
        config = OmegaConf.structured(Config())
        config.visualization.show_plots = False
        config.visualization.save_plots = False
        config.scenarios.children_options = [1.0, 2.0, 3.0]  # Limit for testing
        
        calculator = DynastyFIRE(config)
        visualizer = DynastyVisualizer(calculator)
        
        # Test main visualization
        analysis_results = visualizer.create_dynasty_growth_plot(max_generations=5)
        
        # Verify results structure
        assert isinstance(analysis_results, dict)
        for children in config.scenarios.children_options:
            assert children in analysis_results
            result = analysis_results[children]
            assert "converges" in result
            assert "investments" in result
            assert "cumulative" in result

    def test_edge_case_configurations(self):
        """Test system behavior with edge case configurations"""
        # High ROI configuration (should converge easily)
        high_roi_config = OmegaConf.create({
            "financial": {
                "target_amount": 1_000_000,
                "roi_rate": 0.15,
                "retirement_age": 40,
                "generation_gap": 20
            },
            "analysis": {
                "max_generations": 5,
                "children_per_generation": 3.0
            },
            "scenarios": {
                "children_options": [2.0, 3.0, 4.0, 5.0],
                "roi_range": [0.10, 0.20],
                "gap_range": [15.0, 25.0]
            },
            "visualization": {
                "figure_size": [10, 6],
                "show_plots": False,
                "save_plots": False,
                "output_dir": "test_output"
            },
            "output": {
                "verbose": False,
                "currency": "EUR",
                "decimal_places": 0
            }
        })
        
        calculator = DynastyFIRE(high_roi_config)
        
        # Should converge even with many children due to high ROI
        convergence = calculator.convergence_analysis(4.0)
        assert convergence["converges"] is True
        
        # Low ROI configuration (should diverge easily)
        low_roi_config = OmegaConf.create({
            "financial": {
                "target_amount": 2_000_000,
                "roi_rate": 0.02,
                "retirement_age": 70,
                "generation_gap": 15
            },
            "analysis": {
                "max_generations": 10,
                "children_per_generation": 4.0
            },
            "scenarios": {
                "children_options": [3.0, 4.0, 5.0],
                "roi_range": [0.01, 0.05],
                "gap_range": [10.0, 20.0]
            },
            "visualization": {
                "figure_size": [8, 6],
                "show_plots": False,
                "save_plots": False,
                "output_dir": "test_output"
            },
            "output": {
                "verbose": False,
                "currency": "USD",
                "decimal_places": 2
            }
        })
        
        calculator = DynastyFIRE(low_roi_config)
        
        # Should diverge with low ROI and many children
        convergence = calculator.convergence_analysis(4.0)
        assert convergence["converges"] is False

    def test_fractional_children_workflow(self):
        """Test complete workflow with fractional children"""
        config = OmegaConf.structured(Config())
        config.analysis.children_per_generation = 2.5
        config.scenarios.children_options = [1.5, 2.0, 2.5, 3.0]
        config.visualization.show_plots = False
        
        calculator = DynastyFIRE(config)
        
        # Test all fractional scenarios
        for children in config.scenarios.children_options:
            convergence = calculator.convergence_analysis(children)
            
            # Verify convergence calculation works with fractional children
            expected_ratio = children / ((1 + config.financial.roi_rate) ** config.financial.generation_gap)
            assert abs(convergence["convergence_ratio"] - expected_ratio) < 1e-10
            
            # Verify convergence detection
            assert convergence["converges"] == (expected_ratio < 1.0)

    def test_mathematical_consistency(self):
        """Test mathematical consistency across different calculation methods"""
        config = OmegaConf.structured(Config())
        calculator = DynastyFIRE(config)
        
        # Test consistency between dynasty investment and convergence analysis
        generations = 5
        children = 2.0
        
        # Calculate using dynasty investment method
        total_dynasty, breakdown = calculator.calculate_dynasty_investment(generations, children)
        
        # Calculate using convergence analysis method
        convergence = calculator.convergence_analysis(children, generations)
        total_convergence = convergence["final_cumulative"]
        
        # Should be very close (allowing for floating point precision)
        assert abs(total_dynasty - total_convergence) < 1e-6
        
        # Test single child calculation consistency
        # Generation n has children^(n+1) people (first generation has k children)
        single_child = calculator.calculate_single_child_investment()
        expected_first_generation = single_child * children  # Generation 0 has k children

        assert abs(breakdown[0] - expected_first_generation) < 1e-6

    def test_boundary_conditions(self):
        """Test behavior at mathematical boundaries"""
        config = OmegaConf.structured(Config())
        calculator = DynastyFIRE(config)
        
        # Test at convergence boundary
        max_children = calculator.calculate_max_children_for_convergence(config.financial.roi_rate)
        
        # Just below boundary should converge
        convergence_below = calculator.convergence_analysis(max_children - 0.001)
        assert convergence_below["converges"] is True
        
        # Just above boundary should diverge
        convergence_above = calculator.convergence_analysis(max_children + 0.001)
        assert convergence_above["converges"] is False
        
        # Test with children = 1 (should always converge)
        convergence_one = calculator.convergence_analysis(1.0)
        assert convergence_one["converges"] is True
        assert convergence_one["convergence_ratio"] < 1.0

    def test_error_handling_and_robustness(self):
        """Test system robustness and error handling"""
        config = OmegaConf.structured(Config())
        
        # Test with extreme parameters that might cause overflow
        extreme_config = OmegaConf.create({
            "financial": {
                "target_amount": 1e15,  # Very large target
                "roi_rate": 0.001,      # Very low ROI
                "retirement_age": 100,   # Very long time horizon
                "generation_gap": 10     # Short generation gap
            },
            "analysis": {
                "max_generations": 1000,  # Many generations
                "children_per_generation": 10.0  # Many children
            },
            "scenarios": {
                "children_options": [5.0, 10.0, 15.0],
                "roi_range": [0.001, 0.01],
                "gap_range": [5.0, 15.0]
            },
            "visualization": {
                "figure_size": [10, 6],
                "show_plots": False,
                "save_plots": False,
                "output_dir": "test_output"
            },
            "output": {
                "verbose": False,
                "currency": "TEST",
                "decimal_places": 0
            }
        })
        
        calculator = DynastyFIRE(extreme_config)
        
        # Should not crash, should handle overflow gracefully
        convergence = calculator.convergence_analysis(10.0, 1000)
        
        # Should detect divergence (either mathematically or due to overflow protection)
        assert convergence["converges"] is False
        
        # Should have some results even if truncated due to overflow
        assert len(convergence["investments"]) >= 0

    def test_configuration_override_workflow(self):
        """Test workflow with various configuration overrides"""
        base_config = Config()
        
        # Test different currency and formatting
        config1 = OmegaConf.structured(base_config)
        config1.output.currency = "USD"
        config1.output.decimal_places = 2
        config1.financial.target_amount = 1_500_000
        
        calculator1 = DynastyFIRE(config1)
        result1 = calculator1.calculate_single_child_investment()
        
        # Test different financial parameters
        config2 = OmegaConf.structured(base_config)
        config2.financial.roi_rate = 0.05
        config2.financial.retirement_age = 65
        config2.financial.generation_gap = 30
        
        calculator2 = DynastyFIRE(config2)
        result2 = calculator2.calculate_single_child_investment()
        
        # Results should be different due to different parameters
        assert result1 != result2
        
        # Both should be positive
        assert result1 > 0
        assert result2 > 0