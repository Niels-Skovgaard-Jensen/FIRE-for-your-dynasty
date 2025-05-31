import math
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple


class DynastyFIRE:
    def __init__(self, 
                 target_amount: float = 10_000_000,  # DKK
                 roi_rate: float = 0.07,  # 7% annual return
                 retirement_age: float = 72,  # years
                 generation_gap: float = 25):  # years between generations
        self.M = target_amount
        self.R = roi_rate
        self.Y = retirement_age
        self.Y_c = generation_gap
    
    def calculate_single_child_investment(self) -> float:
        """Calculate initial investment needed for one child's retirement"""
        return self.M / ((1 + self.R) ** self.Y)
    
    def calculate_dynasty_investment(self, generations: int, children_per_generation: int = 1) -> Tuple[float, List[float]]:
        """Calculate total investment needed for multiple generations"""
        investments = []
        total = 0
        
        for n in range(generations):
            years_to_retirement = self.Y + n * self.Y_c
            investment_per_child = self.M / ((1 + self.R) ** years_to_retirement)
            generation_investment = investment_per_child * (children_per_generation ** n)
            investments.append(generation_investment)
            total += generation_investment
            
        return total, investments
    
    def convergence_analysis(self, children_per_generation: int = 2, max_generations: int = 20) -> Dict:
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
            investment = self.M * (children_per_generation ** n) / ((1 + self.R) ** years)
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
            'converges': converges,
            'convergence_ratio': convergence_ratio,
            'investments': investments,
            'cumulative': cumulative,
            'infinite_sum': infinite_sum,
            'final_cumulative': running_total
        }
    
    def sensitivity_analysis(self) -> Dict:
        """Analyze sensitivity to key parameters"""
        base_investment = self.calculate_single_child_investment()
        
        # ROI sensitivity
        roi_range = np.arange(0.03, 0.12, 0.01)
        roi_investments = [self.M / ((1 + r) ** self.Y) for r in roi_range]
        
        # Generation gap sensitivity  
        gap_range = np.arange(15, 35, 2)
        gap_convergence = []
        for gap in gap_range:
            temp_fire = DynastyFIRE(self.M, self.R, self.Y, gap)
            analysis = temp_fire.convergence_analysis(children_per_generation=2)
            gap_convergence.append(analysis['converges'])
        
        return {
            'base_investment': base_investment,
            'roi_sensitivity': {'rates': roi_range, 'investments': roi_investments},
            'gap_sensitivity': {'gaps': gap_range, 'convergence': gap_convergence}
        }
    
    def visualize_dynasty_growth(self, max_generations: int = 10):
        """Create visualization of dynasty investment requirements"""
        scenarios = [
            {'children': 1, 'label': '1 child per generation'},
            {'children': 2, 'label': '2 children per generation'}, 
            {'children': 3, 'label': '3 children per generation'}
        ]
        
        plt.figure(figsize=(12, 8))
        
        for scenario in scenarios:
            analysis = self.convergence_analysis(scenario['children'], max_generations)
            generations = list(range(1, max_generations + 1))
            
            plt.subplot(2, 2, 1)
            plt.plot(generations, analysis['cumulative'], 
                    label=f"{scenario['label']} ({'Converges' if analysis['converges'] else 'Diverges'})")
            plt.xlabel('Generations')
            plt.ylabel('Cumulative Investment (DKK)')
            plt.title('Dynasty Investment Growth')
            plt.legend()
            plt.yscale('log')
            
            plt.subplot(2, 2, 2)
            plt.plot(generations, analysis['investments'], 
                    label=scenario['label'], marker='o')
            plt.xlabel('Generation')
            plt.ylabel('Investment per Generation (DKK)')
            plt.title('Investment Required per Generation')
            plt.legend()
            plt.yscale('log')
        
        # ROI sensitivity
        sensitivity = self.sensitivity_analysis()
        plt.subplot(2, 2, 3)
        plt.plot(sensitivity['roi_sensitivity']['rates'] * 100, 
                sensitivity['roi_sensitivity']['investments'])
        plt.xlabel('ROI Rate (%)')
        plt.ylabel('Single Child Investment (DKK)')
        plt.title('ROI Sensitivity')
        
        # Convergence boundary
        plt.subplot(2, 2, 4)
        children_range = np.arange(1, 5, 0.1)
        boundary_gaps = []
        for c in children_range:
            if c > 1:
                gap = math.log(1/c) / math.log(1 + self.R)
                boundary_gaps.append(max(0, gap))
            else:
                boundary_gaps.append(50)  # Arbitrary high value
        
        plt.plot(children_range, boundary_gaps)
        plt.axhline(y=self.Y_c, color='r', linestyle='--', label=f'Current gap: {self.Y_c} years')
        plt.xlabel('Children per Generation')
        plt.ylabel('Max Generation Gap for Convergence (years)')
        plt.title('Convergence Boundary')
        plt.legend()
        plt.ylim(0, 50)
        
        plt.tight_layout()
        plt.show()
        
        return analysis


def main():
    print("FIRE for Your Dynasty - Compound Interest Analysis")
    print("=" * 50)
    
    # Initialize with Danish parameters from the document
    dynasty = DynastyFIRE(
        target_amount=10_000_000,  # 10M DKK
        roi_rate=0.07,             # 7% annual return
        retirement_age=72,         # Danish retirement age
        generation_gap=25          # 25 years between generations
    )
    
    # Single child calculation
    single_investment = dynasty.calculate_single_child_investment()
    print(f"Investment needed for one child: {single_investment:,.0f} DKK")
    print(f"That's only {single_investment/1_000_000:.2f} million DKK!")
    
    # Multiple generations
    print("\nDynasty Analysis:")
    for generations in [2, 3, 5, 10]:
        total, breakdown = dynasty.calculate_dynasty_investment(generations, children_per_generation=2)
        print(f"{generations} generations (2 children each): {total:,.0f} DKK")
    
    # Convergence analysis
    print("\nConvergence Analysis (2 children per generation):")
    convergence = dynasty.convergence_analysis(children_per_generation=2)
    print(f"Series converges: {convergence['converges']}")
    print(f"Convergence ratio: {convergence['convergence_ratio']:.4f}")
    if convergence['infinite_sum']:
        print(f"Infinite dynasty cost: {convergence['infinite_sum']:,.0f} DKK")
        print(f"That's {convergence['infinite_sum']/1_000_000:.1f} million DKK for infinite generations!")
    
    # Test different scenarios
    print("\nScenario Analysis:")
    scenarios = [
        (1, "1 child per generation (linear dynasty)"),
        (2, "2 children per generation (exponential growth)"),
        (3, "3 children per generation (rapid expansion)")
    ]
    
    for children, description in scenarios:
        analysis = dynasty.convergence_analysis(children_per_generation=children, max_generations=15)
        status = "CONVERGES" if analysis['converges'] else "DIVERGES"
        final_cost = analysis['infinite_sum'] if analysis['infinite_sum'] else analysis['final_cumulative']
        print(f"{description}: {status} - Cost: {final_cost:,.0f} DKK")
    
    # Create visualization
    print("\nGenerating visualization...")
    dynasty.visualize_dynasty_growth()


if __name__ == "__main__":
    main()
