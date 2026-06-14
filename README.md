# Generational FIRE

An interactive web app for analyzing compound interest across generations.
Calculate how much you need to invest today to fund retirement for your
descendants — and whether an "infinite dynasty" is mathematically achievable.

The app is **fully client-side**: all calculations run in the browser, and it
deploys as a static site to GitHub Pages.

## Quick Start

```bash
cd web/frontend
npm install
npm run dev
```

Open http://localhost:5173

## The Math

Funding infinite generations is a geometric series. It converges when:

```
k / (1 + R)^Yc < 1
```

Where:
- `k` = children per generation
- `R` = annual return on investment (after inflation)
- `Yc` = years between generations

When this condition holds, a finite investment today can fund retirement for
all future descendants. The full derivation lives on the app's Introduction
page (`web/frontend/public/introduction.md`).

## Project Structure

```
web/frontend/              # React + TypeScript + Vite app (fully client-side)
├── src/
│   ├── components/        # Calculator UI, convergence heatmap, intro page
│   ├── services/
│   │   └── calculator.ts  # Dynasty FIRE math, in the browser
│   ├── hooks/
│   └── types/
└── public/
    └── introduction.md    # Blog / mathematical explanation
```

## Build

```bash
cd web/frontend
npm run build              # type-checks (tsc) and bundles to dist/
npm run preview            # preview the production build locally
```

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds the
frontend and publishes `web/frontend/dist` to GitHub Pages. Pull requests run
`.github/workflows/ci.yml`, which type-checks and builds the frontend.

## License

MIT
