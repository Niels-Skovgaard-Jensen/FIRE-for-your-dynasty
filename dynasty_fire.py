import math
from typing import Any
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import DictConfig, OmegaConf


@dataclass
class FinancialConfig:
    """Financial parameters for dynasty analysis"""

    target_amount: float = 2e6  # Target retirement amount in DKK
    roi_rate: float = 0.07  # Annual return on investment (7%)
    retirement_age: float = 65  # Retirement age in years
    generation_gap: float = 30  # Years between generations


@dataclass
class AnalysisConfig:
    """Analysis parameters"""

    max_generations: int = 20  # Maximum generations to analyze
    children_per_generation: int = 2  # Default children per generation


@dataclass
class ScenariosConfig:
    """Scenario analysis parameters"""

    children_options: list[int] = field(
        default_factory=lambda: [1, 2, 3, 4]
    )  # Different family size scenarios
    roi_range: list[float] = field(
        default_factory=lambda: [0.03, 0.12]
    )  # ROI sensitivity range
    gap_range: list[float] = field(
        default_factory=lambda: [15.0, 35.0]
    )  # Generation gap range


@dataclass
class VisualizationConfig:
    """Visualization settings"""

    figure_size: list[int] = field(
        default_factory=lambda: [12, 8]
    )  # Figure size for plots
    show_plots: bool = True  # Whether to display plots
    save_plots: bool = False  # Whether to save plots to file
    output_dir: str = "output"  # Directory for saved plots


@dataclass
class OutputConfig:
    """Output settings"""

    verbose: bool = True  # Detailed output
    currency: str = "DKK"  # Currency for display
    decimal_places: int = 0  # Decimal places for currency display


