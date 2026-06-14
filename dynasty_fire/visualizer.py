"""Visualization module for Dynasty FIRE analysis"""

import math
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from hydra.core.hydra_config import HydraConfig

from .calculator import DynastyFIRE


class DynastyVisualizer:
    """Handles visualization and plotting for Dynasty FIRE analysis"""

    def __init__(self, dynasty_calculator: DynastyFIRE):
        self.dynasty = dynasty_calculator
        self.config = dynasty_calculator.config

    def create_dynasty_growth_plot(
        self, max_generations: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create comprehensive visualization of dynasty investment requirements

        Args:
            max_generations: Maximum generations to analyze

        Returns:
            Dictionary containing analysis results
        """
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

        # Create main analysis plots (2x3 grid)
        figsize = self.config.visualization.figure_size
        plt.figure(
            figsize=[figsize[0], figsize[1] * 1.5]
        )  # Make it taller for 6 subplots

        analysis_results = {}

        for scenario in scenarios:
            analysis = self.dynasty.convergence_analysis(
                scenario["children"], max_generations
            )
            analysis_results[scenario["children"]] = analysis
            generations = list(range(1, max_generations + 1))

            plt.subplot(2, 3, 1)
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

            plt.subplot(2, 3, 2)
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
        sensitivity = self.dynasty.sensitivity_analysis()
        plt.subplot(2, 3, 3)
        plt.plot(
            [r * 100 for r in sensitivity["roi_sensitivity"]["rates"]],
            sensitivity["roi_sensitivity"]["investments"],
        )
        plt.xlabel("ROI Rate (%)")
        plt.ylabel("Single Child Investment (DKK)")
        plt.title("ROI Sensitivity")

        # Convergence boundary
        plt.subplot(2, 3, 4)
        children_range = np.arange(1, 5, 0.1)
        boundary_gaps = []
        for c in children_range:
            if c > 1:
                gap = math.log(1 / c) / math.log(1 + self.dynasty.R)
                boundary_gaps.append(max(0, gap))
            else:
                boundary_gaps.append(50)  # Arbitrary high value

        plt.plot(children_range, boundary_gaps)
        plt.axhline(
            y=self.dynasty.Y_c,
            color="r",
            linestyle="--",
            label=f"Current gap: {self.dynasty.Y_c} years",
        )
        plt.xlabel("Children per Generation")
        plt.ylabel("Max Generation Gap for Convergence (years)")
        plt.title("Convergence Boundary")
        plt.legend()
        plt.ylim(0, 50)

        # Add convergence heatmap as subplot 5
        plt.subplot(2, 3, 5)
        self._create_heatmap_subplot()

        # Add cost comparison as subplot 6
        plt.subplot(2, 3, 6)
        self._create_cost_comparison_subplot()

        plt.tight_layout()

        # Save plot if configured
        if self.config.visualization.save_plots:
            self._save_plot("dynasty_comprehensive_analysis.png")

        if self.config.visualization.show_plots:
            plt.show()

        # Also create standalone heatmap
        self.create_convergence_heatmap()

        return analysis_results

    def _save_plot(self, filename: str = "dynasty_analysis.png") -> None:
        """Save the current plot to file"""
        try:
            # Try to use Hydra's output directory
            hydra_cfg = HydraConfig.get()
            output_dir = Path(hydra_cfg.runtime.output_dir)
        except Exception:
            # Fallback to configured output directory
            output_dir = Path(self.config.visualization.output_dir)
            output_dir.mkdir(exist_ok=True)

        plot_file = output_dir / filename
        plt.savefig(plot_file, dpi=self.config.visualization.dpi, bbox_inches="tight")

        if self.config.output.verbose:
            print(f"Plot saved to {plot_file}")

    def _create_heatmap_subplot(self) -> None:
        """Create convergence heatmap as a subplot"""
        roi_min, roi_max = self.config.scenarios.roi_range
        # Use reduced resolution for subplot to keep it readable
        subplot_resolution = min(15, self.config.visualization.heatmap_resolution // 3)
        roi_range = np.linspace(roi_min, roi_max, subplot_resolution)
        children_range = np.linspace(1, 4, subplot_resolution)

        convergence_matrix = np.zeros((len(children_range), len(roi_range)))
        convergence_ratio_matrix = np.zeros((len(children_range), len(roi_range)))

        for i, children in enumerate(children_range):
            for j, roi in enumerate(roi_range):
                convergence_ratio = children / ((1 + roi) ** self.dynasty.Y_c)
                convergence_matrix[i, j] = 1 if convergence_ratio < 1 else 0
                convergence_ratio_matrix[i, j] = convergence_ratio

        plt.imshow(
            convergence_matrix,
            extent=[
                roi_range[0] * 100,
                roi_range[-1] * 100,
                children_range[0],
                children_range[-1],
            ],
            aspect="auto",
            origin="lower",
            cmap="RdYlGn",
            alpha=0.8,
        )

        # Add contour lines if enabled
        if self.config.visualization.add_contours:
            X, Y = np.meshgrid(roi_range * 100, children_range)
            plt.contour(
                X,
                Y,
                convergence_ratio_matrix,
                levels=[1.0],
                colors="black",
                linewidths=2,
                alpha=0.8,
            )

        # Add current configuration point
        plt.plot(
            self.dynasty.R * 100,
            self.config.analysis.children_per_generation,
            "ro",
            markersize=8,
            label="Current Config",
        )

        plt.xlabel("ROI Rate (%)")
        plt.ylabel("Children/Generation")
        plt.title("Convergence Heatmap")
        plt.legend(fontsize=8)

    def _create_cost_comparison_subplot(self) -> None:
        """Create cost comparison as a subplot"""
        costs = []
        labels = []
        colors = []

        for children in self.config.scenarios.children_options[
            :4
        ]:  # Limit to 4 for readability
            analysis = self.dynasty.convergence_analysis(children)
            if analysis["converges"] and analysis["infinite_sum"]:
                costs.append(analysis["infinite_sum"])
                labels.append(
                    f"{children:.1f}"
                    if children != int(children)
                    else f"{int(children)}"
                )
                colors.append("green")

        if costs:
            bars = plt.bar(labels, costs, color=colors, alpha=0.7)
            plt.xlabel("Children/Generation")
            plt.ylabel("Dynasty Cost (DKK)")
            plt.title("Cost by Family Size")
            plt.yscale("log")

            # Add value labels on bars (simplified for subplot)
            for bar, cost in zip(bars, costs):
                height = bar.get_height()
                plt.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{cost / 1000:.0f}K",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

    def create_convergence_heatmap(
        self,
        roi_range: Optional[np.ndarray] = None,
        children_range: Optional[np.ndarray] = None,
    ) -> None:
        """Create a heatmap showing convergence regions

        Args:
            roi_range: Range of ROI rates to test
            children_range: Range of children per generation to test
        """
        if roi_range is None:
            roi_min, roi_max = self.config.scenarios.roi_range
            roi_range = np.linspace(
                roi_min, roi_max, self.config.visualization.heatmap_resolution
            )

        if children_range is None:
            children_range = np.linspace(
                1, 5, self.config.visualization.heatmap_resolution
            )

        convergence_matrix = np.zeros((len(children_range), len(roi_range)))
        convergence_ratio_matrix = np.zeros((len(children_range), len(roi_range)))

        for i, children in enumerate(children_range):
            for j, roi in enumerate(roi_range):
                # Calculate convergence ratio
                convergence_ratio = children / ((1 + roi) ** self.dynasty.Y_c)
                convergence_matrix[i, j] = 1 if convergence_ratio < 1 else 0
                convergence_ratio_matrix[i, j] = convergence_ratio

        plt.figure(figsize=(10, 8))
        im = plt.imshow(
            convergence_matrix,
            extent=[
                roi_range[0] * 100,
                roi_range[-1] * 100,
                children_range[0],
                children_range[-1],
            ],
            aspect="auto",
            origin="lower",
            cmap="RdYlGn",
        )

        # Add contour lines if enabled
        if self.config.visualization.add_contours:
            X, Y = np.meshgrid(roi_range * 100, children_range)
            # Add convergence boundary contour
            contours = plt.contour(
                X,
                Y,
                convergence_ratio_matrix,
                levels=[1.0],
                colors="black",
                linewidths=3,
            )
            plt.clabel(contours, inline=True, fontsize=10, fmt="Boundary")

            # Add additional ratio contours for reference
            ratio_levels = [0.5, 0.75, 1.25, 1.5, 2.0]
            ratio_contours = plt.contour(
                X,
                Y,
                convergence_ratio_matrix,
                levels=ratio_levels,
                colors="gray",
                linewidths=1,
                linestyles="dashed",
                alpha=0.6,
            )
            plt.clabel(ratio_contours, inline=True, fontsize=8, fmt="%.1f")

        plt.colorbar(im, label="Convergence (1=Yes, 0=No)")
        plt.xlabel("ROI Rate (%)")
        plt.ylabel("Children per Generation")
        plt.title(f"Convergence Heatmap (Gap: {self.dynasty.Y_c} years)")

        # Add current configuration point
        plt.plot(
            self.dynasty.R * 100,
            self.config.analysis.children_per_generation,
            "ro",
            markersize=10,
            label="Current Config",
        )
        plt.legend()

        if self.config.visualization.show_plots:
            plt.show()

        if self.config.visualization.save_plots:
            self._save_plot("convergence_heatmap.png")

    def create_cost_comparison_plot(
        self, children_options: Optional[list] = None
    ) -> None:
        """Create a bar chart comparing costs for different family sizes

        Args:
            children_options: List of children per generation options to compare
        """
        if children_options is None:
            children_options = self.config.scenarios.children_options

        costs = []
        labels = []
        colors = []

        for children in children_options:
            analysis = self.dynasty.convergence_analysis(children)
            if analysis["converges"] and analysis["infinite_sum"]:
                costs.append(analysis["infinite_sum"])
                labels.append(
                    f"{children:.1f}"
                    if children != int(children)
                    else f"{int(children)}"
                )
                colors.append("green")
            else:
                # Skip divergent cases for this plot
                continue

        if costs:
            plt.figure(figsize=(10, 6))
            bars = plt.bar(labels, costs, color=colors, alpha=0.7)
            plt.xlabel("Children per Generation")
            plt.ylabel("Total Dynasty Cost (DKK)")
            plt.title("Dynasty Cost by Family Size (Convergent Cases Only)")
            plt.yscale("log")

            # Add value labels on bars
            for bar, cost in zip(bars, costs):
                height = bar.get_height()
                plt.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{cost:,.0f}",
                    ha="center",
                    va="bottom",
                )

            plt.tight_layout()

            if self.config.visualization.show_plots:
                plt.show()

            if self.config.visualization.save_plots:
                self._save_plot("cost_comparison.png")
