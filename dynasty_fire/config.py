"""Configuration classes for Dynasty FIRE analysis"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class FinancialConfig:
    """Financial parameters for dynasty analysis"""

    target_amount: float = 2_000_000  # Target retirement amount in USD
    roi_rate: float = 0.07  # Annual return on investment (7%)
    retirement_age: float = 65  # Retirement age in years
    generation_gap: float = 30  # Years between generations


@dataclass
class AnalysisConfig:
    """Analysis parameters"""

    max_generations: int = 20  # Maximum generations to analyze
    children_per_generation: float = (
        2.0  # Default children per generation (can be fractional)
    )


@dataclass
class ScenariosConfig:
    """Scenario analysis parameters"""

    children_options: List[float] = field(
        default_factory=lambda: [1.0, 2.0, 3.0, 4.0]
    )  # Different family size scenarios (can be fractional)
    roi_range: List[float] = field(
        default_factory=lambda: [0.03, 0.12]
    )  # ROI sensitivity range
    gap_range: List[float] = field(
        default_factory=lambda: [15.0, 35.0]
    )  # Generation gap range


@dataclass
class VisualizationConfig:
    """Visualization settings"""

    figure_size: List[int] = field(
        default_factory=lambda: [12, 8]
    )  # Figure size for plots
    dpi: int = 300  # Resolution for saved plots
    show_plots: bool = True  # Whether to display plots
    save_plots: bool = True  # Whether to save plots to file
    output_dir: str = "output"  # Directory for saved plots
    heatmap_resolution: int = 50  # Resolution for heatmap (grid points)
    add_contours: bool = True  # Whether to add contour lines to heatmap


@dataclass
class OutputConfig:
    """Output settings"""

    verbose: bool = True  # Detailed output
    currency: str = "USD"  # Currency for display
    decimal_places: int = 0  # Decimal places for currency display


@dataclass
class Config:
    """Main configuration class"""

    financial: FinancialConfig = field(default_factory=FinancialConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    scenarios: ScenariosConfig = field(default_factory=ScenariosConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
