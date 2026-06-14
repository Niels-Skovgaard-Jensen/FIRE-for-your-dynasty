"""Pytest configuration and fixtures"""

import pytest
from omegaconf import OmegaConf

from dynasty_fire.config import Config
from dynasty_fire.calculator import DynastyFIRE


@pytest.fixture
def default_config():
    """Create a default configuration for testing"""
    config = Config()
    return OmegaConf.structured(config)


@pytest.fixture
def custom_config():
    """Create a custom configuration for testing edge cases"""
    config_dict = {
        "financial": {
            "target_amount": 5_000_000,
            "roi_rate": 0.05,
            "retirement_age": 65,
            "generation_gap": 30,
        },
        "analysis": {"max_generations": 10, "children_per_generation": 1.5},
        "scenarios": {
            "children_options": [1.0, 1.5, 2.0, 2.5],
            "roi_range": [0.03, 0.08],
            "gap_range": [20.0, 40.0],
        },
        "visualization": {
            "figure_size": [10, 6],
            "show_plots": False,
            "save_plots": False,
            "output_dir": "test_output",
        },
        "output": {"verbose": False, "currency": "USD", "decimal_places": 2},
    }
    return OmegaConf.create(config_dict)


@pytest.fixture
def dynasty_calculator(default_config):
    """Create a Dynasty FIRE calculator with default config"""
    return DynastyFIRE(default_config)


@pytest.fixture
def custom_dynasty_calculator(custom_config):
    """Create a Dynasty FIRE calculator with custom config"""
    return DynastyFIRE(custom_config)


@pytest.fixture
def high_roi_config():
    """Configuration with high ROI that should always converge"""
    config_dict = {
        "financial": {
            "target_amount": 1_000_000,
            "roi_rate": 0.15,  # 15% ROI
            "retirement_age": 50,
            "generation_gap": 20,
        },
        "analysis": {"max_generations": 5, "children_per_generation": 2.0},
        "scenarios": {
            "children_options": [1.0, 2.0, 3.0, 4.0],
            "roi_range": [0.10, 0.20],
            "gap_range": [15.0, 25.0],
        },
        "visualization": {
            "figure_size": [8, 6],
            "show_plots": False,
            "save_plots": False,
            "output_dir": "test_output",
        },
        "output": {"verbose": False, "currency": "EUR", "decimal_places": 0},
    }
    return OmegaConf.create(config_dict)


@pytest.fixture
def low_roi_config():
    """Configuration with low ROI that may diverge"""
    config_dict = {
        "financial": {
            "target_amount": 2_000_000,
            "roi_rate": 0.02,  # 2% ROI
            "retirement_age": 70,
            "generation_gap": 15,
        },
        "analysis": {"max_generations": 20, "children_per_generation": 3.0},
        "scenarios": {
            "children_options": [2.0, 3.0, 4.0, 5.0],
            "roi_range": [0.01, 0.05],
            "gap_range": [10.0, 20.0],
        },
        "visualization": {
            "figure_size": [12, 8],
            "show_plots": False,
            "save_plots": False,
            "output_dir": "test_output",
        },
        "output": {"verbose": False, "currency": "GBP", "decimal_places": 1},
    }
    return OmegaConf.create(config_dict)
