"""Calculator service wrapping the DynastyFIRE class for API use"""

import numpy as np
from omegaconf import OmegaConf

from dynasty_fire.calculator import DynastyFIRE


class CalculatorService:
    """Service layer wrapping DynastyFIRE for web API"""

    @staticmethod
    def create_config(params: dict) -> OmegaConf:
        """Create OmegaConf from API parameters"""
        config_dict = {
            "financial": {
                "target_amount": params.get("target_amount", 10_000_000),
                "roi_rate": params.get("roi_rate", 0.07),
                "retirement_age": params.get("retirement_age", 72),
                "generation_gap": params.get("generation_gap", 25),
            },
            "analysis": {
                "max_generations": params.get("max_generations", 20),
                "children_per_generation": params.get("children_per_generation", 2.0),
            },
            "scenarios": {
                "children_options": [1.0, 2.0, 3.0, 4.0],
                "roi_range": [0.03, 0.12],
                "gap_range": [15.0, 35.0],
            },
            "visualization": {"show_plots": False, "save_plots": False},
            "output": {"verbose": False, "currency": "DKK", "decimal_places": 0},
        }
        return OmegaConf.create(config_dict)

    @staticmethod
    def calculate(params: dict) -> dict:
        """Main calculation returning investment and convergence data"""
        config = CalculatorService.create_config(params)
        dynasty = DynastyFIRE(config)

        children = params.get("children_per_generation", 2.0)
        max_gen = params.get("max_generations", 20)

        convergence = dynasty.convergence_analysis(
            children_per_generation=children,
            max_generations=max_gen,
        )

        return {
            "single_child_investment": dynasty.calculate_single_child_investment(),
            "convergence": {
                "converges": convergence["converges"],
                "convergence_ratio": convergence["convergence_ratio"],
                "infinite_sum": convergence["infinite_sum"],
                "investments": convergence["investments"],
                "cumulative": convergence["cumulative"],
            },
            "max_children_for_convergence": dynasty.calculate_max_children_for_convergence(
                params.get("roi_rate", 0.07)
            ),
        }

    @staticmethod
    def generate_heatmap_data(params: dict) -> dict:
        """Generate heatmap matrix data for visualization"""
        config = CalculatorService.create_config(params)
        dynasty = DynastyFIRE(config)

        roi_range = params.get("roi_range", [0.03, 0.12])
        children_range = params.get("children_range", [1, 5])
        resolution = params.get("resolution", 50)

        roi_values = np.linspace(roi_range[0], roi_range[1], resolution).tolist()
        children_values = np.linspace(
            children_range[0], children_range[1], resolution
        ).tolist()

        convergence_matrix = []
        convergence_ratios = []
        infinite_sums = []

        for children in children_values:
            row_convergence = []
            row_ratios = []
            row_sums = []

            for roi in roi_values:
                # Calculate convergence ratio: k / (1+R)^Y_c
                ratio = children / ((1 + roi) ** dynasty.Y_c)
                converges = ratio < 1

                row_convergence.append(1 if converges else 0)
                row_ratios.append(ratio)

                if converges and abs(1 - ratio) > 1e-10:
                    # Calculate infinite sum: a / (1-r)
                    a = dynasty.M / ((1 + roi) ** dynasty.Y)
                    infinite_sum = a / (1 - ratio)
                    row_sums.append(infinite_sum)
                else:
                    row_sums.append(None)

            convergence_matrix.append(row_convergence)
            convergence_ratios.append(row_ratios)
            infinite_sums.append(row_sums)

        return {
            "roi_values": roi_values,
            "children_values": children_values,
            "convergence_matrix": convergence_matrix,
            "convergence_ratios": convergence_ratios,
            "infinite_sums": infinite_sums,
        }
