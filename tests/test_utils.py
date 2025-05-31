"""Unit tests for utility functions"""

import pytest
import json
import tempfile
from pathlib import Path
from omegaconf import OmegaConf

from dynasty_fire.utils import (
    format_children_text,
    save_results_to_json,
    save_summary_report,
    calculate_years_to_double,
    format_currency,
    validate_config
)
from dynasty_fire.config import Config


class TestFormatChildrenText:
    """Test cases for format_children_text function"""

    def test_whole_numbers(self):
        """Test formatting of whole numbers"""
        assert format_children_text(1.0) == "1"
        assert format_children_text(2.0) == "2"
        assert format_children_text(10.0) == "10"

    def test_fractional_numbers(self):
        """Test formatting of fractional numbers"""
        assert format_children_text(1.5) == "1.5"
        assert format_children_text(2.3) == "2.3"
        assert format_children_text(0.8) == "0.8"

    def test_edge_cases(self):
        """Test edge cases"""
        assert format_children_text(0.0) == "0"
        assert format_children_text(1.00000001) == "1.0"  # Close to integer
        assert format_children_text(2.99999999) == "3.0"  # Close to integer


class TestSaveResultsToJson:
    """Test cases for save_results_to_json function"""

    def test_basic_save(self):
        """Test basic JSON saving functionality"""
        test_data = {
            "single_child_investment": 100000.0,
            "convergence_analysis": {"converges": True, "ratio": 0.5},
            "scenario_results": {1: {"cost": 50000, "status": "CONVERGES"}}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock Hydra output directory
            import dynasty_fire.utils
            original_hydra = dynasty_fire.utils.HydraConfig
            
            class MockHydraConfig:
                @staticmethod
                def get():
                    class MockRuntime:
                        output_dir = temp_dir
                    class MockConfig:
                        runtime = MockRuntime()
                    return MockConfig()
            
            dynasty_fire.utils.HydraConfig = MockHydraConfig
            
            try:
                result_file = save_results_to_json(test_data)
                
                # Verify file was created
                assert result_file.exists()
                assert result_file.name == "dynasty_results.json"
                
                # Verify content
                with open(result_file, 'r') as f:
                    loaded_data = json.load(f)
                
                assert loaded_data["single_child_investment"] == 100000.0
                assert loaded_data["convergence_analysis"]["converges"] is True
                
            finally:
                dynasty_fire.utils.HydraConfig = original_hydra

    def test_custom_filename(self):
        """Test saving with custom filename"""
        test_data = {"test": "data"}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            import os
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                result_file = save_results_to_json(test_data, "custom_results.json")
                
                assert result_file.exists()
                assert result_file.name == "custom_results.json"
                
            finally:
                os.chdir(original_cwd)


class TestSaveSummaryReport:
    """Test cases for save_summary_report function"""

    def test_basic_report_generation(self):
        """Test basic summary report generation"""
        config = OmegaConf.structured(Config())
        results = {
            "single_child_investment": 76625.0,
            "convergence_analysis": {
                "converges": True,
                "convergence_ratio": 0.3685,
                "infinite_sum": 121337.0
            },
            "scenario_results": {
                1.0: {"converges": True, "cost": 93931.0, "status": "CONVERGES"},
                2.0: {"converges": True, "cost": 121337.0, "status": "CONVERGES"},
                3.0: {"converges": False, "cost": None, "status": "DIVERGES"}
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                report_file = save_summary_report(results, config)
                
                assert report_file.exists()
                assert report_file.name == "summary_report.txt"
                
                # Verify content structure
                content = report_file.read_text()
                assert "FIRE for Your Dynasty - Analysis Summary" in content
                assert "Configuration:" in content
                assert "Key Results:" in content
                assert "Scenario Analysis:" in content
                assert "1 children per generation: CONVERGES" in content
                assert "3 children per generation: DIVERGES - ∞ (infinite)" in content
                
            finally:
                os.chdir(original_cwd)


class TestCalculateYearsToDouble:
    """Test cases for calculate_years_to_double function"""

    def test_standard_rates(self):
        """Test with standard interest rates"""
        # Rule of 72: 72 / (rate * 100)
        assert abs(calculate_years_to_double(0.06) - 12.0) < 0.001  # 6% -> 12 years
        assert abs(calculate_years_to_double(0.08) - 9.0) < 0.001   # 8% -> 9 years
        assert abs(calculate_years_to_double(0.12) - 6.0) < 0.001   # 12% -> 6 years

    def test_edge_cases(self):
        """Test edge cases"""
        assert calculate_years_to_double(0.0) == float('inf')
        assert calculate_years_to_double(-0.05) == float('inf')
        
        # Very small positive rate
        result = calculate_years_to_double(0.001)  # 0.1%
        assert result == 720.0  # 72 / (0.1 * 100) = 72 / 0.1 where 0.1 is the percentage

    def test_high_rates(self):
        """Test with high interest rates"""
        result = calculate_years_to_double(1.0)  # 100%
        assert abs(result - 0.72) < 0.001


class TestFormatCurrency:
    """Test cases for format_currency function"""

    def test_basic_formatting(self):
        """Test basic currency formatting"""
        assert format_currency(1000.0) == "1,000 DKK"
        assert format_currency(1000000.0) == "1,000,000 DKK"
        assert format_currency(1500.75, decimal_places=2) == "1,500.75 DKK"

    def test_custom_currency(self):
        """Test with different currencies"""
        assert format_currency(1000.0, currency="USD") == "1,000 USD"
        assert format_currency(2500.0, currency="EUR") == "2,500 EUR"

    def test_decimal_places(self):
        """Test different decimal place settings"""
        amount = 1234.567
        assert format_currency(amount, decimal_places=0) == "1,235 DKK"
        assert format_currency(amount, decimal_places=1) == "1,234.6 DKK"
        assert format_currency(amount, decimal_places=2) == "1,234.57 DKK"

    def test_none_value(self):
        """Test handling of None values (infinite)"""
        assert format_currency(None) == "∞ (infinite)"
        assert format_currency(None, currency="USD") == "∞ (infinite)"

    def test_zero_and_negative(self):
        """Test zero and negative values"""
        assert format_currency(0.0) == "0 DKK"
        assert format_currency(-1000.0) == "-1,000 DKK"


class TestValidateConfig:
    """Test cases for validate_config function"""

    def test_valid_config(self):
        """Test that valid config passes validation"""
        config = OmegaConf.structured(Config())
        assert validate_config(config) is True

    def test_invalid_financial_params(self):
        """Test validation with invalid financial parameters"""
        config = OmegaConf.structured(Config())
        
        # Test negative target amount
        config.financial.target_amount = -1000
        with pytest.raises(ValueError, match="Target amount must be positive"):
            validate_config(config)
        
        # Reset and test zero ROI
        config.financial.target_amount = 1000000
        config.financial.roi_rate = 0.0
        with pytest.raises(ValueError, match="ROI rate must be positive"):
            validate_config(config)
        
        # Reset and test negative retirement age
        config.financial.roi_rate = 0.07
        config.financial.retirement_age = -5
        with pytest.raises(ValueError, match="Retirement age must be positive"):
            validate_config(config)
        
        # Reset and test zero generation gap
        config.financial.retirement_age = 65
        config.financial.generation_gap = 0
        with pytest.raises(ValueError, match="Generation gap must be positive"):
            validate_config(config)

    def test_invalid_analysis_params(self):
        """Test validation with invalid analysis parameters"""
        config = OmegaConf.structured(Config())
        
        # Test zero max generations
        config.analysis.max_generations = 0
        with pytest.raises(ValueError, match="Max generations must be positive"):
            validate_config(config)
        
        # Reset and test negative children
        config.analysis.max_generations = 10
        config.analysis.children_per_generation = -1.5
        with pytest.raises(ValueError, match="Children per generation must be positive"):
            validate_config(config)

    def test_invalid_scenarios_params(self):
        """Test validation with invalid scenario parameters"""
        config = OmegaConf.structured(Config())
        
        # Test empty children options
        config.scenarios.children_options = []
        with pytest.raises(ValueError, match="Children options cannot be empty"):
            validate_config(config)
        
        # Reset and test negative children option
        config.scenarios.children_options = [1.0, -2.0, 3.0]
        with pytest.raises(ValueError, match="All children options must be positive"):
            validate_config(config)

    def test_edge_case_valid_values(self):
        """Test validation with edge case valid values"""
        config = OmegaConf.structured(Config())
        
        # Very small positive values should be valid
        config.financial.roi_rate = 0.0001
        config.financial.generation_gap = 0.1
        config.analysis.children_per_generation = 0.1
        
        assert validate_config(config) is True

    def test_fractional_children_validation(self):
        """Test validation with fractional children values"""
        config = OmegaConf.structured(Config())
        
        # Fractional children should be valid
        config.analysis.children_per_generation = 1.5
        config.scenarios.children_options = [0.5, 1.5, 2.5, 3.5]
        
        assert validate_config(config) is True