# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dynasty FIRE is a compound interest analysis tool for generational wealth planning. It calculates how much money needs to be invested today to fund retirement for multiple generations of descendants, analyzing whether an "infinite dynasty" is mathematically achievable given investment returns and family size.

## Commands

```bash
# Run the main analysis (uses Hydra for config)
uv run python dynasty_fire_main.py

# Override config parameters via CLI
uv run python dynasty_fire_main.py financial.roi_rate=0.08 financial.target_amount=5000000

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_calculator.py::TestDynastyFIRE::test_single_child_investment_calculation

# Run tests by marker
uv run pytest -m "not slow"

# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

## Architecture

### Core Module: `dynasty_fire/`

- **calculator.py** - `DynastyFIRE` class containing the mathematical engine:
  - Single child investment: `B = M / (1 + R)^Y`
  - Dynasty investment across generations with exponential family growth
  - Convergence analysis: series converges when `k / (1+R)^Y_c < 1` (k=children, R=ROI, Y_c=generation gap)
  - Key parameters: `M` (target amount), `R` (ROI rate), `Y` (retirement age), `Y_c` (generation gap)

- **config.py** - Dataclass-based configuration (integrates with Hydra's ConfigStore)

- **visualizer.py** - `DynastyVisualizer` class for matplotlib plots (heatmaps, sensitivity analysis, dynasty growth)

- **utils.py** - Formatting, JSON/report output, config validation

### Entry Points

- **dynasty_fire_main.py** - Hydra-wrapped main function (`@hydra.main`). No YAML configs - uses structured configs from `config.py`
- **dynasty_fire.py** - Legacy standalone analysis script

### Configuration System

Uses Hydra with structured configs (no YAML files). Override parameters via CLI:
```bash
uv run python dynasty_fire_main.py financial.roi_rate=0.10 analysis.max_generations=30
```

Output goes to `outputs/YYYY-MM-DD/HH-MM-SS/` (Hydra default) containing:
- `dynasty_results.json` - Raw analysis data
- `summary_report.txt` - Human-readable summary
- `*.png` - Visualization plots

### Testing

Tests use pytest fixtures defined in `tests/conftest.py`:
- `default_config` / `custom_config` - OmegaConf configuration objects
- `dynasty_calculator` - Pre-configured `DynastyFIRE` instance
- Coverage requirement: 80% minimum

## Key Mathematical Concepts

The convergence condition `k / (1+R)^Y_c < 1` determines if funding infinite generations is possible:
- Converges: finite total cost, "infinite dynasty" achievable
- Diverges: costs grow without bound, only finite generations fundable
