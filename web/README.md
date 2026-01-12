# Generational FIRE Web App

An interactive web application for exploring generational wealth planning with compound interest.

## Features

- **Real-time sliders** for adjusting parameters (target amount, ROI, retirement age, generation gap, children)
- **Interactive heatmap** showing convergence regions - click anywhere to update parameters
- **Generations table** showing investment breakdown per generation
- **Key metrics** showing single child investment, convergence status, and infinite dynasty cost
- **Mobile responsive** design

## Quick Start

```bash
cd web/frontend
npm install
npm run dev
```

Open http://localhost:5173

## Architecture

The frontend is **fully client-side** - all calculations run in the browser using TypeScript. No backend server is required.

```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── IntroductionPage.tsx
│   │   ├── CalculatorPage.tsx
│   │   ├── ConvergenceHeatmap.tsx
│   │   ├── GenerationsTable.tsx
│   │   ├── ParameterSliders.tsx
│   │   └── ResultsDisplay.tsx
│   ├── services/
│   │   └── calculator.ts  # TypeScript calculator (client-side)
│   ├── hooks/
│   │   └── useCalculator.ts
│   └── types/
│       └── calculator.ts
├── public/
│   └── introduction.md    # Editable introduction content
└── package.json
```

## Deployment

### GitHub Pages

The app is configured for GitHub Pages deployment. Push to `main` and the GitHub Action will build and deploy automatically.

### Manual Build

```bash
npm run build
# Output in dist/ - serve with any static file server
```

## Tech Stack

- **React 18** + TypeScript
- **Vite** for bundling
- **Plotly.js** for interactive heatmap
- **KaTeX** for math formula rendering
- **react-markdown** for introduction content
