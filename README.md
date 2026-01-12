# Generational FIRE

A web application and Python library for analyzing compound interest across generations. Calculate how much you need to invest today to fund retirement for your descendants - and whether an "infinite dynasty" is mathematically achievable.

## Quick Start

### Web App (Recommended)

```bash
cd web/frontend
npm install
npm run dev
```

Open http://localhost:5173

### Python CLI

```bash
# Run analysis with default parameters
uv run python dynasty_fire_main.py

# Override parameters
uv run python dynasty_fire_main.py financial.roi_rate=0.08 financial.target_amount=5000000
```

## The Math

The key insight is that funding infinite generations is a geometric series. It converges when:

```
k / (1 + R)^Yc < 1
```

Where:
- `k` = children per generation
- `R` = annual return on investment (after inflation)
- `Yc` = years between generations

When this condition is met, a finite investment today can fund retirement for all future descendants.

## Project Structure

```
├── web/frontend/          # React + TypeScript web app (fully client-side)
├── dynasty_fire/          # Python calculator library
│   ├── calculator.py      # Core DynastyFIRE class
│   ├── config.py          # Configuration dataclasses
│   ├── visualizer.py      # Matplotlib plots
│   └── utils.py           # Formatting utilities
├── dynasty_fire_main.py   # Hydra CLI entry point
├── tests/                 # Pytest test suite
└── Introduction.md        # Detailed mathematical explanation
```

## Development

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint
uv run ruff check .
```

## License

MIT
