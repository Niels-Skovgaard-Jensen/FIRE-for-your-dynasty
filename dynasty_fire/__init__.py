"""Dynasty FIRE - Compound Interest Analysis for Generational Wealth Planning"""

from .config import (
    FinancialConfig,
    AnalysisConfig,
    ScenariosConfig,
    VisualizationConfig,
    OutputConfig,
    Config,
)
from .calculator import DynastyFIRE
from .visualizer import DynastyVisualizer

__version__ = "0.1.0"
__all__ = [
    "FinancialConfig",
    "AnalysisConfig",
    "ScenariosConfig",
    "VisualizationConfig",
    "OutputConfig",
    "Config",
    "DynastyFIRE",
    "DynastyVisualizer",
]
