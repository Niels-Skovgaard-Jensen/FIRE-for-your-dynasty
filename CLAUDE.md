# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

Generational FIRE is an interactive web app for generational wealth planning. It
calculates how much money needs to be invested today to fund retirement for
multiple generations of descendants, and whether an "infinite dynasty" is
mathematically achievable given investment returns and family size.

The app is **fully client-side** — all calculations run in the browser
(TypeScript) and it deploys as a static site to GitHub Pages. There is no
backend.

## Commands

```bash
# Develop (from the frontend directory)
cd web/frontend
npm install
npm run dev        # dev server on http://localhost:5173

# Build for production (runs tsc type-check, then vite build → dist/)
npm run build

# Preview a production build
npm run preview
```

## Architecture

All application code lives in `web/frontend/` (React + TypeScript + Vite).

- **src/services/calculator.ts** — the math engine, in the browser:
  - Single child investment: `B = M / (1 + R)^Y`
  - Dynasty investment across generations with exponential family growth
  - Convergence analysis: the series converges when `k / (1+R)^Yc < 1`
    (k = children, R = ROI, Yc = generation gap)
- **src/hooks/useCalculator.ts** — calculation state for the UI
- **src/components/** — UI components:
  - `CalculatorPage.tsx`, `ParameterSliders.tsx`, `ResultsDisplay.tsx`,
    `GenerationsTable.tsx` — interactive calculator
  - `ConvergenceHeatmap.tsx` — Plotly convergence heatmap (click to update params)
  - `IntroductionPage.tsx` — renders `public/introduction.md` (Markdown + KaTeX)
- **src/types/calculator.ts** — shared TypeScript types
- **public/introduction.md** — the blog / mathematical explanation

## Key Mathematical Concepts

The convergence condition `k / (1+R)^Yc < 1` determines whether funding infinite
generations is possible:
- Converges: finite total cost, "infinite dynasty" achievable
- Diverges: costs grow without bound, only finite generations fundable

## CI/CD

- `.github/workflows/deploy.yml` — on push to `main`, builds the frontend and
  publishes `web/frontend/dist` to GitHub Pages.
- `.github/workflows/ci.yml` — on pull requests, type-checks and builds the
  frontend.
