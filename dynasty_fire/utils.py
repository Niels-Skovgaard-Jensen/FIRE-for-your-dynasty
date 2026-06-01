"""Utility functions for Dynasty FIRE analysis"""

import json
from pathlib import Path
from typing import Dict, Any
from omegaconf import DictConfig
from hydra.core.hydra_config import HydraConfig


def format_children_text(children: float) -> str:
    """Format children count for display

    Args:
        children: Number of children (can be fractional)

    Returns:
        Formatted string representation
    """
    if children == int(children):
        return f"{int(children)}"
    else:
        return f"{children:.1f}"


def save_results_to_json(
    results: Dict[str, Any], filename: str = "dynasty_results.json"
) -> Path:
    """Save analysis results to JSON file

    Args:
        results: Dictionary containing analysis results
        filename: Name of the output file

    Returns:
        Path to the saved file
    """
    try:
        # Try to use Hydra's output directory
        hydra_cfg = HydraConfig.get()
        output_dir = Path(hydra_cfg.runtime.output_dir)
    except Exception:
        # Fallback to current directory
        output_dir = Path(".")

    output_file = output_dir / filename

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    return output_file


def save_summary_report(
    results: Dict[str, Any], config: DictConfig, filename: str = "summary_report.txt"
) -> Path:
    """Save a human-readable summary report

    Args:
        results: Dictionary containing analysis results
        config: Configuration object
        filename: Name of the output file

    Returns:
        Path to the saved file
    """
    try:
        # Try to use Hydra's output directory
        hydra_cfg = HydraConfig.get()
        output_dir = Path(hydra_cfg.runtime.output_dir)
    except Exception:
        # Fallback to current directory
        output_dir = Path(".")

    output_file = output_dir / filename

    with open(output_file, "w") as f:
        f.write("FIRE for Your Dynasty - Analysis Summary\n")
        f.write("=" * 45 + "\n\n")
        f.write("Configuration:\n")
        f.write(
            f"  Target Amount: {config.financial.target_amount:,.0f} {config.output.currency}\n"
        )
        f.write(f"  ROI Rate: {config.financial.roi_rate:.1%}\n")
        f.write(f"  Retirement Age: {config.financial.retirement_age} years\n")
        f.write(f"  Generation Gap: {config.financial.generation_gap} years\n\n")

        f.write("Key Results:\n")
        f.write(
            f"  Single Child Investment: {results['single_child_investment']:,.0f} {config.output.currency}\n"
        )

        convergence = results["convergence_analysis"]
        if convergence["infinite_sum"]:
            f.write(
                f"  Infinite Dynasty Cost: {convergence['infinite_sum']:,.0f} {config.output.currency}\n"
            )
        f.write(f"  Series Converges: {convergence['converges']}\n")
        f.write(f"  Convergence Ratio: {convergence['convergence_ratio']:.4f}\n\n")

        f.write("Scenario Analysis:\n")
        for children, result in results["scenario_results"].items():
            children_str = format_children_text(children)

            if result["converges"]:
                f.write(
                    f"  {children_str} children per generation: {result['status']} - {result['cost']:,.0f} {config.output.currency}\n"
                )
            else:
                f.write(
                    f"  {children_str} children per generation: {result['status']} - ∞ (infinite)\n"
                )

    return output_file


def calculate_years_to_double(roi_rate: float) -> float:
    """Calculate years needed to double investment using rule of 72

    Args:
        roi_rate: Annual return on investment rate

    Returns:
        Number of years to double the investment
    """
    if roi_rate <= 0:
        return float("inf")
    return 72 / (roi_rate * 100)


def format_currency(
    amount: float, currency: str = "DKK", decimal_places: int = 0
) -> str:
    """Format currency amount for display

    Args:
        amount: Amount to format
        currency: Currency symbol/code
        decimal_places: Number of decimal places

    Returns:
        Formatted currency string
    """
    if amount is None:
        return "∞ (infinite)"

    return f"{amount:,.{decimal_places}f} {currency}"


def validate_config(config: DictConfig) -> bool:
    """Validate configuration parameters

    Args:
        config: Configuration to validate

    Returns:
        True if valid, raises ValueError if invalid
    """
    # Financial validation
    if config.financial.target_amount <= 0:
        raise ValueError("Target amount must be positive")

    if config.financial.roi_rate <= 0:
        raise ValueError("ROI rate must be positive")

    if config.financial.retirement_age <= 0:
        raise ValueError("Retirement age must be positive")

    if config.financial.generation_gap <= 0:
        raise ValueError("Generation gap must be positive")

    # Analysis validation
    if config.analysis.max_generations <= 0:
        raise ValueError("Max generations must be positive")

    if config.analysis.children_per_generation <= 0:
        raise ValueError("Children per generation must be positive")

    # Scenarios validation
    if not config.scenarios.children_options:
        raise ValueError("Children options cannot be empty")

    if any(c <= 0 for c in config.scenarios.children_options):
        raise ValueError("All children options must be positive")

    return True
