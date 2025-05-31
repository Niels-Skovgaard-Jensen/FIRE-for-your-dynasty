"""Unit tests for the configuration module"""

import pytest
from omegaconf import OmegaConf

from dynasty_fire.config import (
    FinancialConfig,
    AnalysisConfig,
    ScenariosConfig,
    VisualizationConfig,
    OutputConfig,
    Config
)


class TestFinancialConfig:
    """Test cases for FinancialConfig"""

    def test_default_values(self):
        """Test that default values are set correctly"""
        config = FinancialConfig()
        
        assert config.target_amount == 10_000_000
        assert config.roi_rate == 0.07
        assert config.retirement_age == 72
        assert config.generation_gap == 25

    def test_custom_values(self):
        """Test setting custom values"""
        config = FinancialConfig(
            target_amount=5_000_000,
            roi_rate=0.05,
            retirement_age=65,
            generation_gap=30
        )
        
        assert config.target_amount == 5_000_000
        assert config.roi_rate == 0.05
        assert config.retirement_age == 65
        assert config.generation_gap == 30


class TestAnalysisConfig:
    """Test cases for AnalysisConfig"""

    def test_default_values(self):
        """Test that default values are set correctly"""
        config = AnalysisConfig()
        
        assert config.max_generations == 20
        assert config.children_per_generation == 2.0

    def test_fractional_children(self):
        """Test that fractional children are supported"""
        config = AnalysisConfig(children_per_generation=2.5)
        
        assert config.children_per_generation == 2.5
        assert isinstance(config.children_per_generation, float)


class TestScenariosConfig:
    """Test cases for ScenariosConfig"""

    def test_default_values(self):
        """Test that default values are set correctly"""
        config = ScenariosConfig()
        
        assert config.children_options == [1.0, 2.0, 3.0, 4.0]
        assert config.roi_range == [0.03, 0.12]
        assert config.gap_range == [15.0, 35.0]

    def test_custom_children_options(self):
        """Test setting custom children options"""
        custom_options = [1.0, 1.5, 2.0, 2.5, 3.0]
        config = ScenariosConfig(children_options=custom_options)
        
        assert config.children_options == custom_options

    def test_custom_ranges(self):
        """Test setting custom ranges"""
        config = ScenariosConfig(
            roi_range=[0.02, 0.15],
            gap_range=[10.0, 40.0]
        )
        
        assert config.roi_range == [0.02, 0.15]
        assert config.gap_range == [10.0, 40.0]


class TestVisualizationConfig:
    """Test cases for VisualizationConfig"""

    def test_default_values(self):
        """Test that default values are set correctly"""
        config = VisualizationConfig()
        
        assert config.figure_size == [12, 8]
        assert config.show_plots is True
        assert config.save_plots is False
        assert config.output_dir == "output"

    def test_custom_values(self):
        """Test setting custom visualization options"""
        config = VisualizationConfig(
            figure_size=[16, 10],
            show_plots=False,
            save_plots=True,
            output_dir="custom_output"
        )
        
        assert config.figure_size == [16, 10]
        assert config.show_plots is False
        assert config.save_plots is True
        assert config.output_dir == "custom_output"


class TestOutputConfig:
    """Test cases for OutputConfig"""

    def test_default_values(self):
        """Test that default values are set correctly"""
        config = OutputConfig()
        
        assert config.verbose is True
        assert config.currency == "DKK"
        assert config.decimal_places == 0

    def test_custom_values(self):
        """Test setting custom output options"""
        config = OutputConfig(
            verbose=False,
            currency="USD",
            decimal_places=2
        )
        
        assert config.verbose is False
        assert config.currency == "USD"
        assert config.decimal_places == 2


class TestMainConfig:
    """Test cases for the main Config class"""

    def test_default_initialization(self):
        """Test that main config initializes with all sub-configs"""
        config = Config()
        
        assert isinstance(config.financial, FinancialConfig)
        assert isinstance(config.analysis, AnalysisConfig)
        assert isinstance(config.scenarios, ScenariosConfig)
        assert isinstance(config.visualization, VisualizationConfig)
        assert isinstance(config.output, OutputConfig)

    def test_custom_sub_configs(self):
        """Test setting custom sub-configurations"""
        financial = FinancialConfig(target_amount=1_000_000)
        analysis = AnalysisConfig(max_generations=10)
        
        config = Config(financial=financial, analysis=analysis)
        
        assert config.financial.target_amount == 1_000_000
        assert config.analysis.max_generations == 10
        # Others should use defaults
        assert config.scenarios.children_options == [1.0, 2.0, 3.0, 4.0]

    def test_omegaconf_compatibility(self):
        """Test that config works with OmegaConf"""
        config = Config()
        omega_config = OmegaConf.structured(config)
        
        # Should be able to access nested values
        assert omega_config.financial.target_amount == 10_000_000
        assert omega_config.analysis.children_per_generation == 2.0
        
        # Should be able to modify values
        omega_config.financial.roi_rate = 0.05
        assert omega_config.financial.roi_rate == 0.05

    def test_config_validation_types(self):
        """Test that config enforces correct types"""
        config = Config()
        omega_config = OmegaConf.structured(config)
        
        # Should accept valid types
        omega_config.financial.target_amount = 5_000_000.0
        omega_config.analysis.children_per_generation = 2.5
        
        # Should handle type conversion for compatible types
        omega_config.output.decimal_places = 2  # int should work
        assert omega_config.output.decimal_places == 2

    def test_nested_config_modification(self):
        """Test modifying nested configuration values"""
        config = Config()
        
        # Modify financial config
        config.financial.roi_rate = 0.08
        config.financial.generation_gap = 20
        
        # Modify analysis config  
        config.analysis.children_per_generation = 1.5
        
        # Verify changes
        assert config.financial.roi_rate == 0.08
        assert config.financial.generation_gap == 20
        assert config.analysis.children_per_generation == 1.5

    def test_config_serialization(self):
        """Test that config can be serialized and deserialized"""
        original_config = Config()
        original_config.financial.target_amount = 8_000_000
        original_config.scenarios.children_options = [1.0, 1.5, 2.0]
        
        # Convert to OmegaConf and serialize
        omega_config = OmegaConf.structured(original_config)
        yaml_str = OmegaConf.to_yaml(omega_config)
        
        # Deserialize
        restored_config = OmegaConf.create(yaml_str)
        
        # Verify values are preserved
        assert restored_config.financial.target_amount == 8_000_000
        assert restored_config.scenarios.children_options == [1.0, 1.5, 2.0]