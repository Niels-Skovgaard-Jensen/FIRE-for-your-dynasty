import { useState } from 'react';
import { useCalculator } from '../hooks/useCalculator';
import { ParameterSliders } from './ParameterSliders';
import { ResultsDisplay } from './ResultsDisplay';
import { ConvergenceHeatmap } from './ConvergenceHeatmap';
import { GenerationsTable } from './GenerationsTable';

export function CalculatorPage() {
  const [currency, setCurrency] = useState('USD');
  const {
    params,
    result,
    heatmapData,
    loading,
    error,
    updateParam,
    setParamsFromHeatmapClick,
  } = useCalculator();

  return (
    <div className="calculator-page">
      <aside className="sidebar">
        <ParameterSliders
          params={params}
          currency={currency}
          onParamChange={updateParam}
          onCurrencyChange={setCurrency}
        />
      </aside>

      <section className="content">
        <details className="calculator-description">
          <summary>How to use this calculator</summary>
          <div className="description-content">
            <p>
              Calculate how much you need to invest today to fund retirement for your descendants.
              Adjust the parameters to see if an "infinite dynasty" is mathematically achievable
              given your investment returns and family size.
            </p>
            <h4>Parameters</h4>
            <ul>
              <li><strong>Target Amount:</strong> The amount each descendant needs at retirement age for financial independence.</li>
              <li><strong>ROI Rate:</strong> Expected annual return on investment (after inflation). Historically, global stock markets have averaged ~7%.</li>
              <li><strong>Retirement Age:</strong> The age at which descendants will access their retirement funds.</li>
              <li><strong>Generation Gap:</strong> Average years between generations (parent's age when child is born).</li>
              <li><strong>Children per Generation:</strong> Average number of children per person. This determines how fast the family tree grows.</li>
            </ul>
            <h4>Understanding the Results</h4>
            <p>
              The heatmap shows which combinations of ROI and children per generation lead to convergence (green) or divergence (red).
              When the series converges, there exists a finite amount that can fund infinite generations.
              Click anywhere on the heatmap to update the parameters.
            </p>
          </div>
        </details>

        <div className="top-row">
          <div className="visualization">
            <ConvergenceHeatmap
              data={heatmapData}
              currentRoi={params.roi_rate}
              currentChildren={params.children_per_generation}
              onPointClick={setParamsFromHeatmapClick}
              loading={loading}
            />
          </div>

          <div className="generations-panel">
            <GenerationsTable
              convergence={result?.convergence ?? null}
              currency={currency}
              childrenPerGeneration={params.children_per_generation}
            />
          </div>
        </div>

        <div className="results-section">
          <ResultsDisplay
            result={result}
            loading={loading}
            error={error}
            currency={currency}
          />
        </div>
      </section>
    </div>
  );
}
