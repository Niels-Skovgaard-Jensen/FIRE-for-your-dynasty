#!/usr/bin/env python3
"""
Main entry point for Dynasty FIRE analysis
"""

from typing import Dict, Any, Optional
import hydra
from hydra.core.config_store import ConfigStore
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig, OmegaConf

from dynasty_fire.config import Config
from dynasty_fire.calculator import DynastyFIRE
from dynasty_fire.visualizer import DynastyVisualizer
from dynasty_fire.utils import (
    format_children_text, 
    save_results_to_json, 
    save_summary_report,
    validate_config
)


# Register the config with Hydra
cs = ConfigStore.instance()
cs.store(name="config", node=Config)


@hydra.main(version_base=None, config_path=None, config_name="config")
def main(cfg: DictConfig) -> Optional[Dict[str, Any]]:
    """Main function with Hydra configuration management"""
    
    # Validate configuration
    validate_config(cfg)
    
    if cfg.output.verbose:
        print("FIRE for Your Dynasty - Compound Interest Analysis")
        print("=" * 50)
        print("Configuration:")
        print(f"  Target Amount: {cfg.financial.target_amount:,.0f} {cfg.output.currency}")
        print(f"  ROI Rate: {cfg.financial.roi_rate:.1%}")
        print(f"  Retirement Age: {cfg.financial.retirement_age} years")
        print(f"  Generation Gap: {cfg.financial.generation_gap} years")
        print()

    # Initialize dynasty calculator
    dynasty = DynastyFIRE(cfg)

    # Single child calculation
    single_investment = dynasty.calculate_single_child_investment()
    if cfg.output.verbose:
        print(f"Investment needed for one child: {single_investment:,.{cfg.output.decimal_places}f} {cfg.output.currency}")
        print(f"That's only {single_investment / 1_000_000:.2f} million {cfg.output.currency}!")

    # Multiple generations analysis
    if cfg.output.verbose:
        print("\nDynasty Analysis:")
    
    generation_tests = [2, 3, 5, 10] if cfg.output.verbose else [cfg.analysis.max_generations]

    for generations in generation_tests:
        total, breakdown = dynasty.calculate_dynasty_investment(
            generations, children_per_generation=cfg.analysis.children_per_generation
        )
        if cfg.output.verbose:
            children_str = format_children_text(cfg.analysis.children_per_generation)
            print(f"{generations} generations ({children_str} children each): "
                  f"{total:,.{cfg.output.decimal_places}f} {cfg.output.currency}")

    # Convergence analysis
    convergence = dynasty.convergence_analysis(
        children_per_generation=cfg.analysis.children_per_generation,
        max_generations=cfg.analysis.max_generations,
    )

    if cfg.output.verbose:
        children_str = format_children_text(cfg.analysis.children_per_generation)
        print(f"\nConvergence Analysis ({children_str} children per generation):")
        print(f"Series converges: {convergence['converges']}")
        print(f"Convergence ratio: {convergence['convergence_ratio']:.4f}")

        if convergence["infinite_sum"]:
            print(f"Infinite dynasty cost: {convergence['infinite_sum']:,.{cfg.output.decimal_places}f} {cfg.output.currency}")
            print(f"That's {convergence['infinite_sum'] / 1_000_000:.1f} million {cfg.output.currency} for infinite generations!")

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
        final_cost = analysis["infinite_sum"] if analysis["converges"] else None

        results[children] = {
            "converges": analysis["converges"],
            "cost": final_cost,
            "status": status,
        }

        if cfg.output.verbose:
            children_str = format_children_text(children)
            description = f"{children_str} child{'ren' if children > 1 else ''} per generation"
            
            if analysis["converges"]:
                print(f"{description}: {status} - Cost: {final_cost:,.{cfg.output.decimal_places}f} {cfg.output.currency}")
            else:
                print(f"{description}: {status} - Cost: ∞ (infinite)")

    # Generate visualization if enabled
    if cfg.visualization.show_plots or cfg.visualization.save_plots:
        if cfg.output.verbose:
            print("\nGenerating visualization...")
        
        visualizer = DynastyVisualizer(dynasty)
        visualizer.create_dynasty_growth_plot()

    # Prepare results for output
    final_results = {
        "single_child_investment": single_investment,
        "convergence_analysis": convergence,
        "scenario_results": results,
        "config": OmegaConf.to_container(cfg, resolve=True),
    }

    # Save results
    results_file = save_results_to_json(final_results)
    summary_file = save_summary_report(final_results, cfg)
    
    if cfg.output.verbose:
        print(f"\nResults saved to {results_file}")
        print(f"Summary report saved to {summary_file}")
        try:
            hydra_cfg = HydraConfig.get()
            print(f"Output directory: {hydra_cfg.runtime.output_dir}")
        except:
            pass

    # Return results for programmatic use
    return final_results


if __name__ == "__main__":
    main()