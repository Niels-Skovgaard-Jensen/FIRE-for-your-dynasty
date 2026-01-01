# Dynasty FIRE Web Application

An interactive web application for exploring generational wealth planning with compound interest.

## Features

- **Real-time sliders** for adjusting parameters (target amount, ROI, retirement age, generation gap, children)
- **Interactive heatmap** showing convergence regions - click anywhere to update parameters
- **Key metrics display** showing single child investment, convergence status, and infinite dynasty cost

## Quick Start

### Development Mode

1. **Start the Flask backend** (terminal 1):
   ```bash
   cd /Users/niels/Git/FIRE-for-your-dynasty
   FLASK_APP=web.backend.app:app uv run flask run --port 5001
   ```
   Backend runs at http://localhost:5001

2. **Start the React frontend** (terminal 2):
   ```bash
   cd /Users/niels/Git/FIRE-for-your-dynasty/web/frontend
   npm run dev
   ```
   Frontend runs at http://localhost:5173

3. Open http://localhost:5173 in your browser

### Production Build

```bash
# Build the React frontend
cd web/frontend
npm run build

# Run Flask (serves both API and static files)
cd /Users/niels/Git/FIRE-for-your-dynasty
uv run python -m web.backend.app
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/calculate` | POST | Main calculation endpoint |
| `/api/v1/heatmap` | POST | Generate heatmap data |
| `/api/v1/health` | GET | Health check |

### Example API Request

```bash
curl -X POST http://localhost:5001/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{"target_amount": 10000000, "roi_rate": 0.07, "children_per_generation": 2}'
```

## Tech Stack

- **Backend**: Flask + Python (wraps existing DynastyFIRE calculator)
- **Frontend**: React + TypeScript + Vite
- **Charts**: Plotly.js for interactive heatmap visualization
