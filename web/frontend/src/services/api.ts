import type {
  CalculatorParams,
  CalculatorResult,
  HeatmapParams,
  HeatmapData,
} from '../types/calculator';

const API_BASE = '/api/v1';

export async function calculateDynasty(
  params: CalculatorParams
): Promise<CalculatorResult> {
  const response = await fetch(`${API_BASE}/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Calculation failed');
  }

  return response.json();
}

export async function fetchHeatmapData(
  params: HeatmapParams
): Promise<HeatmapData> {
  const response = await fetch(`${API_BASE}/heatmap`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Heatmap generation failed');
  }

  return response.json();
}