@dataclass
class Config:
    """Main configuration class"""

    financial: FinancialConfig = field(default_factory=FinancialConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    scenarios: ScenariosConfig = field(default_factory=ScenariosConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    output: OutputConfig = field(default_factory=OutputConfig)


class DynastyFIRE:
    """Dynasty FIRE analysis class for compound interest calculations"""

    def __init__(self, config: DictConfig) -> None:
        self.config = config
        self.M: float = config.financial.target_amount
        self.R: float = config.financial.roi_rate
        self.Y: float = config.financial.retirement_age
        self.Y_c: float = config.financial.generation_gap

    def calculate_single_child_investment(self) -> float:
        """Calculate initial investment needed for one child's retirement"""
        return self.M / ((1 + self.R) ** self.Y)

    def calculate_dynasty_investment(
        self, generations: int, children_per_generation: int = 1
    ) -> tuple[float, list[float]]:
        """Calculate total investment needed for multiple generations"""
        investments = []
        total = 0

        for n in range(generations):
            years_to_retirement = self.Y + n * self.Y_c
            investment_per_child = self.M / ((1 + self.R) ** years_to_retirement)
            generation_investment = investment_per_child * (children_per_generation**n)
            investments.append(generation_investment)
            total += generation_investment

        return total, investments

    def convergence_analysis(
        self, children_per_generation: int = 2, max_generations: int = 20
    ) -> dict[str, Any]:
        """Analyze convergence of infinite dynasty investment"""
        # For convergence: |k / (1+R)^Y_c| < 1
        # Where k is children per generation
        convergence_ratio = children_per_generation / ((1 + self.R) ** self.Y_c)
        converges = convergence_ratio < 1

        investments = []
        cumulative = []
        running_total = 0

        for n in range(max_generations):
            years = self.Y + n * self.Y_c
            investment = self.M * (children_per_generation**n) / ((1 + self.R) ** years)
            investments.append(investment)
            running_total += investment
            cumulative.append(running_total)

        # Calculate theoretical infinite sum if convergent
        infinite_sum = None
        if converges:
            # Sum = a / (1 - r) where a = first term, r = common ratio
            a = self.M / ((1 + self.R) ** self.Y)
            r = children_per_generation / ((1 + self.R) ** self.Y_c)
            infinite_sum = a / (1 - r)

        return {
            "converges": converges,
            "convergence_ratio": convergence_ratio,
            "investments": investments,
            "cumulative": cumulative,
            "infinite_sum": infinite_sum,
            "final_cumulative": running_total,
        }

    def sensitivity_analysis(self) -> dict[str, Any]:
        """Analyze sensitivity to key parameters"""
        base_investment = self.calculate_single_child_investment()

        # ROI sensitivity
        roi_min, roi_max = self.config.scenarios.roi_range
        roi_range = np.arange(roi_min, roi_max, 0.01)
        roi_investments = [self.M / ((1 + r) ** self.Y) for r in roi_range]

        # Generation gap sensitivity
        gap_min, gap_max = self.config.scenarios.gap_range
        gap_range = np.arange(gap_min, gap_max, 2)
        gap_convergence = []
        for gap in gap_range:
            # Create temporary config with modified gap
            temp_config = OmegaConf.create(OmegaConf.to_yaml(self.config))
            temp_config.financial.generation_gap = float(
                gap
            )  # Convert numpy float64 to Python float
            temp_fire = DynastyFIRE(temp_config)
            analysis = temp_fire.convergence_analysis(children_per_generation=2)
            gap_convergence.append(analysis["converges"])

        return {
            "base_investment": base_investment,
            "roi_sensitivity": {"rates": roi_range, "investments": roi_investments},
            "gap_sensitivity": {"gaps": gap_range, "convergence": gap_convergence},
        }

    def visualize_dynasty_growth(
        self, max_generations: int | None = None
    ) -> dict[str, Any]:
        """Create visualization of dynasty investment requirements"""
        if max_generations is None:
            max_generations = self.config.analysis.max_generations

        scenarios = [
            {
                "children": c,
                "label": f"{c} child{'ren' if c > 1 else ''} per generation",
            }
            for c in self.config.scenarios.children_options[
                :3
            ]  # Limit to 3 for readability
        ]

        figsize = self.config.visualization.figure_size
        plt.figure(figsize=figsize)

        for scenario in scenarios:
            analysis = self.convergence_analysis(scenario["children"], max_generations)
            generations = list(range(1, max_generations + 1))

            plt.subplot(2, 2, 1)
            plt.plot(
                generations,
                analysis["cumulative"],
                label=f"{scenario['label']} ({'Converges' if analysis['converges'] else 'Diverges'})",
            )
            plt.xlabel("Generations")
            plt.ylabel("Cumulative Investment (DKK)")
            plt.title("Dynasty Investment Growth")
            plt.legend()
            plt.yscale("log")

            plt.subplot(2, 2, 2)
            plt.plot(
                generations,
                analysis["investments"],
                label=scenario["label"],
                marker="o",
            )
            plt.xlabel("Generation")
            plt.ylabel("Investment per Generation (DKK)")
            plt.title("Investment Required per Generation")
            plt.legend()
            plt.yscale("log")

        # ROI sensitivity
        sensitivity = self.sensitivity_analysis()
        plt.subplot(2, 2, 3)
        plt.plot(
            sensitivity["roi_sensitivity"]["rates"] * 100,
            sensitivity["roi_sensitivity"]["investments"],
        )
        plt.xlabel("ROI Rate (%)")
        plt.ylabel("Single Child Investment (DKK)")
        plt.title("ROI Sensitivity")

        # Convergence boundary
        plt.subplot(2, 2, 4)
        children_range = np.arange(1, 5, 0.1)
        boundary_gaps = []
        for c in children_range:
            if c > 1:
                gap = math.log(1 / c) / math.log(1 + self.R)
                boundary_gaps.append(max(0, gap))
            else:
                boundary_gaps.append(50)  # Arbitrary high value

        plt.plot(children_range, boundary_gaps)
        plt.axhline(
            y=self.Y_c,
            color="r",
            linestyle="--",
            label=f"Current gap: {self.Y_c} years",
        )
        plt.xlabel("Children per Generation")
        plt.ylabel("Max Generation Gap for Convergence (years)")
        plt.title("Convergence Boundary")
        plt.legend()
        plt.ylim(0, 50)

        plt.tight_layout()

        if self.config.visualization.save_plots:
            output_dir = Path(self.config.visualization.output_dir)
            output_dir.mkdir(exist_ok=True)
            plt.savefig(
                output_dir / "dynasty_analysis.png", dpi=300, bbox_inches="tight"
            )
            if self.config.output.verbose:
                print(f"Plot saved to {output_dir / 'dynasty_analysis.png'}")

        if self.config.visualization.show_plots:
            plt.show()

        return analysis


# Register the config with Hydra
cs = ConfigStore.instance()
cs.store(name="config", node=Config)


@hydra.main(version_base=None, config_path=None, config_name="config")
def main(cfg: DictConfig) -> dict[str, Any] | None:
    """Main function with Hydra configuration management"""

    if cfg.output.verbose:
        print("FIRE for Your Dynasty - Compound Interest Analysis")
        print("=" * 50)
        print("Configuration:")
        print(
            f"  Target Amount: {cfg.financial.target_amount:,.0f} {cfg.output.currency}"
        )
        print(f"  ROI Rate: {cfg.financial.roi_rate:.1%}")
        print(f"  Retirement Age: {cfg.financial.retirement_age} years")
        print(f"  Generation Gap: {cfg.financial.generation_gap} years")
        print()

    # Initialize dynasty model
    dynasty = DynastyFIRE(cfg)

    # Single child calculation
    single_investment = dynasty.calculate_single_child_investment()
    if cfg.output.verbose:
        print(
            f"Investment needed for one child: {single_investment:,.{cfg.output.decimal_places}f} {cfg.output.currency}"
        )
        print(
            f"That's only {single_investment / 1_000_000:.2f} million {cfg.output.currency}!"
        )

    # Multiple generations analysis
    if cfg.output.verbose:
        print("\nDynasty Analysis:")
    generation_tests = (
        [2, 3, 5, 10] if cfg.output.verbose else [cfg.analysis.max_generations]
    )

    for generations in generation_tests:
        total, breakdown = dynasty.calculate_dynasty_investment(
            generations, children_per_generation=cfg.analysis.children_per_generation
        )
        if cfg.output.verbose:
            print(
                f"{generations} generations ({cfg.analysis.children_per_generation} children each): "
                f"{total:,.{cfg.output.decimal_places}f} {cfg.output.currency}"
            )

    # Convergence analysis
    convergence = dynasty.convergence_analysis(
        children_per_generation=cfg.analysis.children_per_generation,
        max_generations=cfg.analysis.max_generations,
    )

    if cfg.output.verbose:
        print(
            f"\nConvergence Analysis ({cfg.analysis.children_per_generation} children per generation):"
        )
        print(f"Series converges: {convergence['converges']}")
        print(f"Convergence ratio: {convergence['convergence_ratio']:.4f}")

        if convergence["infinite_sum"]:
            print(
                f"Infinite dynasty cost: {convergence['infinite_sum']:,.{cfg.output.decimal_places}f} {cfg.output.currency}"
            )
            print(
                f"That's {convergence['infinite_sum'] / 1_000_000:.1f} million {cfg.output.currency} for infinite generations!"
            )

    # Scenario analysis for all configured children options
    if cfg.output.verbose:
        print("\nScenario Analysis:")

    results = {}
    for children in cfg.scenarios.children_options:
        analysis = dynasty.convergence_analysis(
            children_per_generation=children,
            max_generations=cfg.analysis.max_generations,
        )
        status = "CONVERGES" if analysis["converges"] else "DIVERGES"
        final_cost = (
            analysis["infinite_sum"]
            if analysis["infinite_sum"]
            else analysis["final_cumulative"]
        )

        results[children] = {
            "converges": analysis["converges"],
            "cost": final_cost,
            "status": status,
        }

        if cfg.output.verbose:
            description = (
                f"{children} child{'ren' if children > 1 else ''} per generation"
            )
            print(
                f"{description}: {status} - Cost: {final_cost:,.{cfg.output.decimal_places}f} {cfg.output.currency}"
            )

    # Generate visualization if enabled
    if cfg.visualization.show_plots or cfg.visualization.save_plots:
        if cfg.output.verbose:
            print("\nGenerating visualization...")
        dynasty.visualize_dynasty_growth()

    # Return results for programmatic use
    return {
        "single_child_investment": single_investment,
        "convergence_analysis": convergence,
        "scenario_results": results,
        "config": cfg,
    }


if __name__ == "__main__":
    main()
