import Plot from 'react-plotly.js';
import type { HeatmapData } from '../types/calculator';

interface Props {
  data: HeatmapData | null;
  currentRoi: number;
  currentChildren: number;
  onPointClick: (roi: number, children: number) => void;
  loading: boolean;
}

export function ConvergenceHeatmap({
  data,
  currentRoi,
  currentChildren,
  onPointClick,
  loading,
}: Props) {
  if (!data) {
    return (
      <div className="heatmap-container">
        <div className="heatmap-placeholder">
          {loading ? 'Loading heatmap...' : 'No data available'}
        </div>
      </div>
    );
  }

  // Convert ROI to percentage for display
  const roiPercent = data.roi_values.map((r) => r * 100);
  const currentRoiPercent = currentRoi * 100;

  return (
    <div className="heatmap-container">
      <h2>Convergence Heatmap</h2>
      <Plot
        data={[
          // Main heatmap
          {
            type: 'heatmap',
            x: roiPercent,
            y: data.children_values,
            z: data.convergence_matrix,
            colorscale: [
              [0, '#ef4444'],
              [1, '#22c55e'],
            ],
            showscale: false,
            hovertemplate:
              'ROI: %{x:.1f}%<br>Children: %{y:.1f}<br>Converges: %{z}<extra></extra>',
          },
          // Contour line at convergence boundary
          {
            type: 'contour',
            x: roiPercent,
            y: data.children_values,
            z: data.convergence_ratios,
            contours: {
              start: 1,
              end: 1,
              size: 0.01,
              coloring: 'lines',
            },
            line: { color: 'black', width: 3 },
            showscale: false,
            hoverinfo: 'skip',
          },
          // Current config marker
          {
            type: 'scatter',
            x: [currentRoiPercent],
            y: [currentChildren],
            mode: 'markers',
            marker: {
              size: 16,
              color: 'white',
              symbol: 'circle',
              line: { width: 3, color: '#1e293b' },
            },
            name: 'Current',
            hovertemplate: `Current Config<br>ROI: ${currentRoiPercent.toFixed(1)}%<br>Children: ${currentChildren.toFixed(1)}<extra></extra>`,
          },
        ]}
        layout={{
          title: {
            text: 'Click anywhere to update parameters',
            font: { size: 12, color: '#64748b' },
          },
          xaxis: {
            title: 'ROI Rate (%)',
            gridcolor: '#e2e8f0',
          },
          yaxis: {
            title: 'Children per Generation',
            gridcolor: '#e2e8f0',
          },
          width: 600,
          height: 500,
          margin: { l: 60, r: 40, t: 40, b: 60 },
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: 'rgba(0,0,0,0)',
          font: { family: 'system-ui, sans-serif' },
        }}
        config={{
          displayModeBar: false,
          responsive: true,
        }}
        onClick={(event) => {
          if (event.points && event.points.length > 0) {
            const point = event.points[0];
            if (point.x !== undefined && point.y !== undefined) {
              // Convert back from percentage
              const roi = (point.x as number) / 100;
              const children = point.y as number;
              onPointClick(roi, children);
            }
          }
        }}
      />
      <p className="heatmap-legend">
        <span className="legend-item converges">Green = Converges (finite cost)</span>
        <span className="legend-item diverges">Red = Diverges (infinite cost)</span>
      </p>
    </div>
  );
}
