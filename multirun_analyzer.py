#!/usr/bin/env python3
"""
Dynasty FIRE Multirun Analyzer

Analyzes multiple Hydra output runs to create comparative visualizations and summary reports.
"""

import json
import matplotlib.pyplot as plt
import polars as pl
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import seaborn as sns
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")


class MultirunAnalyzer:
    """Analyzes multiple Dynasty FIRE runs and generates comparative reports"""

    def __init__(self, outputs_dir: str = "multirun"):
        self.outputs_dir = Path(outputs_dir)
        self.runs_data: List[Dict[str, Any]] = []
        self.comparison_df: Optional[pl.DataFrame] = None

    def load_runs(self, pattern: str = "**/*/dynasty_results.json") -> int:
        """Load all Dynasty FIRE runs from the outputs directory"""
        result_files = list(self.outputs_dir.glob(pattern))

        print(f"Found {len(result_files)} result files")

        for result_file in result_files:
            try:
                with open(result_file, "r") as f:
                    data = json.load(f)

                # Add metadata for multirun structure
                data["run_path"] = str(result_file.parent)
                data["run_number"] = result_file.parent.name  # 0, 1, 2, etc.
                data["run_timestamp"] = result_file.parent.parent.name  # HH-MM-SS
                data["run_date"] = result_file.parent.parent.parent.name  # YYYY-MM-DD

                # Try to load multirun.yaml for sweep parameters
                multirun_yaml = result_file.parent.parent / "multirun.yaml"
                if multirun_yaml.exists():
                    try:
                        import yaml

                        with open(multirun_yaml, "r") as f:
                            multirun_config = yaml.safe_load(f)
                            if (
                                "overrides" in multirun_config
                                and "task" in multirun_config["overrides"]
                            ):
                                data["sweep_overrides"] = multirun_config["overrides"][
                                    "task"
                                ]
                    except Exception:
                        pass  # If YAML loading fails, continue without sweep info

                self.runs_data.append(data)

            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not load {result_file}: {e}")

        print(f"Successfully loaded {len(self.runs_data)} runs")
        return len(self.runs_data)

    def create_comparison_dataframe(self) -> pl.DataFrame:
        """Create a Polars DataFrame for easy comparison of runs"""
        records = []

        for i, run in enumerate(self.runs_data):
            config = run["config"]

            # Base record with configuration
            base_record = {
                "run_id": i,
                "run_number": run.get("run_number", "unknown"),
                "run_timestamp": run["run_timestamp"],
                "run_date": run["run_date"],
                "sweep_info": str(run.get("sweep_overrides", [])),
                "target_amount": config["financial"]["target_amount"],
                "roi_rate": config["financial"]["roi_rate"],
                "retirement_age": config["financial"]["retirement_age"],
                "generation_gap": config["financial"]["generation_gap"],
                "currency": config["output"]["currency"],
                "single_child_investment": run["single_child_investment"],
                "base_converges": run["convergence_analysis"]["converges"],
                "base_convergence_ratio": run["convergence_analysis"][
                    "convergence_ratio"
                ],
                "base_infinite_sum": run["convergence_analysis"]["infinite_sum"],
            }

            # Add scenario results
            for children, result in run["scenario_results"].items():
                record = base_record.copy()
                record.update(
                    {
                        "children_per_generation": int(children),
                        "scenario_converges": result["converges"],
                        "scenario_cost": result["cost"],
                        "scenario_status": result["status"],
                    }
                )
                records.append(record)

        self.comparison_df = pl.DataFrame(records)
        return self.comparison_df

    def generate_comparison_plots(self, output_dir: Path) -> None:
        """Generate comprehensive comparison plots"""
        if self.comparison_df is None:
            self.create_comparison_dataframe()

        # Set up the plotting style
        plt.style.use("default")
        sns.set_palette("husl")

        # Create a large figure with multiple subplots
        plt.figure(figsize=(20, 16))

        # Plot 1: ROI vs Single Child Investment
        plt.subplot(3, 3, 1)
        df_single = self.comparison_df.filter(pl.col("children_per_generation") == 1)
        if df_single.height > 0:
            roi_data = df_single["roi_rate"].to_numpy() * 100
            investment_data = df_single["single_child_investment"].to_numpy()
            gap_data = df_single["generation_gap"].to_numpy()
            size_data = df_single["target_amount"].to_numpy() / 50000

            scatter = plt.scatter(
                roi_data,
                investment_data,
                c=gap_data,
                s=size_data,
                alpha=0.7,
                cmap="viridis",
            )
            plt.xlabel("ROI Rate (%)")
            plt.ylabel("Single Child Investment")
            plt.title("ROI vs Investment Required")
            plt.colorbar(scatter, label="Generation Gap (years)")

        # Plot 2: Generation Gap vs Convergence Ratio
        plt.subplot(3, 3, 2)
        df_base = self.comparison_df.filter(pl.col("children_per_generation") == 2)
        if df_base.height > 0:
            gap_data = df_base["generation_gap"].to_numpy()
            ratio_data = df_base["base_convergence_ratio"].to_numpy()
            converges_data = df_base["base_converges"].to_numpy()
            colors = ["red" if not conv else "green" for conv in converges_data]

            plt.scatter(gap_data, ratio_data, c=colors, alpha=0.7)
            plt.axhline(
                y=1, color="red", linestyle="--", alpha=0.5, label="Divergence Boundary"
            )
            plt.xlabel("Generation Gap (years)")
            plt.ylabel("Convergence Ratio")
            plt.title("Generation Gap vs Convergence (2 children)")
            plt.legend()

        # Plot 3: Children per Generation vs Cost (convergent cases only)
        plt.subplot(3, 3, 3)
        convergent_df = self.comparison_df.filter(
            (pl.col("scenario_converges")) & (pl.col("scenario_cost").is_not_null())
        )

        if convergent_df.height > 0:
            for run_id in convergent_df["run_id"].unique():
                run_data = convergent_df.filter(pl.col("run_id") == run_id)
                if run_data.height > 0:
                    roi = run_data["roi_rate"][0]
                    children_data = run_data["children_per_generation"].to_numpy()
                    cost_data = run_data["scenario_cost"].to_numpy()
                    plt.plot(
                        children_data,
                        cost_data,
                        "o-",
                        alpha=0.7,
                        label=f"ROI: {roi:.1%}",
                    )

            plt.xlabel("Children per Generation")
            plt.ylabel("Dynasty Cost")
            plt.title("Family Size vs Dynasty Cost (Convergent Cases)")
            plt.yscale("log")
            plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

        # Plot 4: Parameter Space Heatmap (Convergence)
        plt.subplot(3, 3, 4)
        df_heatmap = self.comparison_df.filter(pl.col("children_per_generation") == 2)
        if df_heatmap.height > 0:
            # Create a simple scatter plot instead of heatmap for now
            roi_data = df_heatmap["roi_rate"].to_numpy()
            gap_data = df_heatmap["generation_gap"].to_numpy()
            converges_data = df_heatmap["base_converges"].to_numpy()

            # Color by convergence
            colors = ["red" if not conv else "green" for conv in converges_data]
            plt.scatter(roi_data, gap_data, c=colors, alpha=0.7, s=50)
            plt.xlabel("ROI Rate")
            plt.ylabel("Generation Gap")
            plt.title("Parameter Space (2 children)")

            # Add legend
            import matplotlib.patches as mpatches

            red_patch = mpatches.Patch(color="red", label="Diverges")
            green_patch = mpatches.Patch(color="green", label="Converges")
            plt.legend(handles=[red_patch, green_patch])

        # Plot 5: Cost Distribution by Children Count
        plt.subplot(3, 3, 5)
        convergent_costs = convergent_df.filter(pl.col("scenario_cost").is_not_null())
        if convergent_costs.height > 0:
            children_counts = sorted(
                convergent_costs["children_per_generation"].unique()
            )
            cost_data = []
            for c in children_counts:
                subset = convergent_costs.filter(pl.col("children_per_generation") == c)
                if subset.height > 0:
                    cost_data.append(subset["scenario_cost"].to_numpy())

            if cost_data:
                plt.boxplot(cost_data, labels=children_counts)
                plt.xlabel("Children per Generation")
                plt.ylabel("Dynasty Cost (log scale)")
                plt.title("Cost Distribution by Family Size")
                plt.yscale("log")

        # Plot 6: ROI Sensitivity Analysis
        plt.subplot(3, 3, 6)
        roi_analysis = self.comparison_df.filter(
            pl.col("children_per_generation") == 1
        ).sort("roi_rate")
        if roi_analysis.height > 0:
            roi_data = roi_analysis["roi_rate"].to_numpy() * 100
            investment_data = roi_analysis["single_child_investment"].to_numpy()
            plt.plot(roi_data, investment_data, "o-")
            plt.xlabel("ROI Rate (%)")
            plt.ylabel("Single Child Investment")
            plt.title("ROI Sensitivity")
            plt.yscale("log")

        # Plot 7: Target Amount vs Investment Ratio
        plt.subplot(3, 3, 7)
        df_ratio = self.comparison_df.filter(pl.col("children_per_generation") == 1)
        if df_ratio.height > 0:
            target_data = df_ratio["target_amount"].to_numpy()
            investment_data = df_ratio["single_child_investment"].to_numpy()
            roi_data = df_ratio["roi_rate"].to_numpy()
            investment_ratio = investment_data / target_data

            scatter = plt.scatter(
                target_data, investment_ratio, c=roi_data, cmap="coolwarm", alpha=0.7
            )
            plt.xlabel("Target Amount")
            plt.ylabel("Investment Ratio (Investment/Target)")
            plt.title("Target vs Investment Efficiency")
            plt.colorbar(scatter, label="ROI Rate")

        # Plot 8: Time to Retirement vs Investment
        plt.subplot(3, 3, 8)
        retirement_analysis = self.comparison_df.filter(
            pl.col("children_per_generation") == 1
        )
        if retirement_analysis.height > 0:
            age_data = retirement_analysis["retirement_age"].to_numpy()
            investment_data = retirement_analysis["single_child_investment"].to_numpy()
            roi_data = retirement_analysis["roi_rate"].to_numpy()
            size_data = retirement_analysis["target_amount"].to_numpy() / 100000

            scatter = plt.scatter(
                age_data,
                investment_data,
                c=roi_data,
                s=size_data,
                alpha=0.7,
                cmap="plasma",
            )
            plt.xlabel("Retirement Age")
            plt.ylabel("Single Child Investment")
            plt.title("Retirement Age vs Investment")
            plt.colorbar(scatter, label="ROI Rate")

        # Plot 9: Convergence Boundary Analysis
        plt.subplot(3, 3, 9)
        if self.comparison_df.height > 0:
            # Plot actual data points
            convergent = self.comparison_df.filter(pl.col("scenario_converges"))
            divergent = self.comparison_df.filter(not pl.col("scenario_converges"))

            if convergent.height > 0:
                conv_roi = convergent["roi_rate"].to_numpy()
                conv_gap = convergent["generation_gap"].to_numpy()
                plt.scatter(
                    conv_roi, conv_gap, c="green", alpha=0.6, label="Convergent", s=20
                )

            if divergent.height > 0:
                div_roi = divergent["roi_rate"].to_numpy()
                div_gap = divergent["generation_gap"].to_numpy()
                plt.scatter(
                    div_roi, div_gap, c="red", alpha=0.6, label="Divergent", s=20
                )

            plt.xlabel("ROI Rate")
            plt.ylabel("Generation Gap")
            plt.title("Convergence Boundary Map")
            plt.legend()

        plt.tight_layout()

        # Save the plot
        plot_file = output_dir / "multirun_comparison.png"
        plt.savefig(plot_file, dpi=300, bbox_inches="tight")
        print(f"Comparison plots saved to {plot_file}")

        plt.show()

    def generate_summary_report(self, output_dir: Path) -> None:
        """Generate a comprehensive text summary report"""
        if self.comparison_df is None:
            self.create_comparison_dataframe()

        report_file = output_dir / "multirun_summary_report.txt"

        with open(report_file, "w") as f:
            f.write("Dynasty FIRE Multirun Analysis Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total runs analyzed: {len(self.runs_data)}\n\n")

            # Configuration Summary
            f.write("Configuration Summary\n")
            f.write("-" * 20 + "\n")
            f.write(
                f"ROI Rates: {self.comparison_df['roi_rate'].min():.1%} - {self.comparison_df['roi_rate'].max():.1%}\n"
            )
            f.write(
                f"Generation Gaps: {self.comparison_df['generation_gap'].min():.0f} - {self.comparison_df['generation_gap'].max():.0f} years\n"
            )
            f.write(
                f"Target Amounts: {self.comparison_df['target_amount'].min():,.0f} - {self.comparison_df['target_amount'].max():,.0f}\n"
            )
            f.write(
                f"Retirement Ages: {self.comparison_df['retirement_age'].min():.0f} - {self.comparison_df['retirement_age'].max():.0f} years\n\n"
            )

            # Convergence Analysis
            f.write("Convergence Analysis\n")
            f.write("-" * 20 + "\n")

            convergence_summary = (
                self.comparison_df.group_by("children_per_generation")
                .agg(
                    [
                        pl.count("scenario_converges").alias("count"),
                        pl.sum("scenario_converges").alias("sum"),
                        pl.mean("scenario_converges").alias("mean"),
                    ]
                )
                .sort("children_per_generation")
            )

            for row in convergence_summary.iter_rows(named=True):
                children = row["children_per_generation"]
                count = row["count"]
                sum_val = row["sum"]
                mean_val = row["mean"]
                f.write(
                    f"{children} children/generation: {sum_val}/{count} converge ({mean_val:.1%})\n"
                )
            f.write("\n")

            # Cost Analysis (Convergent Cases Only)
            convergent_df = self.comparison_df.filter(
                (pl.col("scenario_converges")) & (pl.col("scenario_cost").is_not_null())
            )

            if convergent_df.height > 0:
                f.write("Cost Analysis (Convergent Cases)\n")
                f.write("-" * 30 + "\n")

                cost_stats = (
                    convergent_df.group_by("children_per_generation")
                    .agg(
                        [
                            pl.count("scenario_cost").alias("count"),
                            pl.mean("scenario_cost").alias("mean"),
                            pl.median("scenario_cost").alias("median"),
                            pl.min("scenario_cost").alias("min"),
                            pl.max("scenario_cost").alias("max"),
                        ]
                    )
                    .sort("children_per_generation")
                )

                for row in cost_stats.iter_rows(named=True):
                    children = row["children_per_generation"]
                    f.write(f"{children} children/generation:\n")
                    f.write(f"  Count: {row['count']}\n")
                    f.write(f"  Mean: {row['mean']:,.0f}\n")
                    f.write(f"  Median: {row['median']:,.0f}\n")
                    f.write(f"  Range: {row['min']:,.0f} - {row['max']:,.0f}\n\n")

            # Parameter Sensitivity
            f.write("Parameter Sensitivity\n")
            f.write("-" * 20 + "\n")

            single_child_df = self.comparison_df.filter(
                pl.col("children_per_generation") == 1
            )
            if single_child_df.height > 0:
                # ROI sensitivity
                roi_corr = single_child_df.select(
                    [pl.corr("roi_rate", "single_child_investment").alias("roi_corr")]
                )["roi_corr"][0]
                f.write(f"ROI vs Single Child Investment correlation: {roi_corr:.3f}\n")

                # Generation gap sensitivity
                gap_corr = single_child_df.select(
                    [
                        pl.corr("generation_gap", "single_child_investment").alias(
                            "gap_corr"
                        )
                    ]
                )["gap_corr"][0]
                f.write(f"Generation Gap vs Investment correlation: {gap_corr:.3f}\n")

                # Target amount sensitivity
                target_corr = single_child_df.select(
                    [
                        pl.corr("target_amount", "single_child_investment").alias(
                            "target_corr"
                        )
                    ]
                )["target_corr"][0]
                f.write(
                    f"Target Amount vs Investment correlation: {target_corr:.3f}\n\n"
                )

            # Optimal Configurations
            f.write("Optimal Configurations\n")
            f.write("-" * 22 + "\n")

            # Lowest cost for each family size
            if convergent_df.height > 0:
                for children in sorted(
                    convergent_df["children_per_generation"].unique()
                ):
                    subset = convergent_df.filter(
                        pl.col("children_per_generation") == children
                    )
                    if subset.height > 0:
                        best_idx = subset["scenario_cost"].arg_min()
                        best = subset.row(best_idx, named=True)
                        f.write(
                            f"{children} children - Lowest cost: {best['scenario_cost']:,.0f}\n"
                        )
                        f.write(
                            f"  ROI: {best['roi_rate']:.1%}, Gap: {best['generation_gap']:.0f}y, "
                            f"Target: {best['target_amount']:,.0f}\n"
                        )

            f.write("\n")

            # Detailed Run Information
            f.write("Individual Run Details\n")
            f.write("-" * 25 + "\n")

            for i, run in enumerate(self.runs_data):
                config = run["config"]
                f.write(f"Run {i + 1}: {run['run_date']} {run['run_timestamp']}\n")
                f.write(f"  Config: ROI={config['financial']['roi_rate']:.1%}, ")
                f.write(f"Gap={config['financial']['generation_gap']}y, ")
                f.write(f"Target={config['financial']['target_amount']:,.0f}\n")
                f.write(f"  Single child: {run['single_child_investment']:,.0f}\n")
                f.write(
                    f"  Base convergence: {run['convergence_analysis']['converges']} "
                )
                f.write(
                    f"(ratio: {run['convergence_analysis']['convergence_ratio']:.4f})\n\n"
                )

        print(f"Summary report saved to {report_file}")

    def generate_csv_export(self, output_dir: Path) -> None:
        """Export comparison data to CSV for further analysis"""
        if self.comparison_df is None:
            self.create_comparison_dataframe()

        csv_file = output_dir / "multirun_data.csv"
        self.comparison_df.write_csv(csv_file)
        print(f"Data exported to {csv_file}")


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Analyze Dynasty FIRE multirun results"
    )
    parser.add_argument(
        "--outputs-dir",
        default="multirun",
        help="Directory containing Hydra multirun outputs (default: multirun)",
    )
    parser.add_argument(
        "--output-dir",
        default="multirun_analysis",
        help="Directory to save analysis results (default: multirun_analysis)",
    )
    parser.add_argument(
        "--pattern",
        default="**/*/dynasty_results.json",
        help="File pattern to search for results (default: **/*/dynasty_results.json)",
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Initialize analyzer
    analyzer = MultirunAnalyzer(args.outputs_dir)

    # Load runs
    num_runs = analyzer.load_runs(args.pattern)
    if num_runs == 0:
        print("No runs found! Make sure you have run dynasty_fire.py multiple times.")
        return

    # Generate analysis
    print("Creating comparison dataframe...")
    analyzer.create_comparison_dataframe()

    print("Generating comparison plots...")
    analyzer.generate_comparison_plots(output_dir)

    print("Generating summary report...")
    analyzer.generate_summary_report(output_dir)

    print("Exporting data to CSV...")
    analyzer.generate_csv_export(output_dir)

    print(f"\nAnalysis complete! Results saved to {output_dir}")


if __name__ == "__main__":
    main()
