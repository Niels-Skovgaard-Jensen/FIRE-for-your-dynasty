"""Visualization module for Dynasty FIRE analysis"""

import math
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from omegaconf import DictConfig
from hydra.core.hydra_config import HydraConfig

from .calculator import DynastyFIRE


class DynastyVisualizer:
    """Handles visualization and plotting for Dynasty FIRE analysis"""
    
    def __init__(self, dynasty_calculator: DynastyFIRE):
        self.dynasty = dynasty_calculator
        self.config = dynasty_calculator.config
    
    def create_dynasty_growth_plot(self, max_generations: Optional[int] = None) -> Dict[str, Any]:
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

        figsize = self.config.visualization.figure_size
        plt.figure(figsize=figsize)

        analysis_results = {}
        
        for scenario in scenarios:
            analysis = self.dynasty.convergence_analysis(scenario["children"], max_generations)
            analysis_results[scenario["children"]] = analysis
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
        sensitivity = self.dynasty.sensitivity_analysis()
        plt.subplot(2, 2, 3)
        plt.plot(
            [r * 100 for r in sensitivity["roi_sensitivity"]["rates"]], 
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

        plt.tight_layout()

        # Save plot if configured
        if self.config.visualization.save_plots:
            self._save_plot()

        if self.config.visualization.show_plots:
            plt.show()

        return analysis_results
    
    def _save_plot(self) -> None:
        """Save the current plot to file"""
        try:
            # Try to use Hydra's output directory
            hydra_cfg = HydraConfig.get()
            output_dir = Path(hydra_cfg.runtime.output_dir)
        except:
            # Fallback to configured output directory
            output_dir = Path(self.config.visualization.output_dir)
            output_dir.mkdir(exist_ok=True)
        
        plot_file = output_dir / "dynasty_analysis.png"
        plt.savefig(plot_file, dpi=300, bbox_inches="tight")
        
        if self.config.output.verbose:
            print(f"Plot saved to {plot_file}")
    
    def create_convergence_heatmap(self, roi_range: Optional[np.ndarray] = None, 
                                  children_range: Optional[np.ndarray] = None) -> None:
        """Create a heatmap showing convergence regions
        
        Args:
            roi_range: Range of ROI rates to test
            children_range: Range of children per generation to test
        """
        if roi_range is None:
            roi_min, roi_max = self.config.scenarios.roi_range
            roi_range = np.linspace(roi_min, roi_max, 20)
        
        if children_range is None:
            children_range = np.linspace(1, 5, 20)
        
        convergence_matrix = np.zeros((len(children_range), len(roi_range)))
        
        for i, children in enumerate(children_range):
            for j, roi in enumerate(roi_range):
                # Calculate convergence ratio
                convergence_ratio = children / ((1 + roi) ** self.dynasty.Y_c)
                convergence_matrix[i, j] = 1 if convergence_ratio < 1 else 0
        
        plt.figure(figsize=(10, 8))
        plt.imshow(convergence_matrix, extent=[roi_range[0]*100, roi_range[-1]*100, 
                                              children_range[0], children_range[-1]], 
                   aspect='auto', origin='lower', cmap='RdYlGn')
        plt.colorbar(label='Convergence (1=Yes, 0=No)')
        plt.xlabel('ROI Rate (%)')
        plt.ylabel('Children per Generation')
        plt.title(f'Convergence Heatmap (Gap: {self.dynasty.Y_c} years)')
        
        # Add current configuration point
        plt.plot(self.dynasty.R * 100, self.config.analysis.children_per_generation, 
                'ro', markersize=10, label='Current Config')
        plt.legend()
        
        if self.config.visualization.show_plots:
            plt.show()
            
        if self.config.visualization.save_plots:
            self._save_plot()
    
    def create_cost_comparison_plot(self, children_options: Optional[list] = None) -> None:
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
                labels.append(f"{children:.1f}" if children != int(children) else f"{int(children)}")
                colors.append('green')
            else:
                # Skip divergent cases for this plot
                continue
        
        if costs:
            plt.figure(figsize=(10, 6))
            bars = plt.bar(labels, costs, color=colors, alpha=0.7)
            plt.xlabel('Children per Generation')
            plt.ylabel('Total Dynasty Cost (DKK)')
            plt.title('Dynasty Cost by Family Size (Convergent Cases Only)')
            plt.yscale('log')
            
            # Add value labels on bars
            for bar, cost in zip(bars, costs):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{cost:,.0f}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            if self.config.visualization.show_plots:
                plt.show()
                
            if self.config.visualization.save_plots:
                self._save_plot()