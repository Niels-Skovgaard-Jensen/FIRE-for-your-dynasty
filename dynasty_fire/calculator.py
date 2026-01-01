"""Core calculation engine for Dynasty FIRE analysis"""

import math
from typing import Dict, List, Tuple, Any
from omegaconf import DictConfig, OmegaConf


class DynastyFIRE:
    """Dynasty FIRE analysis class for compound interest calculations"""
    
    def __init__(self, config: DictConfig) -> None:
        self.config = config
        self.M: float = config.financial.target_amount
        self.R: float = config.financial.roi_rate
        self.Y: float = config.financial.retirement_age
        self.Y_c: float = config.financial.generation_gap

    def calculate_single_child_investment(self) -> float:
        """Calculate initial investment needed for one child's retirement
        
        Formula: B = M / (1 + R)^Y
        Where:
        - B = initial investment needed
        - M = target amount at retirement
        - R = annual return rate
        - Y = years until retirement
        
        Returns:
            float: Required initial investment
        """
        return self.M / ((1 + self.R) ** self.Y)

    def calculate_dynasty_investment(
        self, generations: int, children_per_generation: float = 1.0
    ) -> Tuple[float, List[float]]:
        """Calculate total investment needed for multiple generations
        
        Args:
            generations: Number of generations to analyze
            children_per_generation: Average children per generation (can be fractional)
            
        Returns:
            Tuple of (total_investment, investment_per_generation_list)
        """
        investments = []
        total = 0

        for n in range(generations):
            years_to_retirement = self.Y + n * self.Y_c
            investment_per_child = self.M / ((1 + self.R) ** years_to_retirement)
            # Number of people in generation n: first generation has k children, each has k children, etc.
            people_in_generation = children_per_generation ** (n + 1)
            generation_investment = investment_per_child * people_in_generation
            investments.append(generation_investment)
            total += generation_investment

        return total, investments

    def convergence_analysis(
        self, children_per_generation: float = 2.0, max_generations: int = 20
    ) -> Dict[str, Any]:
        """Analyze convergence of infinite dynasty investment series
        
        The infinite series converges when: k / (1+R)^Y_c < 1
        Where:
        - k = children per generation
        - R = annual return rate  
        - Y_c = generation gap in years
        
        Args:
            children_per_generation: Average children per generation
            max_generations: Maximum generations to simulate
            
        Returns:
            Dictionary containing convergence analysis results
        """
        # Calculate convergence ratio
        convergence_ratio = children_per_generation / ((1 + self.R) ** self.Y_c)
        converges = convergence_ratio < 1

        investments = []
        cumulative = []
        running_total = 0

        # Simulate finite generations with overflow protection
        for n in range(max_generations):
            years = self.Y + n * self.Y_c
            try:
                # Check for potential overflow before calculation
                # First generation has k children, each subsequent has k more
                term = children_per_generation ** (n + 1)
                discount = (1 + self.R) ** years

                # Prevent overflow by checking if numbers are getting too large
                if term > 1e100 or discount > 1e100:
                    break

                investment = self.M * term / discount
                
                # Additional check for extremely large values
                if investment > 1e50:
                    break
                    
                investments.append(investment)
                running_total += investment
                cumulative.append(running_total)
                
            except (OverflowError, ZeroDivisionError):
                # Handle overflow - series is diverging
                break

        # Calculate theoretical infinite sum if convergent
        infinite_sum = None
        if converges:
            try:
                # Sum = a / (1 - r) where a = first term, r = common ratio
                # First generation has k children, so first term is k * M / (1+R)^Y
                a = children_per_generation * self.M / ((1 + self.R) ** self.Y)
                r = children_per_generation / ((1 + self.R) ** self.Y_c)
                
                # Additional check: if r is very close to 1, the sum may be unstable
                if abs(1 - r) < 1e-10:
                    # Series converges but very slowly - numerical instability
                    infinite_sum = None
                    converges = False  # Mark as practically non-convergent
                else:
                    infinite_sum = a / (1 - r)
                    
            except (OverflowError, ZeroDivisionError):
                # Numerical issues - treat as divergent
                infinite_sum = None
                converges = False

        return {
            "converges": converges,
            "convergence_ratio": convergence_ratio,
            "investments": investments,
            "cumulative": cumulative,
            "infinite_sum": infinite_sum,
            "final_cumulative": running_total,
        }

    def sensitivity_analysis(self) -> Dict[str, Any]:
        """Analyze sensitivity to key parameters
        
        Returns:
            Dictionary containing sensitivity analysis results
        """
        base_investment = self.calculate_single_child_investment()

        # ROI sensitivity
        roi_min, roi_max = self.config.scenarios.roi_range
        roi_range = [r for r in [roi_min + 0.01 * i for i in range(int((roi_max - roi_min) * 100) + 1)]]
        roi_investments = [self.M / ((1 + r) ** self.Y) for r in roi_range]

        # Generation gap sensitivity  
        gap_min, gap_max = self.config.scenarios.gap_range
        gap_range = [gap_min + 2 * i for i in range(int((gap_max - gap_min) / 2) + 1)]
        gap_convergence = []
        
        for gap in gap_range:
            # Create temporary config with modified gap
            temp_config = OmegaConf.create(OmegaConf.to_yaml(self.config))
            temp_config.financial.generation_gap = float(gap)
            temp_fire = DynastyFIRE(temp_config)
            analysis = temp_fire.convergence_analysis(children_per_generation=2.0)
            gap_convergence.append(analysis["converges"])

        return {
            "base_investment": base_investment,
            "roi_sensitivity": {"rates": roi_range, "investments": roi_investments},
            "gap_sensitivity": {"gaps": gap_range, "convergence": gap_convergence},
        }

    def calculate_convergence_boundary(self, children_per_generation: float) -> float:
        """Calculate the minimum ROI rate required for convergence
        
        For convergence: children_per_generation < (1 + R)^generation_gap
        Solving for R: R > (children_per_generation)^(1/generation_gap) - 1
        
        Args:
            children_per_generation: Number of children per generation
            
        Returns:
            Minimum ROI rate required for convergence
        """
        if children_per_generation <= 1:
            return 0.0  # Always converges for <= 1 child
        
        return children_per_generation**(1/self.Y_c) - 1

    def calculate_max_children_for_convergence(self, roi_rate: float) -> float:
        """Calculate maximum children per generation that still converges
        
        Args:
            roi_rate: Annual return on investment rate
            
        Returns:
            Maximum children per generation for convergence
        """
        return (1 + roi_rate) ** self.Y_c